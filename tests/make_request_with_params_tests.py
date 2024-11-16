import unittest
from unittest.mock import patch, MagicMock
from tradier_api import TradierApiController, Endpoints, AccountParams, OrderParams, \
                        WatchlistParams

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