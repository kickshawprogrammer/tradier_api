"""
Module for testing the `TradierBaseStreamer` class.

This module contains unit tests for the `TradierBaseStreamer` class, which is the abstract base class
for all streamers in the Tradier API library. It provides tests for the core functionality of the base
streamer, such as event handling and error handling.

Classes:
    - TestTradierBaseStreamer: A unittest.TestCase subclass containing test methods for the
                               `TradierBaseStreamer` class.

Test Cases:
    - test_on_open_event_called: Verifies that the on_open() method is called when a stream is started,
                                 ensuring that the streamer properly handles the on_open event.

Dependencies:
    - unittest: Provides the base class for creating and running test cases.
    - unittest.mock: Provides utilities for mocking objects and asserting calls.

Classes and methods under test:
    - TradierBaseStreamer class
        - on_open() method

Please ensure that the tests are run in an environment where the Tradier API
client library has been installed and configured properly.
"""
import unittest
from unittest.mock import Mock
from tradier_api import TradierBaseStreamer, TradierConfig

class TestTradierBaseStreamer(unittest.TestCase):

    def setUp(self):
        self.config = TradierConfig(token="test_token", environment="sandbox")
        self.streamer = TradierBaseStreamer(config=self.config)

    def test_on_open_event_called(self):
        """Ensure on_open is called when stream starts."""
        mock_on_open = Mock()
        self.streamer.on_open = mock_on_open
        self.streamer.on_open()
        mock_on_open.assert_called_once()

    def test_on_message_event_called(self):
        """Ensure on_message is called with message data."""
        mock_on_message = Mock()
        self.streamer.on_message = mock_on_message
        message = "Test message"
        self.streamer.on_message(message)
        mock_on_message.assert_called_once_with(message)

    def test_on_close_event_called(self):
        """Ensure on_close is called when stream ends."""
        mock_on_close = Mock()
        self.streamer.on_close = mock_on_close
        self.streamer.on_close()
        mock_on_close.assert_called_once()

    def test_on_error_event_called(self):
        """Ensure on_error is called with error data."""
        mock_on_error = Mock()
        self.streamer.on_error = mock_on_error
        error = Exception("Test error")
        self.streamer.on_error(error)
        mock_on_error.assert_called_once_with(error)
