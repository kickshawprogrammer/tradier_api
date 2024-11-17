"""
Unit test module for verifying the URL structure of API endpoints in the Tradier API library.

This module contains test cases for ensuring that the URL paths defined in the `Endpoints` class
of the Tradier API library adhere to the expected structure and contain the correct placeholders
for path parameters. The tests are designed to validate the integrity of URL paths by checking
for the presence of the appropriate placeholders required for constructing valid API requests.

Classes:
    TestApiPathsUrlStructure: A unittest.TestCase subclass that provides test methods for
                              validating the URL structure of API endpoints.

Test Cases:
    - test_endpoint_url_placeholders: Verifies that each API endpoint URL contains the expected
                                       placeholders for path parameters, ensuring that endpoints
                                       requiring dynamic values have the correct parameter names
                                       present in the path.
    
Dependencies:
    - unittest: Provides the base class for creating and running test cases.
    - re: Utilized for regular expression operations within test assertions.
    - tradier_api.Endpoints: The class containing endpoint definitions that map to specific
                             API operations.

Usage:
    Run this module with a Python test runner such as `unittest` or `pytest` to execute the
    test cases and validate the URL structures of the Tradier API endpoints.

Notes:
    - This module assumes that the `Endpoints` class contains endpoint definitions with
      associated URL path templates that may include placeholders for dynamic parameters.
    - The expected placeholders are defined in the `expected_placeholders` dictionary, where
      each key corresponds to an endpoint and the value is a list of expected parameter names.

This module is part of the Tradier API library's test suite, aimed at maintaining the reliability
and correctness of the API client by ensuring that endpoint URLs are properly formatted and ready
for use in API requests.

Please ensure that the tests are run in an environment where the Tradier API
client library has been installed and configured properly.
"""
import unittest
import re
from tradier_api import Endpoints

class TestApiPathsUrlStructure(unittest.TestCase):

    def test_endpoint_url_placeholders(self):
        # Define expected placeholders for each endpoint, using an empty list for paths without parameters
        expected_placeholders = {
            Endpoints.GET_AUTHORIZATION: [],
            Endpoints.CREATE_TOKEN: [],
            Endpoints.REFRESH_TOKEN: [],
            Endpoints.GET_PROFILE: [],
            Endpoints.GET_BALANCES: ["account_id"],
            Endpoints.GET_POSITIONS: ["account_id"],
            Endpoints.GET_HISTORY: ["account_id"],
            Endpoints.GET_GAINLOSS: ["account_id"],
            Endpoints.GET_ORDERS: ["account_id"],
            Endpoints.GET_AN_ORDER: ["account_id", "order_id"],
            Endpoints.MODIFY_ORDER: ["account_id", "order_id"],
            Endpoints.CANCEL_ORDER: ["account_id", "order_id"],
            Endpoints.PLACE_EQUITY_ORDER: ["account_id"],
            Endpoints.PLACE_OPTION_ORDER: ["account_id"],
            Endpoints.PLACE_MULTILEG_ORDER: ["account_id"],
            Endpoints.PLACE_COMBO_ORDER: ["account_id"],
            Endpoints.PLACE_OTO_ORDER: ["account_id"],
            Endpoints.PLACE_OCO_ORDER: ["account_id"],
            Endpoints.PLACE_OTOCO_ORDER: ["account_id"],
            Endpoints.GET_QUOTES: [],
            Endpoints.GET_OPTION_CHAINS: [],
            Endpoints.GET_OPTION_STRIKES: [],
            Endpoints.GET_OPTION_EXPIRATIONS: [],
            Endpoints.LOOKUP_OPTION_SYMBOLS: [],
            Endpoints.GET_HISTORICAL_PRICES: [],
            Endpoints.GET_TIME_AND_SALES: [],
            Endpoints.GET_ETB_LIST: [],
            Endpoints.GET_CLOCK: [],
            Endpoints.GET_CALENDAR: [],
            Endpoints.SEARCH_COMPANIES: [],
            Endpoints.LOOKUP_SYMBOL: [],
            Endpoints.GET_COMPANY: [],
            Endpoints.GET_CORPORATE_CALENDAR: [],
            Endpoints.GET_DIVIDENDS: [],
            Endpoints.GET_CORPORATE_ACTIONS: [],
            Endpoints.GET_RATIOS: [],
            Endpoints.GET_FINANCIAL_REPORTS: [],
            Endpoints.GET_PRICE_STATS: [],
            Endpoints.CREATE_MARKET_SESSION: [],
            Endpoints.CREATE_ACCOUNT_SESSION: [],
            Endpoints.GET_STREAMING_QUOTES: [],
            Endpoints.GET_STREAMING_MARKET_EVENTS: [],
            Endpoints.GET_STREAMING_ACCOUNT_EVENTS: [],
            Endpoints.GET_WATCHLISTS: [],
            Endpoints.GET_WATCHLIST: ["watchlist_id"],
            Endpoints.CREATE_WATCHLIST: [],
            Endpoints.UPDATE_WATCHLIST: ["watchlist_id"],
            Endpoints.DELETE_WATCHLIST: ["watchlist_id"],
            Endpoints.ADD_WATCHLIST_SYMBOL: ["watchlist_id", "symbol_id"],
            Endpoints.DELETE_WATCHLIST_SYMBOL: ["watchlist_id", "symbol_id"],
        }

        for endpoint, expected_placeholders_list in expected_placeholders.items():
            with self.subTest(endpoint=endpoint):
                # Get the path and extract placeholders
                path = endpoint.path
                placeholders = re.findall(r"{(.*?)}", path)

                # Verify no missing or extra placeholders
                missing_placeholders = set(expected_placeholders_list) - set(placeholders)
                extra_placeholders = set(placeholders) - set(expected_placeholders_list)
                
                self.assertFalse(
                    missing_placeholders,
                    f"{endpoint.name} is missing placeholders: {missing_placeholders}"
                )
                
                self.assertFalse(
                    extra_placeholders,
                    f"{endpoint.name} has extra placeholders: {extra_placeholders}"
                )

                # Ensure the URL structure is correctly formed
                formatted_path = endpoint.format_path(
                    **{param: "test_value" for param in expected_placeholders_list}
                )
                for placeholder in expected_placeholders_list:
                    self.assertNotIn(f"{{{placeholder}}}", formatted_path, f"Placeholder {placeholder} was not replaced in {endpoint.name} URL.")

