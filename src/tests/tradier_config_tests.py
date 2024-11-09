import unittest
from typing import Dict

from tradier_api import TradierConfig, APIEnv

class TestTradierConfig(unittest.TestCase):
    def setUp(self):
        self.token = "test_token"

    def test_default_environment(self):
        config = TradierConfig(token=self.token)
        self.assertEqual(config.environment, APIEnv.LIVE)
        self.assertEqual(config.token, self.token)
        self.assertIn("Authorization", config.headers)
        self.assertEqual(config.headers["Authorization"], f"Bearer {self.token}")

    def test_environment_string_input(self):
        config = TradierConfig(token=self.token, environment="sandbox")
        self.assertEqual(config.environment, APIEnv.SANDBOX)

    def test_environment_enum_input(self):
        config = TradierConfig(token=self.token, environment=APIEnv.PAPER)
        self.assertEqual(config.environment, APIEnv.SANDBOX)

    def test_invalid_environment(self):
        with self.assertRaises(ValueError):
            TradierConfig(token=self.token, environment="invalid")

    def test_accept_gzip_encoding(self):
        config = TradierConfig(token=self.token)
        self.assertIn("Accept-Encoding", config.headers)
        self.assertEqual(config.headers["Accept-Encoding"], "gzip")

        config.set_accept_gzip_encoding(False)
        self.assertNotIn("Accept-Encoding", config.headers)

    def test_accept_application_json(self):
        config = TradierConfig(token=self.token)
        self.assertEqual(config.headers["Accept"], "application/json")

    def test_accept_application_xml(self):
        config = TradierConfig(token=self.token)
        config.set_accept_application("xml")
        self.assertEqual(config.headers["Accept"], "application/xml")

    def test_invalid_accept_application(self):
        config = TradierConfig(token=self.token)
        with self.assertRaises(ValueError):
            config.set_accept_application("html")

    def test_headers_rebuild_on_change(self):
        config = TradierConfig(token=self.token)
        original_headers: Dict[str, str] = config.headers.copy()

        config.set_accept_gzip_encoding(False)
        config.set_accept_application("xml")
        
        self.assertNotEqual(config.headers, original_headers)
        self.assertNotIn("Accept-Encoding", config.headers)
        self.assertEqual(config.headers["Accept"], "application/xml")

    def test_invalid_type_environment(self):
        config = TradierConfig(token=self.token)
        with self.assertRaises(TypeError):
            config._validate_environment(123)  # type: ignore - intentionally passing an int to trigger TypeError
