"""
Internal implementation details for the Tradier API.

This module contains classes, types, and functions that are used internally by 
the Tradier API implementation. These definitions are not intended for external 
use and should not be relied upon by outside callers.

External callers should instead use the types and exceptions defined in 
`tradier_types.py` file to interact with the API.
"""
from enum import Enum

class BaseURL(Enum):
    """
    Enumeration for different base URLs used in the Tradier API.

    Attributes:
        API: The base URL for the main API endpoint.
        SANDBOX: The base URL for the sandbox environment.
        STREAM: The base URL for streaming data.
        WEBSOCKET: The base URL for websocket connections.
    """
    API = "https://api.tradier.com"
    SANDBOX = "https://sandbox.tradier.com"
    STREAM = "https://stream.tradier.com"
    WEBSOCKET = "wss://ws.tradier.com"

class ApiPaths(Enum):
    """
    Enumeration of API endpoints.
    """

    # Base paths for parameterized URLs
    OAUTH_BASE = "/v1/oauth"
    ACCOUNTS = "/v1/accounts"
    ACCOUNTS_BASE = ACCOUNTS + "/{account_id}"
    ORDERS_BASE = ACCOUNTS_BASE + "/orders"
    MARKETS_BASE = "/v1/markets"
    OPTIONS_BASE = MARKETS_BASE + "/options"
    FUNDAMENTALS_BASE = "/beta/markets/fundamentals"
    WATCHLISTS_BASE = "/v1/watchlists"

    # Authentication endpoints
    GET_AUTHORIZATION = OAUTH_BASE + "/authorize"        # GET
    CREATE_TOKEN = OAUTH_BASE + "/accesstoken"           # POST
    REFRESH_TOKEN = OAUTH_BASE + "/refreshtoken"         # POST

    # Account endpoints
    GET_PROFILE = "/v1/user/profile"                     # GET
    GET_BALANCES = ACCOUNTS_BASE + "/balances"           # GET
    GET_POSITIONS = ACCOUNTS_BASE + "/positions"         # GET
    GET_HISTORY = ACCOUNTS_BASE + "/history"             # GET
    GET_GAINLOSS = ACCOUNTS_BASE + "/gainloss"           # GET
    GET_ORDERS = ORDERS_BASE                             # GET
    ORDERS_APPLY_ID = "/{order_id}"
    GET_AN_ORDER = ORDERS_BASE + ORDERS_APPLY_ID           # GET

    # Trade endpoints
    MODIFY_ORDER = ORDERS_BASE + ORDERS_APPLY_ID         # PUT
    CANCEL_ORDER = ORDERS_BASE + ORDERS_APPLY_ID         # DELETE
    PLACE_ORDER = ORDERS_BASE                            # POST
    PLACE_EQUITY_ORDER = PLACE_ORDER                     # POST
    PLACE_OPTION_ORDER = PLACE_ORDER                     # POST
    PLACE_MULTILEG_ORDER = PLACE_ORDER                   # POST
    PLACE_COMBO_ORDER = PLACE_ORDER                      # POST
    PLACE_OTO_ORDER = PLACE_ORDER                        # POST
    PLACE_OCO_ORDER = PLACE_ORDER                        # POST
    PLACE_OTOCO_ORDER = PLACE_ORDER                      # POST

    # Market Data endpoints
    GET_QUOTES = MARKETS_BASE + "/quotes"                # GET / POST
    GET_OPTION_CHAINS = OPTIONS_BASE + "/chains"         # GET
    GET_OPTION_STRIKES = OPTIONS_BASE + "/strikes"       # GET
    GET_OPTION_EXPIRATIONS = OPTIONS_BASE + "/expirations"  # GET
    LOOKUP_OPTION_SYMBOLS = OPTIONS_BASE + "/symbols"    # GET
    GET_HISTORICAL_PRICES = MARKETS_BASE + "/history"    # GET
    GET_TIME_AND_SALES = MARKETS_BASE + "/timesales"     # GET
    GET_ETB_LIST = MARKETS_BASE + "/etb"                 # GET
    GET_CLOCK = MARKETS_BASE + "/clock"                  # GET
    GET_CALENDAR = MARKETS_BASE + "/calendar"            # GET
    SEARCH_COMPANIES = MARKETS_BASE + "/search"          # GET
    LOOKUP_SYMBOL = MARKETS_BASE + "/lookup"             # GET

    # Fundamental endpoints
    GET_COMPANY = FUNDAMENTALS_BASE + "/company"                # GET
    GET_CORPORATE_CALENDAR = FUNDAMENTALS_BASE + "/calendar"    # GET
    GET_DIVIDENDS = FUNDAMENTALS_BASE + "/dividends"            # GET
    GET_CORPORATE_ACTIONS = FUNDAMENTALS_BASE + "/corporate_actions" # GET
    GET_RATIOS = FUNDAMENTALS_BASE + "/ratios"                  # GET
    GET_FINANCIAL_REPORTS = FUNDAMENTALS_BASE + "/financials"   # GET
    GET_PRICE_STATS = FUNDAMENTALS_BASE + "/statistics"         # GET

    # Streaming endpoints
    EVENTS="/events"
    EVENTS_SESSION = EVENTS + "/session"
    CREATE_MARKET_SESSION = MARKETS_BASE + EVENTS_SESSION    # POST
    CREATE_ACCOUNT_SESSION = ACCOUNTS + EVENTS_SESSION       # POST
    GET_STREAMING_QUOTES = MARKETS_BASE + EVENTS             # GET / POST

    # WebSocket endpoints
    GET_STREAMING_MARKET_EVENTS = MARKETS_BASE + "/events"      # ws
    GET_STREAMING_ACCOUNT_EVENTS = ACCOUNTS + "/events"    # ws

    # Watchlist endpoints
    GET_WATCHLISTS = WATCHLISTS_BASE                                 # GET
    GET_WATCHLIST = WATCHLISTS_BASE + "/{watchlist_id}"              # GET
    WATCHLIST_APPLY_SYMBOL = "/symbols/{symbol_id}"
    CREATE_WATCHLIST = WATCHLISTS_BASE                               # POST
    UPDATE_WATCHLIST = GET_WATCHLIST                                 # PUT
    DELETE_WATCHLIST = GET_WATCHLIST                                 # DELETE
    ADD_WATCHLIST_SYMBOL = GET_WATCHLIST + WATCHLIST_APPLY_SYMBOL    # POST
    DELETE_WATCHLIST_SYMBOL = GET_WATCHLIST + WATCHLIST_APPLY_SYMBOL # DELETE

