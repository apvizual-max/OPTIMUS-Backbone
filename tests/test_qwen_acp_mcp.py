import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add scripts directory to path to import qwen_acp_mcp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.qwen_acp_mcp import AcpSession, ACPPROMPT_TIMEOUT

def test_prompt_success():
    session = AcpSession()
    session.session_id = "test-session-id"

    # Mock the _call method
    session._call = MagicMock(return_value={
        "result": {
            "stopReason": "stop"
        }
    })

    result = session.prompt("hello")
    assert result == "stop"

    session._call.assert_called_once_with(
        "session/prompt",
        {
            "sessionId": "test-session-id",
            "prompt": [{"type": "text", "text": "hello"}]
        },
        timeout=ACPPROMPT_TIMEOUT
    )

def test_prompt_success_no_stop_reason():
    session = AcpSession()
    session.session_id = "test-session-id"

    # Mock the _call method returning empty stop reason
    session._call = MagicMock(return_value={
        "result": {}
    })

    result = session.prompt("hello")
    assert result == "ok"

def test_prompt_error():
    session = AcpSession()
    session.session_id = "test-session-id"

    # Mock the _call method returning an error
    session._call = MagicMock(return_value={
        "error": {
            "message": "Connection error",
            "data": {
                "details": "Model unreachable"
            }
        }
    })

    with pytest.raises(RuntimeError, match=r"prompt failed: Connection error \(Model unreachable\)"):
        session.prompt("hello")

def test_prompt_error_no_details():
    session = AcpSession()
    session.session_id = "test-session-id"

    # Mock the _call method returning an error without details
    session._call = MagicMock(return_value={
        "error": {
            "message": "Internal error"
        }
    })

    with pytest.raises(RuntimeError, match=r"prompt failed: Internal error"):
        session.prompt("hello")
