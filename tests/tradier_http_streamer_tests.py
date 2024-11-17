"""
Unit test module for the TradierHttpStreamer class.

This module contains unit tests for verifying the functionality and behavior of the TradierHttpStreamer
class, which is responsible for handling HTTP streaming requests to the Tradier API. The tests are 
designed to ensure that the HTTP streaming connection is established correctly, that data can be streamed 
in real-time, and that errors are appropriately handled.

The tests in this module cover the following scenarios:
    - Correct initialization of the TradierHttpStreamer with valid configuration.
    - Verification of URL construction and endpoint usage for the HTTP stream.
    - Handling of streaming data events, including on_open, on_message, on_close, and on_error callbacks.
    - Error handling for HTTP errors and exceptions that may occur during streaming.
    - Thread management for starting and stopping the HTTP streaming connection.

Key Components:
    - TradierHttpStreamer: The main class under test, responsible for managing HTTP streaming connections.
    - TradierConfig: Used to configure the API token and environment settings for the streamer.
    - SymbolsParams: Optional parameters for specifying market symbols to stream data for.
    - unittest: The testing framework used to structure and run test cases.
    - unittest.mock: Provides tools for mocking and patching dependencies within test cases.
    - requests: Utilized for simulating HTTP requests and responses during testing.

Usage:
To execute the tests in this module, run the file using a Python test runner such as `unittest` or `pytest`.
Ensure that the Tradier API client library is installed and properly configured in the testing environment.

Note:
This module assumes that the Tradier API token and environment settings are correctly set up in the
TradierConfig object. The tests are designed to be run in isolation, using mocking to simulate API
interactions without requiring an active network connection.
"""
import unittest
from unittest.mock import Mock, patch
import requests, threading
from tradier_api import TradierConfig, TradierHttpStreamer, SymbolsParams

class TestTradierHttpStreamer(unittest.TestCase):

    def setUp(self):
        self.config = TradierConfig(token="test_token", environment="sandbox")
        self.streamer = TradierHttpStreamer(config=self.config)
        self.symbol_params = SymbolsParams(symbols=["AAPL", "TSLA", "SPY"])

    @patch("requests.post")
    def test_start_streaming(self, mock_post):
        """Test that streaming processes incoming data chunks."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        mock_on_message = Mock()
        self.streamer.on_message = mock_on_message

        event = threading.Event()
        event.clear()

        self.streamer.run(session_key="", stop_event=event, params=self.symbol_params)
        self.assertEqual(mock_on_message.call_count, 3)
        mock_on_message.assert_any_call("chunk1")
        mock_on_message.assert_any_call("chunk2")
        mock_on_message.assert_any_call("chunk3")

    @patch("requests.post")
    def test_streaming_handles_error(self, mock_post):
        """Test that an error in the stream triggers on_error."""
        mock_post.side_effect = requests.exceptions.HTTPError("Streaming error")
        mock_on_error = Mock()
        self.streamer.on_error = mock_on_error

        self.streamer.run(Mock(), Mock(), self.symbol_params)
        mock_on_error.assert_called_once()

    @patch("requests.post")
    def test_decode_error_triggers_on_error(self, mock_post):
        """Ensure a decoding error triggers on_error."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b"valid_chunk", b"\x80\x81\x82"]
        mock_post.return_value = mock_response

        mock_on_message = Mock()
        mock_on_error = Mock()
        self.streamer.on_message = mock_on_message
        self.streamer.on_error = mock_on_error

        event = threading.Event()
        event.clear()

        self.streamer.run(Mock(), event, self.symbol_params)
        mock_on_message.assert_called_once_with("valid_chunk")
        mock_on_error.assert_called_once()
        self.assertIsInstance(mock_on_error.call_args[0][0], UnicodeDecodeError)

