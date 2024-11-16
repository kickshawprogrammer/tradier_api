import requests
import asyncio
import websockets
import json

from typing import Optional, Union, List
from threading import Thread, Event

from ._core_types import BaseURL
from .tradier_types import TradierAPIException, Endpoints
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

    def run(self, session_key, stop_event, symbols):
        """Runs the stream logic in a separate thread."""
        raise NotImplementedError


class TradierHttpStreamer(TradierBaseStreamer):
    """HTTP streamer class for handling HTTP streaming requests."""
    def _build_stream_url(self, endpoint: str):
        """
        Builds the URL based on the base URL and endpoint.
        """
        return f"{BaseURL.STREAM.value}{endpoint}"

    def run(self, session_key, stop_event, symbols):
        """Executes the streaming logic in a separate thread."""
        try:
            self._do_on_open()

            # Build URL and set up parameters for streaming
            url = self._build_stream_url(Endpoints.GET_STREAMING_QUOTES.path)
            params = {"symbols": ",".join(symbols), "sessionid": session_key, "linebreak":True}
    
            # Initiate streaming with requests.post, using stream=True for continuous data
            response = requests.post(url, headers=self.config.headers, params=params, stream=True)
            response.raise_for_status()

            # Process each incoming chunk of data
            for chunk in response.iter_lines():
                if stop_event.is_set():
                    break
                if chunk:
                    try:
                        self._do_on_message(chunk.decode('utf-8'))
                    except Exception as e: 
                        self._do_on_error(e)  # Handle streaming-specific errors

        except (TradierAPIException, requests.exceptions.RequestException) as e:
            self._do_on_error(e)  # Handle setup errors
        
        finally:
            self._do_on_close()

class TradierWebsocketStreamer(TradierBaseStreamer):
    def __init__(self, config, on_open=None, on_message=None, on_close=None, on_error=None):
        super().__init__(config, on_open, on_message, on_close, on_error)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._task: Optional[asyncio.Task] = None

    def _build_stream_url(self, endpoint: str):
        """Builds the WebSocket URL based on the endpoint."""
        return f"{BaseURL.WEBSOCKET.value}{endpoint}"
    
    async def _run_stream(self, session_key: str, stop_event: Event, symbols: Union[str, List[str]]):
        # Convert symbols list to comma-separated string if needed
        # if isinstance(symbols, list):
        #     symbols = ",".join(symbols)
        if isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(",")]

        # WebSocket URL
        url = self._build_stream_url(Endpoints.GET_STREAMING_MARKET_EVENTS.path)

        # Correctly format the payload
        payload = json.dumps({
            "symbols": symbols,
            "sessionid": session_key,
            "linebreak": True
        })
        
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

    def run(self, session_key: str, stop_event: Event, symbols: Union[str, List[str]]):
        """Run the WebSocket connection in the asyncio loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._task = self._loop.create_task(self._run_stream(session_key, stop_event, symbols))

        try:
            self._loop.run_until_complete(self._task)
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()
