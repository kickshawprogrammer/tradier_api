"""
Module: tests/make_request_with_params_tests.py

This module contains unit tests for testing the functionality of making requests with various 
parameters using the Tradier API. These tests are designed to ensure that the `TradierApiController` 
correctly handles different parameter types and API endpoint requests. The module leverages the 
`unittest` framework for structuring and running test cases, and utilizes mocking to simulate 
API interactions without making actual HTTP requests.

The primary focus of this module is to validate the correct construction and execution of requests 
using parameter classes such as `AccountParams`, `OrderParams`, `WatchlistParams`, and `SymbolsParams`. 
Each parameter class is responsible for managing specific parts of the API request, such as account 
information, order details, watchlist specifications, and symbol queries.

Key Components:
  - `TradierApiController`: The main controller used for interacting with Tradier API endpoints. 
    It is responsible for constructing requests, sending them to the appropriate endpoints, and 
    handling responses.
  - Parameter Classes: These classes encapsulate various parameters required for different API requests:
    - `AccountParams`: Handles parameters related to account-specific API requests.
    - `OrderParams`: Represents parameters for order-related API operations.
    - `WatchlistParams`: Manages parameters for watchlist-related API requests.
    - `SymbolsParams`: Handles parameters for symbol-related API queries.

Test Structure:
  - `TestMakeRequestWithParams`: The main test class that inherits from `unittest.TestCase`. It 
    includes setup methods for initializing test environments and test methods for verifying 
    the correct behavior of request-making processes.
  - Mocking: Utilizes `unittest.mock` to simulate API responses and interactions, allowing tests 
    to run in isolation from actual API endpoints.

This module ensures the robustness and reliability of the Tradier API client by validating 
that requests are constructed and executed correctly with varying parameters. It helps 
identify and address potential issues early in the development process, facilitating 
smooth integration of the Tradier API into applications.

Please ensure that the Tradier API client library is installed and properly configured 
in your testing environment before running these tests.
"""
import unittest
from unittest.mock import patch, MagicMock
from tradier_api import TradierApiController, Endpoints, AccountParams, OrderParams, \
                        WatchlistParams, SymbolsParams

from tradier_api._core_types import BaseURL

class TestMakeRequestWithParams(unittest.TestCase):

    def setUp(self):
        # Mock the configuration environment as "Sandbox" for this test
        config = MagicMock()
        config.environment.value = "Sandbox"
        config.headers = {"Authorization": "Bearer test_token"}
        self.api_controller = TradierApiController(config)

        # Mock the base URL based on environment setting
        with patch.object(self.api_controller, '_get_base_url', return_value=BaseURL.SANDBOX.value) as mock_base_url:
            self.base_url = mock_base_url.return_value

    @patch('requests.request')
    def test_make_request_with_params(self, mock_request):
        # Prepare expected endpoint and parameter mappings
        symbols = SymbolsParams(symbols=["AAPL", "GOOGL", "MSFT"])
        test_cases = [
            # AccountParams test cases
            (Endpoints.GET_BALANCES, AccountParams(account_id="12345678"), "/v1/accounts/12345678/balances"),
            (Endpoints.GET_POSITIONS, AccountParams(account_id="87654321"), "/v1/accounts/87654321/positions"),
            (Endpoints.GET_HISTORY, AccountParams(account_id="12345678"), "/v1/accounts/12345678/history"),

            # OrderParams test cases
            (Endpoints.GET_AN_ORDER, OrderParams(account_id="12345678", order_id="987654"), "/v1/accounts/12345678/orders/987654"),
            (Endpoints.MODIFY_ORDER, OrderParams(account_id="87654321", order_id="123987"), "/v1/accounts/87654321/orders/123987"),
            (Endpoints.CANCEL_ORDER, OrderParams(account_id="11223344", order_id="998877"), "/v1/accounts/11223344/orders/998877"),

            # WatchlistParams test cases
            (Endpoints.GET_WATCHLIST, WatchlistParams(watchlist_id="watchlist1"), "/v1/watchlists/watchlist1"),
            (Endpoints.DELETE_WATCHLIST_SYMBOL, WatchlistParams(watchlist_id="watchlist1", symbol="AAPL"), "/v1/watchlists/watchlist1/symbols/AAPL"),
            (Endpoints.DELETE_WATCHLIST_SYMBOL, WatchlistParams(watchlist_id="watchlist2", symbol="GOOGL"), "/v1/watchlists/watchlist2/symbols/GOOGL"),
            (Endpoints.ADD_WATCHLIST_SYMBOL, WatchlistParams(watchlist_id="watchlist3", symbol="MSFT"), "/v1/watchlists/watchlist3/symbols/MSFT"),

            # Additional generic endpoint tests without specific parameters
            (Endpoints.GET_QUOTES, None, "/v1/markets/quotes"),
            (Endpoints.GET_HISTORICAL_PRICES, None, "/v1/markets/history"),
            (Endpoints.GET_OPTION_CHAINS, None, "/v1/markets/options/chains"),
            (Endpoints.CREATE_MARKET_SESSION, None, "/v1/markets/events/session"),
            (Endpoints.GET_CALENDAR, None, "/v1/markets/calendar")
        ]

 
        for endpoint, params, expected_path in test_cases:
            with self.subTest(endpoint=endpoint, params=params):
                # Mock response to return a JSON object
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"data": "test_data"}
                mock_request.return_value = mock_response

                # Call make_request with the endpoint and params
                result = self.api_controller.make_request(endpoint, path_params=params)

                # Verify the correct URL was constructed
                mock_request.assert_called_once_with(
                    method=endpoint.method,
                    url=f"{self.base_url}{expected_path}",
                    headers=self.api_controller.headers,
                    params={} if endpoint.method in ["GET", "DELETE"] else None,
                    data={} if endpoint.method in ["POST", "PUT"] else None
                )

                # Check the result to ensure it's as expected
                self.assertEqual(result, {"data": "test_data"})

                # Reset the mock for the next iteration
                mock_request.reset_mock()

    def test_format_path_parameter_count_mismatch(self):
        # Test cases where parameter count does not match expected
        mismatched_cases = [
            (Endpoints.GET_AN_ORDER, {"account_id": "12345678"}),  # Missing 'order_id'
            (Endpoints.GET_WATCHLIST, {}),  # Missing 'watchlist_id'
            (Endpoints.GET_BALANCES, {"account_id": "12345678", "extra_param": "test"}),  # Extra 'extra_param'
            (Endpoints.GET_POSITIONS, {"account_id": "87654321", "unexpected_param": "extra"}),  # Extra 'unexpected_param'
        ]

        for endpoint, params in mismatched_cases:
            with self.subTest(endpoint=endpoint, params=params):
                # Assert that a ValueError is raised when the parameter count doesn't match
                with self.assertRaises(ValueError):
                    endpoint.format_path(**params)