import time
import requests
import threading

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ._core_types import BaseURL
from .tradier_types import TradierAPIException, Endpoints
from .tradier_params import BaseParams
from .tradier_config import TradierConfig
from .tradier_streams import TradierBaseStreamer

import logging
logger = logging.getLogger(__name__)

class TradierBaseController:
    def __init__(self, config: TradierConfig):
        self.config = config
        self.base_url = self._get_base_url(config.environment.value)
        self.headers = config.headers

    def _get_base_url(self, environment: str) -> str:
        environment = environment.lower()
        if environment == "live":
            return BaseURL.API.value
        elif environment == "sandbox" or environment == "paper":
            return BaseURL.SANDBOX.value
        else:
            raise ValueError(f"Invalid environment: {environment}")
        
    def _build_url(self, endpoint: str):
        """
        Builds the URL based on the base URL and endpoint.
        """
        return f"{self.base_url}{endpoint}"
    
class TradierApiController(TradierBaseController):

    class ThrottleHandler:
        @staticmethod
        def handle_throttling(response):
            expiry = int(response.headers.get('X-Ratelimit-Expiry', str(int(time.time()) + 60)))  # Default to 60 seconds in future
            available = int(response.headers.get('X-Ratelimit-Available', '0'))  # Default to 0
            allowed = int(response.headers.get('X-Ratelimit-Allowed', '0'))  # Default to 0
            used = int(response.headers.get('X-Ratelimit-Used', '0'))  # Default to 0

            logger.debug(f"X-Ratelimit-Allowed: {allowed}, X-Ratelimit-Used: {used}")
            logger.debug(f"X-Ratelimit-Available: {available}, X-Ratelimit-Expiry: {expiry}")

            # Skip throttling if all rate limit values are zero
            if available == allowed == used == 0:
                return response
            
            if available < 1:
                # If no requests are available, calculate the time until reset and sleep
                sleep_time = max(expiry - int(time.time()), 0)
                logger.debug(f"Sleep required: {sleep_time} - negative values will be ignored.")
                
                if sleep_time > 0:
                    logger.debug(f"Throttling: Sleeping for {sleep_time} seconds")
                    time.sleep(sleep_time)

            return response

    class ApiErrorHandler:
        @staticmethod
        def handle_errors(response):
            # Check for HTTP errors (non-2xx status codes)
            if response.status_code != 200:
                response.raise_for_status()  # Raise an HTTP error if status is not 200

            # If status code is 200, check for API-specific error messages
            error_message = response.json().get('error', {}).get('message')
            if error_message:
                raise TradierAPIException(message=error_message)

            # If no errors, return None (or you can return response for further handling)
            return response

    def __init__(self, config: TradierConfig):
        super().__init__(config)

    def make_request(self, endpoint: Endpoints, path_params: Optional[BaseParams] = None, query_params: Optional[Dict[str, Any]] = None) -> Any:
        """Makes a request to the Tradier API with the given endpoint and parameters."""
        
        # Convert path parameters to dictionary and format the URL
        formatted_path = endpoint.format_path(**(path_params.to_query_params() if path_params else {}))
        url = self._build_url(formatted_path)
        
        # Combine query parameters if provided
        final_query_params = query_params or {}

        try:
            response = requests.request(
                method=endpoint.method,
                url=url,
                headers=self.headers,
                params=final_query_params if endpoint.method in ["GET", "DELETE"] else None,
                data=final_query_params if endpoint.method in ["POST", "PUT"] else None
            )

            # Error and throttling handling
            self.ApiErrorHandler.handle_errors(response)
            self.ThrottleHandler.handle_throttling(response)

            print(f"Response status: {response.json()}")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            raise

        except TradierAPIException as e:
            raise

        except Exception as e:
            raise Exception(f"Error making request to {url}: {str(e)}") from e
    
class TradierStreamController(TradierApiController):
    def __init__(self, config: TradierConfig, streamer: TradierBaseStreamer):
        super().__init__(config)
        self.streamer = streamer
        self.session_key = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def create_session(self):
        """Creates a session and retrieves the session key."""
        response = self.make_request(self.streamer.get_session_endpoint())
        self.session_key = response.get("stream", {}).get("sessionid")
        if not self.session_key:
            raise ValueError("Failed to retrieve session key.")
        logger.debug(f"Session key acquired: {self.session_key}")

    def start(self, params: BaseParams):
        """Starts the HTTP streaming connection in a new thread."""
        if not self.session_key:
            self.create_session()  # Ensures a session is created before streaming

        # Set up a new thread for streaming
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.streamer.run, args=(self.session_key, self._stop_event, params,))
        self._thread.start()

    def close(self):
        """Signals the stream to stop and waits for the thread to exit."""
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
            self._thread = None
        logger.debug("Streaming closed.")
