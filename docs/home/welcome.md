
# Welcome to Tradier API

Welcome to the **Tradier API** library! This documentation will help you understand how to set up, use, and maximize the potential of the `tradier_api` package.

---

## What is Tradier API?

The `tradier_api` library is a powerful tool for integrating with the Tradier brokerage platform, offering a streamlined interface to:

- Access market data.
- Manage your trading accounts.
- Execute orders programmatically.
- Leverage advanced functionality like streaming and WebSocket APIs (coming soon).

Whether you're building automated trading systems, analyzing market data, or experimenting with algorithmic trading, `tradier_api` has you covered.

---

## Getting Started

Follow these simple steps to get up and running with the library:

### 1. Installation

Install the `tradier_api` package via PyPI:

```bash
pip install tradier_api
```

### 2. Configuration

Create a configuration object for your API key and environment:

```python
from tradier_api import TradierConfig, APIEnv

config = TradierConfig(api_key="YOUR_API_KEY", environment=APIEnv.PRODUCTION)
```

### 3. Making Your First API Call

Here’s an example of fetching market quotes:

```python
from tradier_api import TradierApiController

controller = TradierApiController(config)
response = controller.make_request(endpoint="markets/quotes", parameters={"symbols": "AAPL,MSFT"})
print(response)
```

---

## Key Features

### Simple Integration
Seamlessly connect to Tradier’s platform using a well-documented and Pythonic interface.

### Modular Design
Leverage the modular structure to customize and extend functionality as needed.

### Parameterized Endpoints
Work with dynamic, parameterized endpoints for flexible API calls.

### Example Use Cases
Explore ready-to-use examples for common workflows, from fetching market data to managing watchlists.

---

## Next Steps

- Check out the **[Source Code](../source_code/tradier_api/index.md)** for an in-depth look at individual modules.
- Refer to **[Examples](../source_code/examples/index.md)** to explore pre-built scripts.
- Dive into **[How-To Guides](../how_to/index.md)** for endpoint-specific tutorials (coming soon).

---

## Need Assistance?

- Visit the [GitHub repository](https://github.com/your-repo-url).
- Review the [README](readme.md) for a project overview.
- Open a GitHub issue if you encounter problems.

Thank you for choosing `tradier_api`! We look forward to seeing what you build.
