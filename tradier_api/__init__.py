"""
Tradier API client library for Python.

The Tradier API is a set of cloud-based financial services offering trading, real-time
data, and other financial services through a simple, yet powerful API.

This library provides a convenient interface to these services, allowing you to:

- Fetch real-time market data
- Stream real-time market events
- Fetch historical market data
- Trade stocks and options
- Manage watchlists and accounts
- Fetch corporate actions and other financial data

The library is organized into several subpackages:

- `tradier_api.tradier_types`: defines public types and exceptions used by the API
- `tradier_api.tradier_params`: defines parameter classes used by the API
- `tradier_api.tradier_config`: defines configuration classes used by the API
- `tradier_api.tradier_controllers`: defines classes used to interact with the API
- `tradier_api.tradier_streams`: defines classes used to stream data from the API

The main entrypoints are:

- `TradierConfig`: a class representing the configuration for the API
- `TradierApiController`: a class providing a convenient interface to the API
- `TradierStreamController`: a class providing a convenient interface to streaming
  data from the API

"""
import logging

from .tradier_types import TradierAPIException, Endpoints, WebSocketEndpoints, ExchangeCode
from .tradier_params import (PathParams, QueryParams, AccountPathParams, OrderPathParams,
                             WatchlistPathParams, SymbolsParams, ExcludedAccountParams)
from .tradier_config import APIEnv, TradierConfig, SandboxConfig, LiveConfig, PaperConfig
from .tradier_controllers import TradierBaseController, TradierApiController, TradierStreamController
from .tradier_streams import (TradierBaseStreamer, TradierHttpStreamer, TradierWebsocketStreamer,
                              TradierMarketsStreamer, TradierAccountStreamer)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

logger.info(f"Initializing Tradier API: {__name__}")

__all__ = [
    # tradier_config.py
    "APIEnv",
    "TradierConfig",
    "SandboxConfig",
    "LiveConfig",
    "PaperConfig",

    # tradier_types.py
    "TradierAPIException",
    "Endpoints",
    "WebSocketEndpoints",
    "ExchangeCode",

    # tradier_params.py
    "PathParams",
    "QueryParams",
    "AccountPathParams",
    "OrderPathParams",
    "WatchlistPathParams",
    "SymbolsParams",
    "ExcludedAccountParams",

    # tradier_controllers.py
    "TradierBaseController",
    "TradierApiController",
    "TradierStreamController",

    #tradier_streams.py
    "TradierBaseStreamer",
    "TradierHttpStreamer",
    "TradierWebsocketStreamer",
    "TradierMarketsStreamer",
    "TradierAccountStreamer"
]
    