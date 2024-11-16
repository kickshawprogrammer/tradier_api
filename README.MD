### `README.md`
---

# Tradier API Python Library

[![PyPI version](https://badge.fury.io/py/tradier-api.svg)](https://pypi.org/project/tradier-api/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A Python library for interacting with the [Tradier API](https://developer.tradier.com/). This library simplifies access to Tradier's market data, trading functionalities, and account management features.

---

## Features

- **Market Data**: Retrieve historical and real-time market data, including OHLC and volume.
- **Account Management**: Access account balances, positions, and trading history.
- **Order Management**: Place, modify, and cancel orders programmatically.
- **Streaming**: Utilize Tradier's WebSocket API for live market data.
- **Environment Switching**: Easily toggle between sandbox and live environments.

---

## Installation

Install the library using `pip`:

```bash
pip install tradier-api
```

Or install the development version directly from source:

```bash
git clone https://github.com/kickshawprogrammer/tradier_api.git
cd tradier_api
pip install -e .
```

---

## Getting Started

### Prerequisites

1. Python 3.6 or higher.
2. An active [Tradier API account](https://developer.tradier.com/).
3. A `_secrets.py` file containing your API tokens and account numbers:
   ```python
   TRADIER_API_TOKEN = "YOUR_LIVE_API_TOKEN"
   TRADIER_API_ACCOUNT = "YOUR_LIVE_ACCOUNT_NUMBER"   TRADIER_SANDBOX_TOKEN = "YOUR_SANDBOX_API_TOKEN"
   TRADIER_SANDBOX_ACCT = "YOUR_SANDBOX_ACCOUNT_NUMBER"
   ```

   **Note**: `_secrets.py` is excluded from version control to ensure security.

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
- **[Example: Plot Historical Data](examples/plot_historical_data.py)**
- **[Example: Websocket Data Streaming](examples/websocket_streaming.py)**
- **[Example: Streaming HTTP Data](examples/http_streaming.py)**
---

## Testing

Run tests using `pytest`:

```bash
pip install pytest
pytest tests/
```

---

## Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---

## License

Feel free to use in any way you wish; but please, be kind and do good!

