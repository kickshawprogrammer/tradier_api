import requests

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

