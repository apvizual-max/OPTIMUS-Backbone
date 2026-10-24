import pytest
import sys
import os
from types import ModuleType

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.minimax_client import ask

# Create mock modules
mock_anthropic = ModuleType("anthropic")
sys.modules["anthropic"] = mock_anthropic

mock_httpx = ModuleType("httpx")
sys.modules["httpx"] = mock_httpx

def test_ask_no_api_key(monkeypatch):
    def mock_credentials():
        return {"api_key_present": False, "oauth_present": False}
    monkeypatch.setattr("scripts.minimax_client.credentials", mock_credentials)
    monkeypatch.setenv("MINIMAX_API_KEY", "")

    result = ask("hello")
    assert result["ok"] is False
    assert "no MINIMAX_API_KEY available" in result["error"]

def test_ask_with_anthropic_sdk(monkeypatch):
    def mock_credentials():
        return {
            "api_key_present": True,
            "anthropic_sdk": True,
            "httpx": False
        }
    monkeypatch.setattr("scripts.minimax_client.credentials", mock_credentials)
    monkeypatch.setenv("MINIMAX_API_KEY", "fake_key")

    class MockMessageResponse:
        def __init__(self):
            self.model = "MiniMax-M3"
            self.stop_reason = "end_turn"
            class TextBlock:
                type = "text"
                text = "mocked anthropic response"
            self.content = [TextBlock()]

    class MockMessages:
        def create(self, **kwargs):
            return MockMessageResponse()

    class MockClient:
        def __init__(self, api_key, base_url):
            self.messages = MockMessages()

    mock_anthropic.Anthropic = MockClient

    result = ask("hello")
    assert result["ok"] is True
    assert result["transport"] == "anthropic-sdk"
    assert result["text"] == "mocked anthropic response"

def test_ask_with_httpx_success(monkeypatch):
    def mock_credentials():
        return {
            "api_key_present": True,
            "anthropic_sdk": False,
            "httpx": True
        }
    monkeypatch.setattr("scripts.minimax_client.credentials", mock_credentials)
    monkeypatch.setenv("MINIMAX_API_KEY", "fake_key")

    class MockResponse:
        status_code = 200
        text = ""
        def json(self):
            return {
                "model": "MiniMax-M3",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "mocked httpx response"}]
            }

    def mock_post(*args, **kwargs):
        return MockResponse()

    mock_httpx.post = mock_post

    result = ask("hello", system="system prompt")
    assert result["ok"] is True
    assert result["transport"] == "httpx"
    assert result["text"] == "mocked httpx response"

def test_ask_with_httpx_error(monkeypatch):
    def mock_credentials():
        return {
            "api_key_present": True,
            "anthropic_sdk": False,
            "httpx": True
        }
    monkeypatch.setattr("scripts.minimax_client.credentials", mock_credentials)
    monkeypatch.setenv("MINIMAX_API_KEY", "fake_key")

    class MockResponse:
        status_code = 400
        text = "Bad Request error"

    def mock_post(*args, **kwargs):
        return MockResponse()

    mock_httpx.post = mock_post

    result = ask("hello")
    assert result["ok"] is False
    assert result["status"] == 400
    assert "Bad Request error" in result["error"]

def test_ask_neither_installed(monkeypatch):
    def mock_credentials():
        return {
            "api_key_present": True,
            "anthropic_sdk": False,
            "httpx": False
        }
    monkeypatch.setattr("scripts.minimax_client.credentials", mock_credentials)
    monkeypatch.setenv("MINIMAX_API_KEY", "fake_key")

    result = ask("hello")
    assert result["ok"] is False
    assert "neither the anthropic SDK nor httpx is installed" in result["error"]
