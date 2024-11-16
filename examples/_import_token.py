"""
_import_token.py

This module provides access to API tokens and account information for the Tradier API, allowing example scripts and 
other modules to use these credentials without directly exposing sensitive data.

### `_secrets.py`

The `_secrets.py` file is expected to define the following variables:

- `TRADIER_API_TOKEN`: Your API token for live trading.
- `TRADIER_API_ACCOUNT` (optional): Your live trading account number.
- `TRADIER_SANDBOX_TOKEN`: Your API token for sandbox (test) trading.
- `TRADIER_SANDBOX_ACCT` (optional): Your sandbox account number.

These values are critical for interacting with the Tradier API and should be kept secure. For this reason:

1. **Do not commit `_secrets.py` to version control.**
   - `_secrets.py` is `.gitignore`'d to prevent accidental exposure of sensitive data.

2. **Placeholder Behavior:**
   - If `_secrets.py` is unavailable, the module will fallback to using placeholder value. Replace these placeholders 
     with your actual credentials when deploying or running examples.

### Usage

Import the `API_TOKEN` (or any other necessary credentials) into your example or script:

    ```python
    from _import_token import API_TOKEN

    print(f"My API token is: {API_TOKEN}")
    ```

### Security Note

Always treat API tokens and account numbers as sensitive information. Ensure _secrets.py is stored 
securely and excluded from any public or shared repositories. 

"""
import sys
from pathlib import Path

# Add the parent directory to sys.path for accessing _secrets.py
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Fallback placeholder values
PLACEHOLDER_TOKEN = "ENTER_YOUR_API_TOKEN_HERE"
PLACEHOLDER_ACCOUNT = "ENTER_YOUR_ACCOUNT_NUMBER_HERE"

# Try to import credentials from _secrets.py, fallback if not available
try:
    from _secrets import (
        TRADIER_API_TOKEN,
        TRADIER_API_ACCOUNT,
        TRADIER_SANDBOX_TOKEN,
        TRADIER_SANDBOX_ACCT,
    )
except ImportError:
    TRADIER_API_TOKEN = PLACEHOLDER_TOKEN
    TRADIER_API_ACCOUNT = PLACEHOLDER_ACCOUNT
    TRADIER_SANDBOX_TOKEN = PLACEHOLDER_TOKEN
    TRADIER_SANDBOX_ACCT = PLACEHOLDER_ACCOUNT

# Re-export the tokens under generic names for consistent use
API_TOKEN = TRADIER_API_TOKEN
SANDBOX_TOKEN = TRADIER_SANDBOX_TOKEN
API_ACCOUNT = TRADIER_API_ACCOUNT
SANDBOX_ACCOUNT = TRADIER_SANDBOX_ACCT
