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

