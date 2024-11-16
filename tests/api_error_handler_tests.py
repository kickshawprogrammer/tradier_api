import unittest
from unittest.mock import MagicMock

import requests
from tradier_api import TradierApiController, TradierAPIException

class TestApiErrorHandler(unittest.TestCase):

    def test_handle_errors_with_http_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")

        with self.assertRaises(requests.exceptions.HTTPError):
            TradierApiController.ApiErrorHandler.handle_errors(mock_response)

    def test_handle_errors_with_api_specific_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": {"message": "API-specific error"}}

        with self.assertRaises(TradierAPIException) as context:
            TradierApiController.ApiErrorHandler.handle_errors(mock_response)
        self.assertEqual(str(context.exception.message), "API-specific error")

    def test_handle_errors_no_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "valid_data"}

        result = TradierApiController.ApiErrorHandler.handle_errors(mock_response)
        self.assertEqual(result, mock_response)
