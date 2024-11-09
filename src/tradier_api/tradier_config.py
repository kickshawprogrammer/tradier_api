from enum import Enum
from typing import Optional, Dict, Union

class APIEnv(Enum):
    """
    Enumeration representing different environments for the Tradier API.

    Attributes:
        LIVE: Represents the live production environment.
        SANDBOX: Represents the sandbox environment for testing.
        PAPER: An alias for the sandbox environment.
    """
    LIVE = "live"
    SANDBOX = "sandbox"
    PAPER = "sandbox"  # Alias to Sandbox

class TradierConfig:
    """
    Encapsulates configuration for the Tradier API, including the access token and environment.

    Attributes:
        token (str): The access token to use for all requests.
        environment (APIEnv): The environment to use for requests. Defaults to the live environment.
        headers (Dict[str, str]): The HTTP headers to use for requests, including the access token and content type.
    """
    def __init__(self, 
                 token: str, 
                 environment: Optional[Union[APIEnv, str]] = APIEnv.LIVE):
        """
        Initializes a TradierConfig object with the given token and environment.

        Args:
            token: The access token to use for all requests.
            environment: The environment to use, defaults to the live environment.
        """
        environment = environment or APIEnv.LIVE
        self.token = token
        self.environment = self._validate_environment(environment)
        
        # Header settings
        self._accept_gzip = True
        self._accept_application = "application/json"
        
        # Initial header build
        self.headers = self._build_headers()
    
    def _validate_environment(self, environment: Union[APIEnv, str]) -> APIEnv:
        """Validates and returns an APIEnv enum member based on input."""
        if isinstance(environment, APIEnv):
            return environment
        elif isinstance(environment, str):
            try:
                return APIEnv(environment.lower())
            except ValueError:
                raise ValueError(f"Invalid environment '{environment}'. Choose from: {[e.value for e in APIEnv]}")
            
        raise TypeError("Environment must be of type APIEnv or str")

    def _build_headers(self) -> Dict[str, str]:
        """Builds the headers based on current settings."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": self._accept_application
        }
        if self._accept_gzip:
            headers["Accept-Encoding"] = "gzip"
        return headers

    def set_accept_gzip_encoding(self, accept: bool = True) -> None:
        """Sets whether to accept gzip encoding."""
        self._accept_gzip = accept
        self.headers = self._build_headers()  # Rebuild headers on change
    
    def set_accept_application(self, content_type: str = "json") -> None:
        """Sets the content type to accept, either JSON or XML."""
        if content_type.lower() not in ["json", "xml"]:
            raise ValueError("Content type must be either 'json' or 'xml'")
        
        self._accept_application = f"application/{content_type.lower()}"
        self.headers = self._build_headers()  # Rebuild headers on change
