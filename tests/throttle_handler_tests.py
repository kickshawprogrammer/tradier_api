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
