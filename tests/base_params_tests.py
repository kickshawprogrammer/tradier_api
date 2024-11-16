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
