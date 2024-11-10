import unittest
from unittest.mock import Mock, patch, MagicMock
from tradier_api import TradierConfig, TradierStreamController

class TestTradierStreamController(unittest.TestCase):

    class TestableTradierStreamController(TradierStreamController):
        def __init__(self, config, on_open=None, on_message=None, on_close=None, on_error=None):
            super().__init__(config, on_open, on_message, on_close, on_error)
            self.session_key = "test_session_key"

        def start(self):
            pass  # Implement a no-op start method for testing

        def close(self):
            pass  # Implement a no-op close method for testing

    def setUp(self):
        self.token = "test_token"
        self.config = TradierConfig(token=self.token, environment="sandbox")
        self.controller = self.TestableTradierStreamController(config=self.config)

    def test_on_open_callback(self):
        """Test that on_open callback is invoked if provided."""
        mock_on_open = Mock()
        controller = self.TestableTradierStreamController(config=self.config, on_open=mock_on_open)
        controller._do_on_open()
        mock_on_open.assert_called_once()

    def test_on_open_default(self):
        """Test the default message for on_open if no callback is provided."""
        controller = self.TestableTradierStreamController(config=self.config)
        with patch("builtins.print") as mock_print:
            controller._do_on_open()
            mock_print.assert_called_once_with("Stream opened.")

    def test_on_message_callback(self):
        """Test that on_message callback is invoked with the correct message."""
        mock_on_message = Mock()
        controller = self.TestableTradierStreamController(config=self.config, on_message=mock_on_message)
        test_message = "Test message"
        controller._do_on_message(test_message)
        mock_on_message.assert_called_once_with(test_message)

    def test_on_message_default(self):
        """Test the default message for on_message if no callback is provided."""
        controller = self.TestableTradierStreamController(config=self.config)
        test_message = "Test message"
        with patch("builtins.print") as mock_print:
            controller._do_on_message(test_message)
            mock_print.assert_called_once_with("Received message:", test_message)

    def test_on_close_callback(self):
        """Test that on_close callback is invoked if provided."""
        mock_on_close = Mock()
        controller = self.TestableTradierStreamController(config=self.config, on_close=mock_on_close)
        controller._do_on_close()
        mock_on_close.assert_called_once()

    def test_on_close_default(self):
        """Test the default message for on_close if no callback is provided."""
        controller = self.TestableTradierStreamController(config=self.config)
        with patch("builtins.print") as mock_print:
            controller._do_on_close()
            mock_print.assert_called_once_with("Stream closed.")

    def test_on_error_callback(self):
        """Test that on_error callback is invoked with the correct error."""
        mock_on_error = Mock()
        controller = self.TestableTradierStreamController(config=self.config, on_error=mock_on_error)
        test_error = Exception("Test error")
        controller._do_on_error(test_error)
        mock_on_error.assert_called_once_with(test_error)

    def test_on_error_default(self):
        """Test the default message for on_error if no callback is provided."""
        controller = self.TestableTradierStreamController(config=self.config)
        test_error = Exception("Test error")
        with patch("builtins.print") as mock_print:
            controller._do_on_error(test_error)
            mock_print.assert_called_once_with("Stream error:", test_error)

    @patch("tradier_api.TradierApiController.make_request")
    def test_create_session(self, mock_get):
        """Test create_session with a mocked API response."""
        # Mock the response object from requests.get
        mock_response = Mock()
        mock_response.json.return_value = {"stream":{"sessionid": "mock_session_key"}}
        mock_get.return_value = mock_response

        # Run create_session and verify the session_key is set
        self.controller.create_session()
        self.assertEqual(self.controller.session_key, "mock_session_key")
        mock_get.assert_called_once()  # Verify requests.get was called

    @patch("tradier_api.TradierApiController.make_request")
    def test_create_session_failed_to_create_session_key(self, mock_get):
        """Test that session_key remains None if create_session is not set with a value."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        with self.assertRaises(Exception):
            self.controller.create_session()