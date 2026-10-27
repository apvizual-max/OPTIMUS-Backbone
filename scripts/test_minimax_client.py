import unittest
from unittest.mock import patch, mock_open
import json
import os
from minimax_client import credentials, HERMES_ENV, BASE_URL, DEFAULT_MODEL

class TestMinimaxClientCredentials(unittest.TestCase):
    @patch("minimax_client._read_dotenv")
    @patch.dict(os.environ, {"MINIMAX_API_KEY": "env_key"}, clear=True)
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"minimax": {"oauth": "token"}}))
    def test_api_key_in_env_and_oauth_present(self, mock_file, mock_read_dotenv):
        mock_read_dotenv.return_value = {}
        res = credentials()
        self.assertTrue(res["api_key_present"])
        self.assertEqual(res["api_key_source"], "MINIMAX_API_KEY env")
        self.assertTrue(res["oauth_present"])
        self.assertEqual(res["oauth_detail"], "found")

    @patch("minimax_client._read_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    @patch("builtins.open", side_effect=OSError("File not found"))
    def test_api_key_in_dotenv_and_oauth_missing(self, mock_file, mock_read_dotenv):
        mock_read_dotenv.return_value = {"MINIMAX_API_KEY": "dotenv_key"}
        res = credentials()
        self.assertTrue(res["api_key_present"])
        self.assertEqual(res["api_key_source"], f"{HERMES_ENV}")
        self.assertFalse(res["oauth_present"])
        self.assertEqual(res["oauth_detail"], "unreadable: OSError")

    @patch("minimax_client._read_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_no_api_key_and_invalid_oauth_json(self, mock_file, mock_read_dotenv):
        mock_read_dotenv.return_value = {}
        res = credentials()
        self.assertFalse(res["api_key_present"])
        self.assertIsNone(res["api_key_source"])
        self.assertFalse(res["oauth_present"])
        self.assertEqual(res["oauth_detail"], "unreadable: JSONDecodeError")

    @patch("minimax_client._read_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"other": "data"}))
    def test_no_minimax_oauth_entry(self, mock_file, mock_read_dotenv):
        mock_read_dotenv.return_value = {}
        res = credentials()
        self.assertFalse(res["oauth_present"])
        self.assertEqual(res["oauth_detail"], "no minimax oauth entry")

if __name__ == '__main__':
    unittest.main()
