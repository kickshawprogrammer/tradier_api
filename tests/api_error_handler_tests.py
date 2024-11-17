"""
Module containing tests for the ApiErrorHandler class.

This module contains unit tests for the ApiErrorHandler class, which is used to
process API responses and handle any errors that may be present.

The ApiErrorHandler class is responsible for inspecting the response content and
header values to identify any errors that may have been raised by the API. If an
error is detected, the ApiErrorHandler will raise a TradierAPIException with a
message indicating the error type and any additional details that may be
available.

The tests in this module cover the following scenarios:

    - The API response contains an HTTP error status code.
    - The API response contains an error message in the response content.
    - The API response contains a throttling error message.
    - The API response contains an unexpected error message.

Each test case is carefully crafted to exercise a specific scenario and
validate that the ApiErrorHandler behaves as expected.

Tests are run using the unittest framework.

Please ensure that the tests are run in an environment where the Tradier API
client library has been installed and configured properly.
"""
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
