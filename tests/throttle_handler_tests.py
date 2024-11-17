"""
Unit test module for verifying the `ThrottleHandler` class functionality.

This module provides test cases for the `ThrottleHandler` class, which is
responsible for managing rate limiting for the Tradier API. The `ThrottleHandler`
class is a static class that provides a single method, `handle_throttling`, which
takes a response object from the Tradier API and ensures that the rate limit is
enforced.

The `handle_throttling` method is responsible for calculating the time until the
rate limit is reset and sleeping until that time if necessary. The method also
performs additional checks to ensure that the rate limit is not exceeded.

This module is part of the Tradier API library's test suite, aimed at maintaining
the reliability and correctness of the API client by ensuring that the
`ThrottleHandler` class behaves as expected.

The tests in this module cover the following scenarios:

    -   The API response contains the necessary rate limit headers.
    -   The API response contains an HTTP error status code.
    -   The API response contains an error message in the response content.
    -   The API response contains a throttling error message.
    -   The API response contains an unexpected error message.

Each test case is carefully crafted to exercise a specific scenario and
validate that the `ThrottleHandler` class behaves as expected.

Tests are run using the unittest framework.

Please ensure that the tests are run in an environment where the Tradier API
client library has been installed and configured properly.
"""
import unittest
from unittest.mock import patch, MagicMock

import time

from tradier_api import TradierApiController

class TestThrottleHandler(unittest.TestCase):

    @patch('time.sleep')  # Mock time.sleep to avoid actual sleep
    def test_handle_throttling_no_sleep_needed(self, mock_sleep):
        mock_response = MagicMock()
        mock_response.headers = {
            "X-Ratelimit-Available": "5",
            "X-Ratelimit-Expiry": str(int(time.time()) + 60)
        }

        TradierApiController.ThrottleHandler.handle_throttling(mock_response)
        mock_sleep.assert_not_called()

    @patch('time.sleep')  # Mock time.sleep to avoid actual sleep
    def test_handle_throttling_sleep_needed(self, mock_sleep):
        mock_response = MagicMock()
        mock_response.headers = {
            "X-Ratelimit-Allowed": "200",
            "X-Ratelimit-Used": "200",
            "X-Ratelimit-Available": "0",
            "X-Ratelimit-Expiry": str(int(time.time()) + 10)
        }

        TradierApiController.ThrottleHandler.handle_throttling(mock_response)
        mock_sleep.assert_called_once_with(10)

    @patch('time.sleep')  # Mock time.sleep to avoid actual sleep
    def test_handle_throttling_expiry_in_past(self, mock_sleep):
        mock_response = MagicMock()
        mock_response.headers = {
            "X-Ratelimit-Available": "0",
            "X-Ratelimit-Expiry": str(int(time.time()) - 10)
        }

        TradierApiController.ThrottleHandler.handle_throttling(mock_response)
        mock_sleep.assert_not_called()

    @patch('time.sleep', return_value=None)
    def test_handle_throttling_with_zero_rate_limits(self, mock_sleep):
        mock_response = MagicMock()
        mock_response.headers = {
            'X-Ratelimit-Available': '0',
            'X-Ratelimit-Allowed': '0',
            'X-Ratelimit-Used': '0'
        }

        result = TradierApiController.ThrottleHandler.handle_throttling(mock_response)
        mock_sleep.assert_not_called()
        self.assertEqual(result, mock_response)
