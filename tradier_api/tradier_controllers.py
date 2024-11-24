"""
Module containing API controller classes for the Tradier API.

This module provides abstract base classes for API controllers for the Tradier
API. These controllers provide higher-level interfaces for interacting with the
API, wrapping the underlying HTTP request and error handling.

Controllers are responsible for encapsulating the logic for interacting with the
API, including generating the correct URL for the request and handling errors
raised by the API.

This module provides the following abstract base classes:

- `TradierBaseController`: The base class for all API controllers.
- `TradierApiController`: A controller for interacting with the main API
  endpoint.
- `TradierStreamController`: A controller for interacting with the streaming API
  endpoint.

"""
import time
import requests
import threading

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

from ._core_types import BaseURL
from .tradier_types import TradierAPIException, Endpoints
from .tradier_params import PathParams, QueryParams, BaseParamWithNormalization
from .tradier_config import TradierConfig
from .tradier_streams import TradierBaseStreamer

import logging
logger = logging.getLogger(__name__)

class TradierBaseController:
    """
    Abstract base class for API controllers.

    This class serves as the base class for all API controllers. It provides a standard
    interface for interacting with the API, including:

    - `__init__`: Initializes the controller with the given configuration.
    - `_get_base_url`: Returns the base URL for the API based on the environment.
    - `_build_url`: Builds the URL based on the base URL and endpoint.

    This class is intended to be subclassed to provide more specialized controllers
    for different endpoints of the API.

    Attributes:
        config (TradierConfig): The configuration for the controller.
        base_url (str): The base URL for the API based on the environment.
        headers (Dict[str, str]): The headers to be used when making requests to the API.
    """
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
    """
    Controller class for interacting with the Tradier API.

    The `TradierApiController` is responsible for making requests to the Tradier API,
    handling throttling, and managing errors. It extends the `TradierBaseController` 
    to provide additional functionality specific to the Tradier API endpoints.

    Attributes:
        config (TradierConfig): The configuration for the API controller, including
            the access token and environment settings.
        headers (Dict[str, str]): HTTP headers used for requests to the API.

    Inner Classes:
        ThrottleHandler: Handles API rate limiting by managing the waiting time 
                         based on the rate limit headers returned by the API.
        ApiErrorHandler: Processes the API response to identify and handle any
                         errors, whether HTTP-related or specific to the Tradier API.
    
    Methods:
        __init__(config: TradierConfig):
            Initializes the controller with the provided configuration.

        make_request(endpoint: Endpoints, path_params: Optional[BaseParams] = None, 
                     query_params: Optional[Dict[str, Any]] = None) -> Any:
            Makes a request to the Tradier API using the specified endpoint and parameters.
    """
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

    def make_request( 
            self,
            endpoint: Endpoints, 
            path_params: Optional[PathParams] = None, 
            query_params: Optional[Union[QueryParams, Dict[str, Any]]] = None 
    ) -> Any:
        """Makes a request to the Tradier API with the given endpoint and parameters."""
        
        # Helper function to normalize query parameters
        def normalize_query_params(params: Optional[Union[QueryParams, Dict[str, Any]]]) -> Dict[str, Any]:
            """Converts QueryParams or dictionary into a standard dictionary."""
            if params is None:
                return {}
            if isinstance(params, QueryParams):
                return params.to_query_params()
            if isinstance(params, dict):
                return params
            raise ValueError("query_params must be of type QueryParams or Dict[str, Any]")
        
        # Normalize path parameters
        path_dict = path_params.to_query_params() if path_params else {}
        formatted_path = endpoint.format_path(**path_dict)
        url = self._build_url(formatted_path)
        
        # Normalize query parameters
        final_query_params = normalize_query_params(query_params)

        try:
            response = requests.request(
                method=endpoint.method,
                url=url,
                headers=self.headers,
                params=final_query_params if endpoint.method in ["GET", "DELETE"] else None,
                data=final_query_params if endpoint.method in ["POST", "PUT"] else None,
            )

            # Error and throttling handling
            self.ApiErrorHandler.handle_errors(response)
            self.ThrottleHandler.handle_throttling(response)

            return response.json()

        except requests.exceptions.HTTPError as e:
            raise

        except TradierAPIException as e:
            raise

        except Exception as e:
            raise Exception(f"Error making request to {url}: {str(e)}") from e
        
class TradierStreamController(TradierApiController):
    """
    Controller class for interacting with the Tradier API for streaming.

    The `TradierStreamController` is responsible for managing the lifetime of an
    streaming connection to the Tradier API. It extends the `TradierApiController`
    to provide additional functionality specific to the streaming endpoints.

    Attributes:
        config (TradierConfig): The configuration for the API controller, including
            the access token and environment settings.
        streamer (TradierBaseStreamer): The streamer object responsible for running
            the streaming connection.
        session_key (str): The session key acquired after creating a session.
        _stop_event (threading.Event): Used to signal the stream to stop.
        _thread (threading.Thread): The thread running the streaming connection.

    Methods:
        __init__(config: TradierConfig, streamer: TradierBaseStreamer):
            Initializes the controller with the provided configuration and streamer.

        create_session():
            Creates a session and retrieves the session key.

        start(params: BaseParams):
            Starts the streaming connection in a new thread using the session key.

        close():
            Signals the stream to stop and waits for the thread to exit.
    """
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

    def start(self, params: BaseParamWithNormalization):
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
