"""
Module containing parameter classes for the Tradier API.

This module provides classes for defining parameters that can be used with the
Tradier API. These classes are used to define the parameters for API endpoints,
and can be used to generate query strings or URL paths for API requests.

The following classes are available in this module:

- `BaseParams`: A base class for all parameter classes, providing a method for
  converting the parameters to a dictionary.
- `PathParams`: A base class for parameters that are used in URL paths.
- `AccountPathParams`: Parameters for API endpoints that require an account ID.
- `OrderPathParams`: Parameters for API endpoints that require an account ID and
  order ID.
- `WatchlistPathParams`: Parameters for API endpoints that require a watchlist ID
  and optional symbol.

"""
from typing import Optional, Union, List, Dict, Any

class BaseParams:
    def to_query_params(self) -> dict:
        """
        Converts the parameters to a dictionary, filtering out any None values.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

#####################################################################################
#####################################################################################

class PathParams(BaseParams):
    pass

class AccountPathParams(PathParams):
    def __init__(self, account_id: str):
        self.account_id = account_id

class OrderPathParams(PathParams):
    def __init__(self, account_id: str, order_id: str):
        self.account_id = account_id
        self.order_id = order_id

class WatchlistPathParams(PathParams):
    def __init__(self, watchlist_id: str, symbol: Optional[str] = None):
        if watchlist_id is None or watchlist_id.strip() == "":
            raise ValueError("Watchlist ID is required but was not provided.")
        
        self.watchlist_id = watchlist_id
        self.symbol = symbol

#####################################################################################
#####################################################################################

class QueryParams(BaseParams):
    pass

class BaseParamWithNormalization(QueryParams):
    def __init__(self, values: Union[List[str], str, None], key: str, required: bool = True):
        """
        Base class for parameter types that normalize list, string, or None inputs.

        Args:
            values (Union[List[str], str, None]): List of strings, a comma-separated string, or None.
            key (str): The key to use for query parameter generation.
            required (bool): Whether the values parameter is mandatory.
        """
        if values is None:
            if required:
                raise ValueError(f"{key} is required but was not provided.")
            self.values = []
        elif isinstance(values, str):
            self.values = [v.strip() for v in values.split(",")]
        elif isinstance(values, list):
            self.values = values
        else:
            raise ValueError(f"{key} must be a list, a comma-separated string, or None.")
        self.key = key

    def to_query_params(self) -> Dict[str, Any]:
        """Convert the normalized values to a query parameter dictionary."""
        if not self.values:
            return {}  # Return an empty dictionary if there are no values
        return {self.key: self.values}

class SymbolsParams(BaseParamWithNormalization):
    def __init__(self, symbols: Union[List[str], str]):
        if symbols is None or symbols == "" or (isinstance(symbols, list) and not symbols):
            raise ValueError("Symbols must not be empty.")
        super().__init__(values=symbols, key="symbols", required=True)

class ExcludedAccountParams(BaseParamWithNormalization):
    def __init__(self, account_ids: Union[List[str], str, None] = None):
        super().__init__(values=account_ids, key="account_id", required=False)
