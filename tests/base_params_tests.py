"""
This module contains unit tests for the parameter classes used in the Tradier API.

The tests cover the following parameter classes:
    - `SymbolsParams`: Validates handling of symbol inputs, ensuring the correct initialization
    and conversion to query parameters. Tests include:
    - Requirement to provide valid symbols, which should raise a `ValueError` for invalid inputs
        like `None`, an empty string, or an empty list.
    - Handling of valid list inputs, ensuring they are correctly converted to query parameters.
    - Handling of valid comma-separated string inputs, ensuring they are correctly parsed and 
        converted to query parameters.

    - `ExcludedAccountParams`: Validates handling of account IDs, ensuring correct initialization
    and conversion to query parameters. Tests include:
    - Handling of `None` input, ensuring it is allowed and correctly handled when converting
        to query parameters.

    - `WatchlistParams`: Validates handling of watchlist ID and optional symbol inputs, ensuring 
    correct initialization and conversion to query parameters. The tests aim to ensure:
    - Both watchlist ID and symbol are correctly included in the query parameters.
    - The class can function with only a watchlist ID.
    - An error is raised if the watchlist ID is not provided.

These tests ensure that the parameter classes behave as expected and generate the correct query
parameters for API requests. This helps maintain the robustness and reliability of the Tradier
API client by catching potential issues in parameter handling early in the development process.

Note: These tests rely on the `unittest` framework and use mocking for any necessary dependencies.

Please ensure that the tests are run in an environment where the Tradier API
client library has been installed and configured properly.
"""
import unittest
from typing import Optional, Dict, Any, Union, List
from tradier_api import SymbolsParams, ExcludedAccountParams, WatchlistParams 

class TestBaseParams(unittest.TestCase):
    def test_symbols_params_requires_symbols(self):
        """Ensure SymbolsParams raises an error for invalid symbol inputs."""
        invalid_inputs = [None, "", []]

        for invalid_input in invalid_inputs:
            with self.subTest(symbols=invalid_input):
                with self.assertRaises(ValueError):
                    SymbolsParams(invalid_input)

    def test_symbols_params_with_list(self):
        """Ensure SymbolsParams handles list input correctly."""
        symbols = ["SPY", "AAPL", "TSLA"]
        params = SymbolsParams(symbols)
        query_params = params.to_query_params()
        self.assertEqual(query_params, {"symbols": "SPY,AAPL,TSLA"})

    def test_symbols_params_with_string(self):
        """Ensure SymbolsParams handles comma-separated string input correctly."""
        symbols = "SPY,AAPL,TSLA"
        params = SymbolsParams(symbols)
        query_params = params.to_query_params()
        self.assertEqual(query_params, {"symbols": "SPY,AAPL,TSLA"})

    def test_excluded_account_params_allows_none(self):
        """Ensure ExcludedAccountParams handles None correctly."""
        params = ExcludedAccountParams(None)
        query_params = params.to_query_params()
        self.assertEqual(query_params, {})  # Expect an empty dictionary

    def test_excluded_account_params_with_list(self):
        """Ensure ExcludedAccountParams handles list input correctly."""
        account_ids = ["acc1", "acc2", "acc3"]
        params = ExcludedAccountParams(account_ids)
        query_params = params.to_query_params()
        self.assertEqual(query_params, {"account_id": "acc1,acc2,acc3"})

    def test_excluded_account_params_with_string(self):
        """Ensure ExcludedAccountParams handles comma-separated string input correctly."""
        account_ids = "acc1,acc2,acc3"
        params = ExcludedAccountParams(account_ids)
        query_params = params.to_query_params()
        self.assertEqual(query_params, {"account_id": "acc1,acc2,acc3"})

    def test_watchlist_params_with_symbol(self):
        """Ensure WatchlistParams handles both watchlist_id and symbol."""
        params = WatchlistParams(watchlist_id="wl123", symbol="AAPL")
        query_params = params.to_query_params()
        self.assertEqual(query_params, {"watchlist_id": "wl123", "symbol": "AAPL"})

    def test_watchlist_params_without_symbol(self):
        """Ensure WatchlistParams works with only watchlist_id."""
        params = WatchlistParams(watchlist_id="wl123")
        query_params = params.to_query_params()
        self.assertEqual(query_params, {"watchlist_id": "wl123"})

    def test_watchlist_params_invalid_id(self):
        """Ensure WatchlistParams raises an error for an empty watchlist_id."""
        with self.assertRaises(ValueError):
            WatchlistParams(watchlist_id="")
