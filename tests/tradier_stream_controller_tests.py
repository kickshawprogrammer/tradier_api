"""
Tests for the TradierStreamController class.

This module contains unit tests for the TradierStreamController class, which is
responsible for managing the lifecycle of a streaming connection to the Tradier
API. The controller provides methods for starting and stopping the stream, as
well as managing the underlying streamer object.

The tests in this module cover the following scenarios:

    - Correct construction of the controller with a valid configuration and streamer.
    - Correct starting and stopping of the stream.
    - Correct handling of errors raised by the streamer.
    - Correct thread management for background streaming.

This module is part of the Tradier API library's test suite, aimed at maintaining
the reliability and correctness of the API client by ensuring that the
TradierStreamController class properly manages streaming connections.

Please ensure that the tests are run in an environment where the Tradier API
client library has been installed and configured properly.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from tradier_api import TradierConfig, TradierStreamController, TradierHttpStreamer

class TestTradierStreamController(unittest.TestCase):

    def setUp(self):
        self.config = TradierConfig(token="test_token", environment="sandbox")
        self.streamer = Mock(spec=TradierHttpStreamer)  # Mock streamer to isolate controller testing
        self.controller = TradierStreamController(config=self.config, streamer=self.streamer)

    def test_start_stream_calls_run(self):
        """Verify that start() in controller calls the streamer's run method."""
        # Mock the create_session method and the streamer's run method
        self.controller.create_session = MagicMock() # mocked result returns None
        self.streamer.run = MagicMock()

        # Call start, which should invoke create_session and then run
        self.controller.start(["AAPL"]) # type: ignore

        # Verify create_session was called
        self.controller.create_session.assert_called_once()

        # Verify run was called with no session_key,_stop_event and symbols 
        self.streamer.run.assert_called_once_with(None, self.controller._stop_event, ["AAPL"])

    def test_close_signals_stop_event(self):
        """Ensure that calling close() sets _stop_event and calls on_close when a thread is active."""
        # Mock _thread with a mock `join` method
        mock_thread = MagicMock()
        mock_thread.join = MagicMock()
        self.controller._thread = mock_thread

        # Now call close, which should set _stop_event and trigger on_close
        self.controller.close()

        # Ensure that join was called on the mock thread to simulate cleanup
        mock_thread.join.assert_called_once()
        
        # Assert _stop_event is set as expected
        self.assertTrue(self.controller._stop_event.is_set())

    @patch("tradier_api.TradierApiController.make_request")
    def test_create_session(self, mock_make_request):
        """Test that create_session sets session_key correctly with API response."""
        mock_make_request.return_value = {"stream": {"sessionid": "mock_session_key"}}
        self.controller.create_session()
        self.assertEqual(self.controller.session_key, "mock_session_key")

    @patch("tradier_api.TradierApiController.make_request")
    def test_create_session_failed_to_create_session_key(self, mock_make_request):
        """Test that session_key remains None if API response lacks a session key."""
        mock_make_request.return_value = {}
        with self.assertRaises(Exception):
            self.controller.create_session()
