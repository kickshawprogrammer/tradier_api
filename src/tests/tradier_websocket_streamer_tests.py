import unittest
import asyncio
import json

from threading import Event
from unittest.mock import AsyncMock, Mock, patch

from tradier_api import TradierConfig, TradierWebsocketStreamer

class TestTradierWebsocketStreamer(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.config = TradierConfig(token=self.token, environment="sandbox")
        self.stop_event = Event()
        self.symbols = ["SPY", "AAPL", "TSLA", "MSFT"]
        self.session_key = "test_session_key"

        # Create a test instance of the WebSocket streamer
        self.streamer = TradierWebsocketStreamer(config=self.config)

    @patch("websockets.connect", new_callable=AsyncMock)
    def test_run_stream_normal_flow(self, mock_connect):
        """Test that _run_stream processes messages and triggers callbacks."""
        # Mock WebSocket behaviors
        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = [
            "message1",
            "message2",
            asyncio.TimeoutError(),
            StopAsyncIteration(),
        ]
        mock_connect.return_value = mock_websocket

        # Mock callbacks
        self.streamer.on_open = Mock()
        self.streamer.on_message = Mock()
        self.streamer.on_error = Mock()
        self.streamer.on_close = Mock()

        # Run the _run_stream logic
        asyncio.run(self.streamer._run_stream("test_session_key", self.stop_event, self.symbols))

        # Verify callbacks were triggered correctly
        self.streamer.on_open.assert_called_once()
        self.streamer.on_message.assert_any_call("message1")
        self.streamer.on_message.assert_any_call("message2")

        # Ensure only unexpected errors trigger on_error
        errors = [call_arg[0] for call_arg in self.streamer.on_error.call_args_list]
        self.assertNotIn(StopAsyncIteration(), errors)

        # Verify that on_close is called once
        self.streamer.on_close.assert_called_once()

    @patch("websockets.connect", new_callable=AsyncMock)
    def test_run_stream_handles_exception(self, mock_connect):
        """Test that exceptions in the WebSocket connection trigger on_error."""
        # Configure the WebSocket mock to simulate an exception during the connection
        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = Exception("Connection error")
        mock_connect.return_value = mock_websocket  # Return the mock WebSocket directly

        # Mock callbacks
        self.streamer.on_error = Mock()
        self.streamer.on_close = Mock()

        # Run the _run_stream logic
        asyncio.run(self.streamer._run_stream("test_session_key", self.stop_event, self.symbols))

        # # Verify on_close was also called
        self.streamer.on_close.assert_called_once()
        self.streamer.on_error.assert_called_once()
        self.streamer.on_error.assert_called_with(mock_websocket.recv.side_effect)
        self.streamer.on_close.assert_called_once()

    def test_run_starts_asyncio_loop(self):
        """Test that run starts an asyncio loop."""
        with patch.object(self.streamer, "_run_stream", new_callable=AsyncMock) as mock_run_stream:
            self.streamer.run("test_session_key", self.stop_event, self.symbols)
            mock_run_stream.assert_called_once_with("test_session_key", self.stop_event, self.symbols)

    def test_stop_event_stops_streaming(self):
        """Test that setting the stop_event breaks the streaming loop."""
        self.stop_event.set()
        self.assertTrue(self.stop_event.is_set())

    @patch("websockets.connect", new_callable=AsyncMock)
    def test_run_stream_outer_exception_handler(self, mock_connect):
        """Test that the outer exception handler in _run_stream triggers the on_error callback."""
        # Mock WebSocket behaviors to raise a generic exception
        mock_connect.side_effect = Exception("Connection error")

        # Mock callbacks
        self.streamer.on_open = Mock()
        self.streamer.on_message = Mock()
        self.streamer.on_error = Mock()
        self.streamer.on_close = Mock()

        # Run the _run_stream logic
        asyncio.run(self.streamer._run_stream("test_session_key", self.stop_event, self.symbols))

        # Ensure on_open and on_message are not called
        self.streamer.on_open.assert_not_called()
        self.streamer.on_message.assert_not_called()

        # Verify that on_error was triggered with the correct exception
        self.streamer.on_error.assert_called_once()
        error_arg = self.streamer.on_error.call_args[0][0]
        assert isinstance(error_arg, Exception), f"Expected Exception, got {type(error_arg)}"
        self.assertEqual(str(error_arg), "Connection error")

        # Ensure on_close is called after handling the exception
        self.streamer.on_close.assert_called_once()

    def test_payload_with_list(self):
        """Ensure payload is correctly formatted when symbols is a list."""
        symbols = ["SPY", "AAPL", "TSLA", "MSFT"]

        payload = json.dumps({
            "symbols": symbols,
            "sessionid": self.session_key,
            "linebreak": True
        })

        parsed_payload = json.loads(payload)

        self.assertEqual(parsed_payload["symbols"], symbols)
        self.assertEqual(parsed_payload["sessionid"], self.session_key)
        self.assertTrue(parsed_payload["linebreak"])

    def test_payload_with_comma_separated_string(self):
        """Ensure payload is correctly formatted when symbols is a comma-separated string."""
        symbols = "SPY,AAPL,TSLA,MSFT"

        # Convert to list
        symbols_list = [s.strip() for s in symbols.split(",")]

        payload = json.dumps({
            "symbols": symbols_list,
            "sessionid": self.session_key,
            "linebreak": True
        })

        parsed_payload = json.loads(payload)

        self.assertEqual(parsed_payload["symbols"], ["SPY", "AAPL", "TSLA", "MSFT"])
        self.assertEqual(parsed_payload["sessionid"], self.session_key)
        self.assertTrue(parsed_payload["linebreak"])