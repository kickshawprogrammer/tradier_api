"""
Module containing API streamer classes for the Tradier API.

This module provides classes and functions for streaming data from the Tradier API, 
including both HTTP and WebSocket streaming capabilities. It defines the necessary 
streamers to facilitate real-time market and account event data retrieval, handling 
the underlying connection, data processing, and event management.

Classes:
    - `TradierHttpStreamer`: Handles HTTP streaming requests to fetch real-time market data.
    - `TradierWebsocketStreamer`: Manages WebSocket connections for streaming data, supporting 
                                  asynchronous event-driven communication.
    - `TradierMarketsStreamer`: Extends `TradierWebsocketStreamer` to specifically stream market events.
    - `TradierAccountStreamer`: Extends `TradierWebsocketStreamer` to specifically stream account-related events.

Dependencies:
    - `requests`: For HTTP requests and response handling.
    - `asyncio` and `websockets`: For asynchronous WebSocket connections.
    - `json`: To parse and construct JSON data.
    - `threading`: To manage concurrent execution of streaming tasks.

Usage:
This module is typically used within the context of a larger application that interacts 
with the Tradier API. It requires proper configuration through `TradierConfig` and 
appropriate parameters (`SymbolsParams`, `ExcludedAccountParams`) to specify the data to stream.

Logging:
Uses the `logging` module to provide detailed logs for debugging and operational insights. 
Ensure to configure the logger appropriately in the main application to capture these logs.

"""
import requests
import asyncio
import websockets
import json

from typing import Optional, Union, List, cast
from threading import Thread, Event

from ._core_types import BaseURL
from .tradier_types import TradierAPIException, Endpoints
from .tradier_params import BaseParams, SymbolsParams, ExcludedAccountParams
from .tradier_config import TradierConfig

import logging
logger = logging.getLogger(__name__)

class TradierBaseStreamer:
    """
    Base class for streamers that interact with the Tradier API.

    This class provides common functionality for both HTTP and WebSocket streaming. 
    It manages the underlying connection, data processing, and event management. 
    Subclasses should implement the specific logic for setting up the connection 
    and processing the data received from the API.

    Attributes:
        config (TradierConfig): The configuration for the API controller, including
            the access token and environment settings.
        on_open (Optional[Callable[[None], None]]): Called when the connection is opened.
        on_message (Optional[Callable[[str], None]]): Called when a message is received from the API.
        on_close (Optional[Callable[[None], None]]): Called when the connection is closed.
        on_error (Optional[Callable[[Exception], None]]): Called when an error occurs.

    Methods:
        _handle_event (Optional[Callable[[str], None]], str, *args): Handles an event with the given callback, 
            defaulting to a message if callback is None.

    """
    def __init__(self, config: TradierConfig, on_open=None, on_message=None, on_close=None, on_error=None):
        """Initializes the stream with configuration and event callbacks."""
        self.config = config    # we need this for the headers

        self.on_open = on_open
        self.on_message = on_message
        self.on_close = on_close
        self.on_error = on_error
   
    def _handle_event(self, callback, default_message, *args):
        """Handles event with given callback, defaulting to a message if callback is None."""
        if callback:
            callback(*args)
        else:
            logger.debug(default_message, *args)

    def _do_on_open(self):
        """Triggers the on_open event."""
        self._handle_event(self.on_open, "Stream opened.")

    def _do_on_message(self, message):
        """Triggers the on_message event with message content."""
        self._handle_event(self.on_message, "Received message:", message)

    def _do_on_close(self):
        """Triggers the on_close event."""
        self._handle_event(self.on_close, "Stream closed.")

    def _do_on_error(self, error):
        """Triggers the on_error event with error details."""
        self._handle_event(self.on_error, "Stream error:", error)

    def run(self, session_key, stop_event, params: BaseParams):
        """Runs the stream logic in a separate thread."""
        raise NotImplementedError
    
    def get_session_endpoint(self) -> Endpoints:
        """Returns the appropriate session endpoint for the streamer."""
        raise NotImplementedError

class TradierHttpStreamer(TradierBaseStreamer):
    """
    A streamer for the HTTP streaming endpoint.

    The `TradierHttpStreamer` will open a connection to the HTTP streaming endpoint
    and stream data for the specified parameters. It extends the
    `TradierBaseStreamer` with additional functionality for HTTP streaming.

    Attributes:
        config (TradierConfig): The configuration for the streamer, including
            the access token and environment settings.

    Methods:
        run(session_key: str, stop_event: Event, params: BaseParams):
            Runs the stream logic in a separate thread, using the given
            session key and parameters. The `stop_event` is used to signal the
            stream to stop.
    """
    def _build_stream_url(self, endpoint: str):
        """
        Builds the URL based on the base URL and endpoint.
        """
        return f"{BaseURL.STREAM.value}{endpoint}"
    
    def get_session_endpoint(self) -> Endpoints:
        """Returns the appropriate session endpoint for the streamer."""
        return Endpoints.CREATE_MARKET_SESSION

    def run(self, session_key: str, stop_event: Event, params: BaseParams):
        """Executes the streaming logic using provided parameters."""
        if not isinstance(params, SymbolsParams):
            raise ValueError("Invalid parameters for TradierHttpStreamer. Expected SymbolsParams.")

        try:
            self._do_on_open()

            url = self._build_stream_url(Endpoints.GET_STREAMING_QUOTES.path)
            query_params = params.to_query_params()
            query_params["sessionid"] = session_key  # Add session ID as a query parameter
            query_params["linebreak"] = True

            response = requests.post(url, headers=self.config.headers, params=query_params, stream=True)
            response.raise_for_status()

            for chunk in response.iter_lines():
                if stop_event.is_set():
                    break
                if chunk:
                    try:
                        self._do_on_message(chunk.decode('utf-8'))
                    except Exception as e:
                        self._do_on_error(e)

        except (TradierAPIException, requests.exceptions.RequestException) as e:
            self._do_on_error(e)

        finally:
            self._do_on_close()

class TradierWebsocketStreamer(TradierBaseStreamer):
    """
    A streamer for the WebSocket endpoint.

    The `TradierWebsocketStreamer` will open a WebSocket connection to the
    specified endpoint and stream data for the specified parameters. It extends
    the `TradierBaseStreamer` with additional functionality for WebSocket
    streaming.

    Attributes:
        config (TradierConfig): The configuration for the streamer, including
            the access token and environment settings.
        _loop (Optional[asyncio.AbstractEventLoop]): The event loop used to
            run the stream logic.
        _task (Optional[asyncio.Task]): The task that runs the stream logic.
        _endpoint (Optional[Endpoints]): The endpoint for the WebSocket
            connection.

    Methods:
        run(session_key: str, stop_event: Event, params: BaseParams):
            Runs the stream logic in a separate thread, using the given
            session key and parameters. The `stop_event` is used to signal the
            stream to stop.

    """
    def __init__(self, config, on_open=None, on_message=None, on_close=None, on_error=None):
        super().__init__(config, on_open, on_message, on_close, on_error)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._task: Optional[asyncio.Task] = None
        self._endpoint: Optional[Endpoints] = None

    def _build_stream_url(self, endpoint: str):
        """Builds the WebSocket URL based on the endpoint."""
        return f"{BaseURL.WEBSOCKET.value}{endpoint}"
    
    async def _run_stream(self, session_key: str, stop_event: Event, params: BaseParams):
        """Handle the WebSocket connection and data stream."""

        # Convert parameters into query payload
        payload_dict = params.to_query_params()  # Convert parameters to a dictionary
        payload_dict["sessionid"] = session_key  # Add session ID
        payload_dict["linebreak"] = True  # Include line breaks in the data
        payload = json.dumps(payload_dict)  # Convert the updated dictionary to a JSON string

        if self._endpoint is None:
            raise ValueError("Endpoint is not set.")
        
        url = self._build_stream_url(self._endpoint.path)

        try:
            websocket = await websockets.connect(url, ssl=True, compression=None)
            await websocket.send(payload)
            self._do_on_open()

            while not stop_event.is_set():
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    self._do_on_message(message)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self._do_on_error(e)
                    break

            await websocket.close()

        except Exception as e:
            self._do_on_error(e)

        finally:
            self._do_on_close()
    def run(self, session_key: str, stop_event: Event,  params: BaseParams):
        """Run the WebSocket connection in the asyncio loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._task = self._loop.create_task(self._run_stream(session_key, stop_event, params))

        try:
            self._loop.run_until_complete(self._task)
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

class TradierMarketsStreamer(TradierWebsocketStreamer):
    """
    A streamer for the WebSocket market events endpoint.

    The `TradierMarketsStreamer` establishes a WebSocket connection to stream
    real-time market events using the Tradier API. It extends the `TradierWebsocketStreamer`
    with specific functionality for market event streaming.

    Attributes:
        config (TradierConfig): The configuration for the streamer, including
            the access token and environment settings.

    Methods:
        run(session_key: str, stop_event: Event, params: BaseParams):
            Initiates the WebSocket connection to stream market events.
    """
    def __init__(self, config, on_open=None, on_message=None, on_close=None, on_error=None):
        super().__init__(config, on_open, on_message, on_close, on_error)
        self._endpoint = Endpoints.GET_STREAMING_MARKET_EVENTS


    def get_session_endpoint(self) -> Endpoints:
        """Returns the appropriate session endpoint for the streamer."""
        return Endpoints.CREATE_MARKET_SESSION

    def run(self, session_key: str, stop_event: Event, params: BaseParams):
        """Run the WebSocket connection for market events."""
        if not isinstance(params, SymbolsParams):
            raise ValueError("Invalid parameters for TradierMarketsStreamer. Expected SymbolsParams.")

        # Call the WebSocket implementation
        super().run(session_key, stop_event, params)

class TradierAccountStreamer(TradierWebsocketStreamer):
    """
    A streamer for the WebSocket account events endpoint.

    The `TradierAccountStreamer` establishes a WebSocket connection to stream
    real-time account events using the Tradier API. It extends the `TradierWebsocketStreamer`
    with specific functionality for account event streaming.

    Attributes:
        config (TradierConfig): The configuration for the streamer, including
            the access token and environment settings.

    Methods:
        run(session_key: str, stop_event: Event, params: BaseParams):
            Initiates the WebSocket connection to stream account events.
    """
    def __init__(self, config, on_open=None, on_message=None, on_close=None, on_error=None):
        super().__init__(config, on_open, on_message, on_close, on_error)
        self._endpoint = Endpoints.GET_STREAMING_ACCOUNT_EVENTS

    def get_session_endpoint(self) -> Endpoints:
        """Returns the appropriate session endpoint for the streamer."""
        return Endpoints.CREATE_ACCOUNT_SESSION

    def run(self, session_key: str, stop_event: Event, params: BaseParams):
        """Run the WebSocket connection for account events."""
        if not isinstance(params, ExcludedAccountParams):
            raise ValueError("Invalid parameters for TradierAccountStreamer. Expected AccountParams.")

        # Call the WebSocket implementation
        super().run(session_key, stop_event, params)
