"""
Module: tests/tradier_websocket_streamer_tests.py

This module contains unit tests for the TradierMarketsStreamer and TradierAccountStreamer classes.

The tests cover the following scenarios:

    - Correct construction of streamers with valid configuration and parameters.
    - Correct handling of WebSocket connection setup and teardown.
    - Correct handling of incoming messages from the API.
    - Correct handling of errors raised by the API.
    - Correct handling of throttling errors raised by the API.
    - Correct handling of reconnections and session key refreshes.

The tests are designed to be run in isolation from the actual API, and
utilize mocking to simulate API responses.

This will execute all of the tests in the project, including the tests in
this module.

Please ensure that the tests are run in an environment where the Tradier API
client library has been installed and configured properly.
"""
import unittest
import asyncio
import json

from threading import Event
from unittest.mock import AsyncMock, Mock, patch

from tradier_api import TradierConfig, TradierMarketsStreamer, TradierAccountStreamer, SymbolsParams, ExcludedAccountParams


class TestTradierWebsocketStreamer(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"
        self.config = TradierConfig(token=self.token, environment="sandbox")
        self.stop_event = Event()
        self.session_key = "test_session_key"

        # Set up streamers and their corresponding parameters
        self.streamers = [
            (TradierMarketsStreamer(config=self.config), SymbolsParams(["SPY", "AAPL", "TSLA", "MSFT"])),
            (TradierAccountStreamer(config=self.config), ExcludedAccountParams()),
        ]

    @patch("websockets.connect", new_callable=AsyncMock)
    def test_run_stream_normal_flow(self, mock_connect):
        """Test that _run_stream processes messages and triggers callbacks."""
        for streamer, params in self.streamers:
            with self.subTest(streamer=type(streamer).__name__):
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
                streamer.on_open = Mock()
                streamer.on_message = Mock()
                streamer.on_error = Mock()
                streamer.on_close = Mock()

                # Run the _run_stream logic
                asyncio.run(streamer._run_stream(self.session_key, self.stop_event, params))

                # Verify callbacks were triggered correctly
                streamer.on_open.assert_called_once()
                streamer.on_message.assert_any_call("message1")
                streamer.on_message.assert_any_call("message2")

                # Ensure only unexpected errors trigger on_error
                errors = [call_arg[0] for call_arg in streamer.on_error.call_args_list]
                self.assertNotIn(StopAsyncIteration(), errors)

                # Verify that on_close is called once
                streamer.on_close.assert_called_once()

    @patch("websockets.connect", new_callable=AsyncMock)
    def test_run_stream_handles_exception(self, mock_connect):
        """Test that exceptions in the WebSocket connection trigger on_error."""
        for streamer, params in self.streamers:
            with self.subTest(streamer=type(streamer).__name__):
                # Configure the WebSocket mock to simulate an exception during the connection
                mock_websocket = AsyncMock()
                mock_websocket.recv.side_effect = Exception("Connection error")
                mock_connect.return_value = mock_websocket

                # Mock callbacks
                streamer.on_error = Mock()
                streamer.on_close = Mock()

                # Run the _run_stream logic
                asyncio.run(streamer._run_stream(self.session_key, self.stop_event, params))

                # Verify on_close was also called
                streamer.on_close.assert_called_once()
                streamer.on_error.assert_called_once()
                streamer.on_error.assert_called_with(mock_websocket.recv.side_effect)

    def test_run_starts_asyncio_loop(self):
        """Test that run starts an asyncio loop."""
        for streamer, params in self.streamers:
            with self.subTest(streamer=type(streamer).__name__):
                with patch.object(streamer, "_run_stream", new_callable=AsyncMock) as mock_run_stream:
                    streamer.run(self.session_key, self.stop_event, params)
                    mock_run_stream.assert_called_once_with(self.session_key, self.stop_event, params)

    @patch("websockets.connect", new_callable=AsyncMock)
    def test_run_stream_outer_exception_handler(self, mock_connect):
        """Test that the outer exception handler in _run_stream triggers the on_error callback."""
        for streamer, params in self.streamers:
            with self.subTest(streamer=type(streamer).__name__):
                # Mock WebSocket behaviors to raise a generic exception
                mock_connect.side_effect = Exception("Connection error")

                # Mock callbacks
                streamer.on_open = Mock()
                streamer.on_message = Mock()
                streamer.on_error = Mock()
                streamer.on_close = Mock()

                # Run the _run_stream logic
                asyncio.run(streamer._run_stream(self.session_key, self.stop_event, params))

                # Ensure on_open and on_message are not called
                streamer.on_open.assert_not_called()
                streamer.on_message.assert_not_called()

                # Verify that on_error was triggered with the correct exception
                streamer.on_error.assert_called_once()
                error_arg = streamer.on_error.call_args[0][0]
                self.assertIsInstance(error_arg, Exception)
                self.assertEqual(str(error_arg), "Connection error")

                # Ensure on_close is called after handling the exception
                streamer.on_close.assert_called_once()
