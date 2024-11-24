# Tradier API Python Library

[![PyPI version](https://badge.fury.io/py/tradier-api.svg)](https://pypi.org/project/tradier-api/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A Python library for interacting with the [Tradier API](https://tradier.com/). This library simplifies access to Tradier's market data, trading functionalities, and account management features.

---

## Features

- **Market Data:** Retrieve historical and real-time market data, including OHLC and volume.
- **Account Management:** Access account balances, positions, and trading history.
- **Order Management:** Place, modify, and cancel orders programmatically.
- **Streaming:** Utilize Tradier's WebSocket API for live market data.
- **Environment Switching:** Easily toggle between sandbox and live environments.
- **Built-in Rate-Limiting:** Rate limits enforced internally by the library code.

---

## Installation

Install the library using `pip`:

```bash
pip install tradier-api
```
---

## Getting Started

### Prerequisites

1. Python 3.6 or higher.
2. An active [Tradier API account](https://tradier.com/).
3. A `_secrets.py` file containing your API tokens and account numbers:
   ```python
   TRADIER_API_TOKEN = "YOUR_LIVE_API_TOKEN"
   TRADIER_API_ACCOUNT = "YOUR_LIVE_ACCOUNT_NUMBER"   
   TRADIER_SANDBOX_TOKEN = "YOUR_SANDBOX_API_TOKEN"
   TRADIER_SANDBOX_ACCT = "YOUR_SANDBOX_ACCOUNT_NUMBER"
   ```

   **Note:** `_secrets.py` is excluded from version control to ensure security.

### Basic Usage

Here’s an example of fetching historical market data:

```python
from tradier_api import LiveConfig, TradierApiController, Endpoints
from _secrets import TRADIER_API_TOKEN

# Initialize the Tradier API with your live token
config = LiveConfig(token=TRADIER_API_TOKEN)
api_controller = TradierApiController(config)

# Fetch historical data for SPY
historical_data = api_controller.make_request(
    endpoint=Endpoints.GET_HISTORICAL_PRICES,
    query_params={
        "symbol": "SPY",
        "interval": "daily",
        "start": "2023-01-01",
        "end": "2023-12-31",
    },
)

# Print the historical data
print(historical_data)
```

---

## Examples

Refer to the `examples/` directory for additional scripts demonstrating various features:

- **[Example: Get User Profile](examples/get_user_profile.py)**
- **[Example: Streaming HTTP Data](examples/http_streaming.py)**
- **[Example: Websocket Data Streaming](examples/websocket_streaming.py)**
- **[Example: Account Data Streaming](examples/account_streaming.py)**
- **[Example: Plot Historical Data](examples/plot_historical_data.py)**
---

## Testing

Run tests using `pytest`:

```bash
pip install pytest
pytest tests/
```

---

## Class Hierarchy

<pre style="font-size: 0.7em; line-height: 1.4;">
+--- TradierAPIException: Custom exception class for handling errors specific to the Tradier API.  
|  
+-- TradierConfig: Manages API configuration, including environment selection and headers.  
|   +-- LiveConfig:                 Configures the API for live production usage.  
|   +-- SandboxConfig:              Configures the API for sandbox (testing) environment usage.  
|   +-- PaperConfig:                Alias for SandobxConfig (paper-trading) type.    
|  
+-- TradierBaseController: Base controller class for shared logic across Tradier API controllers.  
|   +-- TradierApiController:       Main controller for interacting with Tradier REST API endpoints.  
|   +-- TradierStreamController:    Handles configuration and session control for streaming data connections.  
|  
+-- TradierBaseStreamer: Base class for implementing HTTP and WebSocket streaming functionality.  
|   +-- TradierHttpStreamer:        Provides functionality for HTTP-based streaming of market data or events.  
|   +-- TradierWebsocketStreamer:   Implements WebSocket-based streaming for live market and account data.  
|       +-- TradierMarketsStreamer: Specializes in market-specific data streams (e.g., quotes, trades).  
|       +-- TradierAccountStreamer: Specializes in account-related data streams (e.g., balances, orders).  
|  
+-- BaseParams: Abstract base class for defining parameter types used in API requests.  
|   +-- AccountParams:              Handles parameters related to account-specific API requests.  
|   +-- OrderParams:                Represents parameters for order-related API operations.  
|   +-- WatchlistParams:            Manages parameters for watchlist-related API requests.  
|   +-- BaseParamWithNormalization: Base class for parameters that require normalization (e.g., list/string parsing).  
|       +-- SymbolsParams:          Handles parameters for symbol-related API queries with validation.  
|       +-- ExcludedAccountParams:  Manages excluded account parameters for API queries, allowing flexible inputs.  
|  
+-- Enums: Group of enumerations for standardizing API-related constants.  
    +-- APIEnv:                     Defines API environments (e.g., live, sandbox, stream, websocket).  
    +-- Endpoints:                  Maps REST API endpoint paths to their corresponding operations.  
    +-- WebSocketEndpoints:         Enumerates WebSocket-specific endpoints for Tradier API streaming.  
    +-- ExchangeCode:               Defines exchange codes used for identifying market exchanges.  
</pre>
---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

- **Important Notice:** This library is designed for use with the Tradier API. By using this library, you acknowledge that you are bound by Tradier's API terms of service, including but not limited to usage limits, data restrictions, and account requirements. Please ensure you comply with all applicable policies as set forth by Tradier. For more details, visit [Tradier's API documentation](https://tradier.com).
