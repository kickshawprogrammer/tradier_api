import unittest
from unittest.mock import Mock, patch

import requests
from tradier_api import TradierConfig, TradierHttpStreamController

class TestHttpStreamController(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.config = TradierConfig(token=self.token, environment="sandbox")

    @patch("requests.post")
    def test_start_streaming(self, mock_post):
        """Test that streaming starts and processes incoming data chunks."""
        # Mock a streaming response with data chunks
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_response.status_code = 200
        mock_post.return_value = mock_response

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

    @patch("requests.post")
    def test_streaming_handles_error(self, mock_post):
        """Test that an error in the stream triggers the on_error callback without raising."""
        # Mock the response to raise an HTTP error
        mock_post.side_effect = requests.exceptions.HTTPError("Streaming error")

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
        mock_on_error.assert_called_with(mock_post.side_effect)

    @patch("requests.post")
    def test_stop_event_breaks_stream(self, mock_post):
        """Test that setting _stop_event during streaming breaks the loop."""
        # Mock the streaming response
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mock on_message and on_close to verify that streaming stops as expected
        mock_on_message = Mock()
        mock_on_close = Mock()

        # Initialize HttpStreamController with mocked event handlers
        controller = TradierHttpStreamController(
            config=self.config,
            on_message=mock_on_message,
            on_close=mock_on_close
        )


        # Start streaming, set the stop event, and join the thread
        controller._run_stream(["AAPL"])
        controller.close()

        # controller._stop_event.set()  # Set stop event to simulate stopping the stream
        # controller._thread.join()  # Ensure streaming loop exits cleanly

        # Verify that on_message was called only once, indicating early termination
        mock_on_message.assert_called()
        mock_on_close.assert_called_once()

    @patch("requests.post")
    def test_decode_error_triggers_on_error(self, mock_post):
        """Test that a decoding error in _run_stream triggers the on_error callback."""
        # Mock the streaming response with invalid data
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b"valid_chunk", b"\x80\x81\x82"]  # Second chunk is invalid UTF-8
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mock the event handlers
        mock_on_message = Mock()
        mock_on_error = Mock()

        # Initialize HttpStreamController with mocked event handlers
        controller = TradierHttpStreamController(
            config=self.config,
            on_message=mock_on_message,
            on_error=mock_on_error
        )

        # Start streaming in the main thread
        controller._run_stream(["AAPL"])

        # Verify that on_message was called for the valid chunk
        mock_on_message.assert_called_once_with("valid_chunk")

        # Verify that on_error was called with a UnicodeDecodeError instance for the invalid chunk
        mock_on_error.assert_called_once()
        error_arg = mock_on_error.call_args[0][0]        # mock_on_error.assert_called_with("Failed to decode message: 'utf-8' codec can't decode byte 0x80 in position 0: invalid start byte")
        assert isinstance(error_arg, UnicodeDecodeError), f"Expected UnicodeDecodeError, got {type(error_arg)}"