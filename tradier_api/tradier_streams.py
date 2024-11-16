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
    """HTTP streamer class for handling HTTP streaming requests."""
    def _build_stream_url(self, endpoint: str):
        """
        Builds the URL based on the base URL and endpoint.
        """
        return f"{BaseURL.STREAM.value}{endpoint}"
    
    def get_session_endpoint(self) -> Endpoints:
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
    def __init__(self, config, on_open=None, on_message=None, on_close=None, on_error=None):
        super().__init__(config, on_open, on_message, on_close, on_error)
        self._endpoint = Endpoints.GET_STREAMING_MARKET_EVENTS


    def get_session_endpoint(self) -> Endpoints:
        return Endpoints.CREATE_MARKET_SESSION

    def run(self, session_key: str, stop_event: Event, params: BaseParams):
        """Run the WebSocket connection for market events."""
        if not isinstance(params, SymbolsParams):
            raise ValueError("Invalid parameters for TradierMarketsStreamer. Expected SymbolsParams.")

        # Call the WebSocket implementation
        super().run(session_key, stop_event, params)

class TradierAccountStreamer(TradierWebsocketStreamer):
    def __init__(self, config, on_open=None, on_message=None, on_close=None, on_error=None):
        super().__init__(config, on_open, on_message, on_close, on_error)
        self._endpoint = Endpoints.GET_STREAMING_ACCOUNT_EVENTS


    def get_session_endpoint(self) -> Endpoints:
        return Endpoints.CREATE_ACCOUNT_SESSION

    def run(self, session_key: str, stop_event: Event, params: BaseParams):
        """Run the WebSocket connection for account events."""
        if not isinstance(params, ExcludedAccountParams):
            raise ValueError("Invalid parameters for TradierAccountStreamer. Expected AccountParams.")

        # Call the WebSocket implementation
        super().run(session_key, stop_event, params)