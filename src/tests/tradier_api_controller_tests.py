import unittest
from unittest.mock import patch, MagicMock

import requests

from tradier_api import TradierConfig, TradierApiController, TradierAPIException, Endpoints, APIEnv
from tradier_api._core_types import BaseURL

class TestTradierApiController(unittest.TestCase):

    def setUp(self):
        config = MagicMock()
        config.environment.value = "live"
        config.headers = {"Authorization": "Bearer test_token"}
        self.api_controller = TradierApiController(config)
        self.token = "test_token"

    @patch('requests.request')
    def test_make_request_successful(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "valid_data"}
        mock_request.return_value = mock_response

        result = self.api_controller.make_request(Endpoints.GET_QUOTES)
        self.assertEqual(result, {"data": "valid_data"})

    @patch('requests.request')
    def test_make_request_http_error(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_request.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
            self.api_controller.make_request(Endpoints.GET_QUOTES)

    @patch('requests.request')
    def test_make_request_api_specific_error(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": {"message": "API-specific error"}}
        mock_request.return_value = mock_response

        with self.assertRaises(TradierAPIException) as context:
            self.api_controller.make_request(Endpoints.GET_QUOTES)
        self.assertEqual(str(context.exception.message), "API-specific error")

    @patch('requests.request')
    def test_make_request_unexpected_exception(self, mock_request):
        # Simulate an unexpected exception, such as ValueError
        original_exception = ValueError("Unexpected error")
        mock_request.side_effect = original_exception

        with self.assertRaises(Exception) as context:
            self.api_controller.make_request(Endpoints.GET_QUOTES)

        # Verify the custom error message includes the base URL and the message of the original exception
        self.assertIn("Error making request to", str(context.exception))
        self.assertIn("Unexpected error", str(context.exception))

        # Confirm that the original exception is chained as the cause
        self.assertIs(context.exception.__cause__, original_exception)
        
    def test_api_env_base_url(self):
        """Test that each APIEnv setting configures the correct base URL."""
        test_cases = [
            (APIEnv.LIVE, BaseURL.API.value),
            (APIEnv.SANDBOX, BaseURL.SANDBOX.value),
            (APIEnv.STREAM, BaseURL.STREAM.value),
            (APIEnv.WEBSOCKET, BaseURL.WEBSOCKET.value),
            (APIEnv.PAPER, BaseURL.SANDBOX.value)
        ]
        
        for env_setting, expected_base_url in test_cases:
            with self.subTest(env_setting=env_setting):
                # Set up the config with each environment
                config = TradierConfig(token=self.token, environment=env_setting)
                
                # Initialize TradierBaseController with the given config
                controller = TradierApiController(config)
                
                # Assert the base URL matches the expected value
                self.assertEqual(controller.base_url, expected_base_url,
                                 f"Failed for environment {env_setting}")        
