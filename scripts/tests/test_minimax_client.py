import json
import sys
import argparse
from unittest.mock import patch, MagicMock
from io import StringIO

import pytest

# Adding parent dir to sys.path is often needed in these scripts if they aren't part of a package
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import minimax_client

class TestMain:

    @patch("minimax_client.credentials")
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_doctor(self, mock_stdout, mock_credentials):
        mock_credentials.return_value = {"api_key_present": True}

        with patch.object(sys, "argv", ["minimax_client.py", "doctor"]):
            result = minimax_client.main()

        assert result == 0
        mock_credentials.assert_called_once()
        assert json.loads(mock_stdout.getvalue()) == {"api_key_present": True}

    @patch("minimax_client.ask")
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_ask_success(self, mock_stdout, mock_ask):
        mock_ask.return_value = {"ok": True, "text": "This is a mocked response."}

        with patch.object(sys, "argv", ["minimax_client.py", "ask", "hello", "world"]):
            result = minimax_client.main()

        assert result == 0
        mock_ask.assert_called_once_with("hello world", model=None, max_tokens=1024)
        assert mock_stdout.getvalue().strip() == "This is a mocked response."

    @patch("minimax_client.ask")
    @patch("sys.stdout", new_callable=StringIO)
    def test_main_ask_stdin(self, mock_stdout, mock_ask):
        mock_ask.return_value = {"ok": True, "text": "Response from stdin prompt."}

        with patch.object(sys, "argv", ["minimax_client.py", "ask", "-"]):
            with patch("sys.stdin.read", return_value="hello from stdin\nmultiline"):
                result = minimax_client.main()

        assert result == 0
        mock_ask.assert_called_once_with("hello from stdin\nmultiline", model=None, max_tokens=1024)
        assert mock_stdout.getvalue().strip() == "Response from stdin prompt."

    @patch("sys.stderr", new_callable=StringIO)
    def test_main_ask_empty_prompt(self, mock_stderr):
        with patch.object(sys, "argv", ["minimax_client.py", "ask", "   "]):
            result = minimax_client.main()

        assert result == 2
        assert "error: ask needs a prompt" in mock_stderr.getvalue()

    @patch("minimax_client.ask")
    @patch("sys.stderr", new_callable=StringIO)
    def test_main_ask_failure(self, mock_stderr, mock_ask):
        mock_ask.return_value = {"ok": False, "error": "Something went wrong"}

        with patch.object(sys, "argv", ["minimax_client.py", "ask", "trigger error"]):
            result = minimax_client.main()

        assert result == 1
        mock_ask.assert_called_once_with("trigger error", model=None, max_tokens=1024)
        assert json.loads(mock_stderr.getvalue()) == {"ok": False, "error": "Something went wrong"}
