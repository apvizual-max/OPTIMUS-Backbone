import json
import pytest
import sys
from unittest.mock import patch, MagicMock

# Create mocks
mcp_mock = MagicMock()
mcp_mock.tool = MagicMock(return_value=lambda x: x)

mcp_server_mock = MagicMock()
fastmcp_mock = MagicMock()
fastmcp_class = MagicMock(return_value=mcp_mock)
fastmcp_mock.FastMCP = fastmcp_class
mcp_server_mock.fastmcp = fastmcp_mock

# Mock modules before importing the module under test
# This is still module-level but we use a more standard pattern for module mocking
# when the module under test does top-level imports of dependencies
sys.modules['mcp'] = mcp_mock
sys.modules['mcp.server'] = mcp_server_mock
sys.modules['mcp.server.fastmcp'] = fastmcp_mock
sys.modules['mcp.server.stdio'] = MagicMock()

from scripts.qwen_acp_mcp import qwen_auth_status, ws_call

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_auth_status_success(mock_ws_call):
    """Test successful case where both auth and providers return results."""
    def side_effect(method, *args, **kwargs):
        if method == "_qwen/workspace/auth/status":
            return {"result": {"logged_in": True}}
        elif method == "_qwen/workspace/providers":
            return {"result": ["provider1", "provider2"]}
        return {}

    mock_ws_call.side_effect = side_effect

    result_str = qwen_auth_status()
    result = json.loads(result_str)

    assert result["ok"] is True
    assert result["auth"] == {"logged_in": True}
    assert result["providers"] == ["provider1", "provider2"]
    assert "hint" not in result

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_auth_status_daemon_down(mock_ws_call):
    """Test case where daemon is completely unreachable (ws_call returns errors)."""
    def side_effect(method, *args, **kwargs):
        return {"error": {"code": "timeout", "message": "timeout"}}

    mock_ws_call.side_effect = side_effect

    result_str = qwen_auth_status()
    result = json.loads(result_str)

    # According to current code logic, out["auth"] and out["providers"] will not be None
    # (they will be the error objects), so out["ok"] will be True.
    # While it might seem unintuitive, this reflects the current code behavior.
    assert result["ok"] is True
    assert result["auth"] == {"code": "timeout", "message": "timeout"}
    assert result["providers"] == {"code": "timeout", "message": "timeout"}
    assert "hint" not in result

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_auth_status_empty_results(mock_ws_call):
    """Test case where both returns are completely empty (edge case)."""
    def side_effect(method, *args, **kwargs):
        return {}

    mock_ws_call.side_effect = side_effect

    result_str = qwen_auth_status()
    result = json.loads(result_str)

    assert result["ok"] is False
    assert result["auth"] is None
    assert result["providers"] is None
    assert "hint" in result

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_auth_status_partial_failure(mock_ws_call):
    """Test case where auth succeeds but providers fail."""
    def side_effect(method, *args, **kwargs):
        if method == "_qwen/workspace/auth/status":
            return {"result": {"logged_in": True}}
        elif method == "_qwen/workspace/providers":
            return {"error": {"code": -32601, "message": "Method not found"}}
        return {}

    mock_ws_call.side_effect = side_effect

    result_str = qwen_auth_status()
    result = json.loads(result_str)

    assert result["ok"] is True  # If at least one isn't None, ok is True
    assert result["auth"] == {"logged_in": True}
    assert result["providers"] == {"code": -32601, "message": "Method not found"}
    assert "hint" not in result
