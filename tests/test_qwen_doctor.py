import sys
import json
import pytest
from unittest.mock import MagicMock, patch

# Mock mcp.server.fastmcp before importing the script
class MockFastMCP:
    def __init__(self, name):
        self.name = name

    def tool(self):
        def decorator(func):
            return func
        return decorator

    def run(self):
        pass

mock_fastmcp_module = MagicMock()
mock_fastmcp_module.FastMCP = MockFastMCP
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = mock_fastmcp_module

import scripts.qwen_acp_mcp as qm

def test_qwen_doctor_all_ok():
    """Test when ACP transport, session and model provider are all ok."""
    with patch('scripts.qwen_acp_mcp.AcpSession') as mock_session_cls:
        mock_session = mock_session_cls.return_value
        mock_session.session_id = "test-session-123"
        mock_session.models = {
            "currentModelId": "test-model",
            "availableModels": [{"modelId": "test-model"}, {"modelId": "other-model"}]
        }
        mock_session.prompt.return_value = "QWEN-ACP-OK"

        result_json = qm.qwen_doctor()
        result = json.loads(result_json)

        assert result["acp_transport"] == "ok"
        assert result["session"] == "ok"
        assert result["model_provider"] == "ok"
        assert result["session_id"] == "test-session-123"
        assert result["current_model"] == "test-model"
        assert result["available_models"] == ["test-model", "other-model"]
        assert len(result["findings"]) == 0

def test_qwen_doctor_prompt_fails():
    """Test when prompt fails, meaning model provider is unreachable."""
    with patch('scripts.qwen_acp_mcp.AcpSession') as mock_session_cls:
        mock_session = mock_session_cls.return_value
        mock_session.session_id = "test-session-123"
        mock_session.models = {
            "currentModelId": "test-model",
            "availableModels": [{"modelId": "test-model"}]
        }
        mock_session.prompt.side_effect = Exception("Connection error.")

        result_json = qm.qwen_doctor()
        result = json.loads(result_json)

        assert result["acp_transport"] == "ok"
        assert result["session"] == "ok"
        assert result["model_provider"] == "unreachable"
        assert len(result["findings"]) == 1
        assert "session/prompt failed" in result["findings"][0]
        assert "LOCAL Ollama endpoint" in result["findings"][0]

def test_qwen_doctor_start_fails():
    """Test when start fails, meaning session creation failed."""
    with patch('scripts.qwen_acp_mcp.AcpSession') as mock_session_cls:
        mock_session = mock_session_cls.return_value
        mock_session.start.side_effect = Exception("Start failed")
        mock_session.stderr_tail = ["error 1", "error 2"]
        mock_session.session_id = "test-session-123"
        mock_session.models = {}

        result_json = qm.qwen_doctor()
        result = json.loads(result_json)

        assert result["acp_transport"] == "unknown"
        assert result["session"] == "failed"
        assert result["model_provider"] == "unknown"
        assert len(result["findings"]) == 1
        assert "ACP session creation failed" in result["findings"][0]
        assert result["stderr"] == ["error 1", "error 2"]

def test_qwen_doctor_closes_session():
    """Test to ensure session is always closed."""
    with patch('scripts.qwen_acp_mcp.AcpSession') as mock_session_cls:
        mock_session = mock_session_cls.return_value
        mock_session.session_id = "test-session-123"
        mock_session.models = {
            "currentModelId": "test-model",
            "availableModels": [{"modelId": "test-model"}]
        }
        mock_session.prompt.return_value = "QWEN-ACP-OK"

        qm.qwen_doctor()

        mock_session.close.assert_called_once()

    # Also verify it closes when an exception occurs
    with patch('scripts.qwen_acp_mcp.AcpSession') as mock_session_cls:
        mock_session = mock_session_cls.return_value
        mock_session.start.side_effect = Exception("Start failed")
        mock_session.stderr_tail = []

        qm.qwen_doctor()

        mock_session.close.assert_called_once()
