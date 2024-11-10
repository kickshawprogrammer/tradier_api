"""
Module containing public types and exceptions for the Tradier API.

This module provides classes and types that can be used by external callers to 
interact with the Tradier API. It includes exceptions that may be raised by the
API, as well as other types that can be used to define API requests and responses.

Internal implementation details are defined in `_core_definitions.py` and should \
not be used directly by external callers.
"""
import re

from enum import Enum

from ._core_types import ApiPaths

class TradierAPIException(Exception):
    """Base class for all API exceptions."""
    def __init__(self, status_code=None, message="An error occurred with the Tradier API"):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Status {status_code}: {message}")

class Endpoints(Enum):
    """Publicly accessible API endpoints for the Tradier API."""
    
    # Authentication
    GET_AUTHORIZATION = ("GET", ApiPaths.GET_AUTHORIZATION)
    CREATE_TOKEN = ("POST", ApiPaths.CREATE_TOKEN)
    REFRESH_TOKEN = ("POST", ApiPaths.REFRESH_TOKEN)

    # Account
    GET_PROFILE = ("GET", ApiPaths.GET_PROFILE)
    GET_BALANCES = ("GET", ApiPaths.GET_BALANCES)
    GET_POSITIONS = ("GET", ApiPaths.GET_POSITIONS)
    GET_HISTORY = ("GET", ApiPaths.GET_HISTORY)
    GET_GAINLOSS = ("GET", ApiPaths.GET_GAINLOSS)
    GET_ORDERS = ("GET", ApiPaths.GET_ORDERS)
    GET_AN_ORDER = ("GET", ApiPaths.GET_AN_ORDER)

    # Trade
    MODIFY_ORDER = ("PUT", ApiPaths.MODIFY_ORDER)
    CANCEL_ORDER = ("DELETE", ApiPaths.CANCEL_ORDER)
    PLACE_EQUITY_ORDER = ("POST", ApiPaths.PLACE_EQUITY_ORDER)
    PLACE_OPTION_ORDER = ("POST", ApiPaths.PLACE_OPTION_ORDER)
    PLACE_MULTILEG_ORDER = ("POST", ApiPaths.PLACE_MULTILEG_ORDER)
    PLACE_COMBO_ORDER = ("POST", ApiPaths.PLACE_COMBO_ORDER)
    PLACE_OTO_ORDER = ("POST", ApiPaths.PLACE_OTO_ORDER)
    PLACE_OCO_ORDER = ("POST", ApiPaths.PLACE_OCO_ORDER)
    PLACE_OTOCO_ORDER = ("POST", ApiPaths.PLACE_OTOCO_ORDER)

    # Market Data
    GET_QUOTES = ("POST", ApiPaths.GET_QUOTES)
    GET_OPTION_CHAINS = ("GET", ApiPaths.GET_OPTION_CHAINS)
    GET_OPTION_STRIKES = ("GET", ApiPaths.GET_OPTION_STRIKES)
    GET_OPTION_EXPIRATIONS = ("GET", ApiPaths.GET_OPTION_EXPIRATIONS)
    LOOKUP_OPTION_SYMBOLS = ("GET", ApiPaths.LOOKUP_OPTION_SYMBOLS)
    GET_HISTORICAL_PRICES = ("GET", ApiPaths.GET_HISTORICAL_PRICES)
    GET_TIME_AND_SALES = ("GET", ApiPaths.GET_TIME_AND_SALES)
    GET_ETB_LIST = ("GET", ApiPaths.GET_ETB_LIST)
    GET_CLOCK = ("GET", ApiPaths.GET_CLOCK)
    GET_CALENDAR = ("GET", ApiPaths.GET_CALENDAR)
    SEARCH_COMPANIES = ("GET", ApiPaths.SEARCH_COMPANIES)
    LOOKUP_SYMBOL = ("GET", ApiPaths.LOOKUP_SYMBOL)

    # Fundamentals
    GET_COMPANY = ("GET", ApiPaths.GET_COMPANY)
    GET_CORPORATE_CALENDAR = ("GET", ApiPaths.GET_CORPORATE_CALENDAR)
    GET_DIVIDENDS = ("GET", ApiPaths.GET_DIVIDENDS)
    GET_CORPORATE_ACTIONS = ("GET", ApiPaths.GET_CORPORATE_ACTIONS)
    GET_RATIOS = ("GET", ApiPaths.GET_RATIOS)
    GET_FINANCIAL_REPORTS = ("GET", ApiPaths.GET_FINANCIAL_REPORTS)
    GET_PRICE_STATS = ("GET", ApiPaths.GET_PRICE_STATS)

    # Streaming
    CREATE_MARKET_SESSION = ("POST", ApiPaths.CREATE_MARKET_SESSION)
    CREATE_ACCOUNT_SESSION = ("POST", ApiPaths.CREATE_ACCOUNT_SESSION)
    GET_STREAMING_QUOTES = ("POST", ApiPaths.GET_STREAMING_QUOTES)

    # Watchlist
    GET_WATCHLISTS = ("GET", ApiPaths.GET_WATCHLISTS)
    GET_WATCHLIST = ("GET", ApiPaths.GET_WATCHLIST)
    CREATE_WATCHLIST = ("POST", ApiPaths.CREATE_WATCHLIST)
    UPDATE_WATCHLIST = ("PUT", ApiPaths.UPDATE_WATCHLIST)
    DELETE_WATCHLIST = ("DELETE", ApiPaths.DELETE_WATCHLIST)
    ADD_WATCHLIST_SYMBOL = ("POST", ApiPaths.ADD_WATCHLIST_SYMBOL)
    DELETE_WATCHLIST_SYMBOL = ("DELETE", ApiPaths.DELETE_WATCHLIST_SYMBOL)

    @property
    def method(self) -> str:
        """Returns the HTTP method as a string."""
        return self.value[0]

    @property
    def path(self) -> str:
        """Returns the URL path as a string."""
        return self.value[1].value
    
    def format_path(self, **path_params) -> str:
        """Formats the endpoint path by filling placeholders with provided parameters in order."""
        # Find all placeholders in the path (e.g., {account_id}, {order_id})
        placeholders = re.findall(r"\{(.*?)\}", self.path)
        
        # Ensure the number of provided parameters matches the placeholders
        if len(placeholders) != len(path_params):
            raise ValueError(f"{self.name} requires {len(placeholders)} parameters, but {len(path_params)} were provided.")

        # Use only the values in the provided order
        values = list(path_params.values())
        
        # Replace placeholders with corresponding values from path_params
        formatted_path = self.path
        for placeholder, value in zip(placeholders, values):
            formatted_path = formatted_path.replace(f"{{{placeholder}}}", str(value))

        return formatted_path
    
class WebSocketEndpoints(Enum):
    """Public WebSocket API endpoints for Tradier."""
    STREAM_MARKET_EVENTS = ApiPaths.GET_STREAMING_MARKET_EVENTS.value
    STREAM_ACCOUNT_EVENTS = ApiPaths.GET_STREAMING_ACCOUNT_EVENTS.value
        
class ExchangeCode(Enum):
    """
    Enumeration for different exchanges used in the Tradier API.
    """
    NYSE_MKT = "A"
    NASDAQ_BX = "B"
    NATIONAL_STOCK_EXCHANGE = "C"
    FINRA_ADF = "D"
    MARKET_INDEPENDENT = "E"
    MUTUAL_FUNDS = "F"
    INTERNATIONAL_SECURITIES_EXCHANGE = "I"
    DIRECT_EDGE_A = "J"
    DIRECT_EDGE_X = "K"
    LONG_TERM_STOCK_EXCHANGE = "L"
    CHICAGO_STOCK_EXCHANGE = "M"
    NYSE = "N"
    NYSE_ARCA = "P"
    NASDAQ_OMX = "Q"
    NASDAQ_SMALL_CAP = "S"
    NASDAQ_INT = "T"
    OTCBB = "U"
    OTC_OTHER = "V"
    CBOE = "W"
    NASDAQ_OMX_PSX = "X"
    GLOBEX = "G"
    BATS_Y_EXCHANGE = "Y"
    BATS = "Z"

    # OPRA Feeds (Options)
    NYSE_AMEX_OPTIONS = "A"
    BOX_OPTIONS_EXCHANGE = "B"
    CBOE_OPTIONS = "C"
    ISE_GEMINI = "H"
    MIAX_OPTIONS_EXCHANGE = "M"
    NYSE_ARCA_OPTIONS = "N"
    OPRA = "O"
    MIAX_PEARL = "P"
    NASDAQ_OPTIONS_MARKET = "Q"
    NASDAQ_OMX_BX_OPTIONS = "T"
    C2_OPTIONS_EXCHANGE = "W"
    NASDAQ_OMX_PHLX = "X"
    BATS_OPTIONS_MARKET = "Z"    
