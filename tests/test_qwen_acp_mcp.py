import json
import pytest
from unittest.mock import patch, MagicMock

# Create a dummy decorator that doesn't alter the function
class DummyFastMCP:
    def __init__(self, name):
        self.name = name
    def tool(self):
        def decorator(func):
            return func
        return decorator
    def run(self):
        pass

import sys
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.server'] = MagicMock()
sys.modules['mcp.server.fastmcp'] = MagicMock()
sys.modules['mcp.server.fastmcp'].FastMCP = DummyFastMCP

# Now we can safely import the module under test
import scripts.qwen_acp_mcp as qwen_acp_mcp

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_workspace_tools_success(mock_ws_call):
    # Setup mock return value for a successful call
    mock_ws_call.return_value = {
        "result": {
            "tools": ["tool1", "tool2"],
            "capabilities": ["cap1"]
        }
    }

    # Call the function
    result_str = qwen_acp_mcp.qwen_workspace_tools()

    # Assert
    assert mock_ws_call.called
    assert mock_ws_call.call_args[0][0] == "_qwen/workspace/tools"

    result = json.loads(result_str)
    assert result["tools"] == ["tool1", "tool2"]
    assert result["capabilities"] == ["cap1"]

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_workspace_tools_stdio_error(mock_ws_call):
    # Setup mock return value for the -32601 error (method not found on stdio)
    mock_ws_call.return_value = {
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }

    # Call the function
    result_str = qwen_acp_mcp.qwen_workspace_tools()

    # Assert
    result = json.loads(result_str)
    assert result["ok"] is False
    assert "_qwen/* is not available on the stdio transport" in result["error"]

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_workspace_tools_other_error(mock_ws_call):
    # Setup mock return value for a different error
    mock_ws_call.return_value = {
        "error": {
            "code": -32000,
            "message": "Some other error"
        }
    }

    # Call the function
    result_str = qwen_acp_mcp.qwen_workspace_tools()

    # Assert
    # It should fall through to the default return
    result = json.loads(result_str)
    assert "error" in result
    assert result["error"]["code"] == -32000
    assert result["error"]["message"] == "Some other error"

@patch('scripts.qwen_acp_mcp.ws_call')
def test_qwen_workspace_tools_no_result(mock_ws_call):
    # Setup mock return value for a response with no result (but not a -32601 error)
    mock_ws_call.return_value = {
        "id": 1,
        "jsonrpc": "2.0"
    }

    # Call the function
    result_str = qwen_acp_mcp.qwen_workspace_tools()

    # Assert
    # It should fall through and return the whole response object
    result = json.loads(result_str)
    assert "id" in result
    assert result["id"] == 1
