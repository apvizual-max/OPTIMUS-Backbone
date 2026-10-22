import json
import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.qwen_acp_mcp import qwen_prompt, AcpSession

@patch('scripts.qwen_acp_mcp.AcpSession')
def test_qwen_prompt_success(mock_acp_session_class):
    mock_session = MagicMock()
    mock_session.session_id = "test-session-123"
    mock_session.models = {"currentModelId": "test-model"}
    mock_session.prompt.return_value = "Hello world!"
    mock_acp_session_class.return_value = mock_session

    result = qwen_prompt("test prompt", 10.0)
    result_dict = json.loads(result)

    assert result_dict["ok"] is True
    assert result_dict["session"] == "test-session-123"
    assert result_dict["model"] == "test-model"
    assert result_dict["stop_reason"] == "Hello world!"

    mock_session.start.assert_called_once()
    mock_session.prompt.assert_called_once_with("test prompt", timeout=10.0)
    mock_session.close.assert_called_once()

@patch('scripts.qwen_acp_mcp.AcpSession')
def test_qwen_prompt_start_fails(mock_acp_session_class):
    mock_session = MagicMock()
    mock_session.start.side_effect = Exception("Start failed")
    mock_acp_session_class.return_value = mock_session

    with pytest.raises(Exception, match="Start failed"):
        qwen_prompt("test prompt")

    mock_session.start.assert_called_once()
    mock_session.prompt.assert_not_called()
    mock_session.close.assert_called_once()

@patch('scripts.qwen_acp_mcp.AcpSession')
def test_qwen_prompt_prompt_fails(mock_acp_session_class):
    mock_session = MagicMock()
    mock_session.prompt.side_effect = Exception("Prompt failed")
    mock_acp_session_class.return_value = mock_session

    with pytest.raises(Exception, match="Prompt failed"):
        qwen_prompt("test prompt")

    mock_session.start.assert_called_once()
    mock_session.prompt.assert_called_once()
    mock_session.close.assert_called_once()
