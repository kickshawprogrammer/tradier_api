import unittest
from unittest.mock import Mock, patch

import requests
from tradier_api import TradierConfig, TradierHttpStreamController

class TestHttpStreamController(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.config = TradierConfig(token=self.token, environment="sandbox")

    @patch("requests.get")
    @patch("tradier_api.TradierStreamController.ApiErrorHandler.handle_errors")
    @patch("tradier_api.TradierStreamController.ThrottleHandler.handle_throttling")
    def test_start_streaming(self, mock_throttle, mock_error_handler, mock_get):
        """Test that streaming starts and processes incoming data chunks."""
        # Mock a streaming response with data chunks
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Configure the error handler and throttle handler to return mock_response
        mock_error_handler.return_value = mock_response
        mock_throttle.return_value = mock_response

        # Mock the event handlers
        mock_on_message = Mock()
        mock_on_close = Mock()

        # Initialize HttpStreamController with mocked event handlers
        controller = TradierHttpStreamController(
            config=self.config,
            on_message=mock_on_message,
            on_close=mock_on_close
        )

        # Start the stream (directly call _run_stream for testing without threading)
        controller._run_stream(["AAPL"])

        # Check that on_message was called for each chunk
        self.assertEqual(mock_on_message.call_count, 3)
        mock_on_message.assert_any_call("chunk1")
        mock_on_message.assert_any_call("chunk2")
        mock_on_message.assert_any_call("chunk3")

        # Ensure on_close was called once after streaming
        mock_on_close.assert_called_once()
            
    @patch("tradier_api.TradierApiController.make_request")
    def test_stop_streaming(self, mock_get):
        """Test that streaming can be stopped and triggers on_close."""
        # Mock a streaming response
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Mock the event handlers
        mock_on_message = Mock()
        mock_on_close = Mock()

        # Initialize HttpStreamController with mocked event handlers
        controller = TradierHttpStreamController(
            config=self.config,
            on_message=mock_on_message,
            on_close=mock_on_close
        )

        # Start streaming and then immediately stop it
        controller.start(["AAPL"])
        controller.close()

        # Ensure that the on_close event handler was called
        mock_on_close.assert_called_once()

    @patch("requests.get")
    def test_streaming_handles_error(self, mock_get):
        """Test that an error in the stream triggers the on_error callback without raising."""
        # Mock the response to raise an HTTP error
        mock_get.side_effect = requests.exceptions.HTTPError("Streaming error")

        # Mock the on_error event handler
        mock_on_error = Mock()

        # Initialize HttpStreamController with the mocked on_error handler
        controller = TradierHttpStreamController(
            config=self.config,
            on_error=mock_on_error
        )

        # Attempt to start the stream, expecting it to handle the error internally
        controller._run_stream(["AAPL"])

        # Verify that on_error was called with the expected error
        mock_on_error.assert_called_once()
        mock_on_error.assert_called_with(mock_get.side_effect)


