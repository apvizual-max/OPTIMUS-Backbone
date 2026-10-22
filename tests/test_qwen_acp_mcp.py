import json
import pytest
from unittest.mock import patch, MagicMock

import sys
import os

# Ensure the scripts dir is in the sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from qwen_acp_mcp import qwen_auth_device_flow_start

def test_qwen_auth_device_flow_start_success():
    """Test the happy path where the device flow starts successfully."""
    # The actual structure expected from a successful call
    mock_response = {
        "result": {
            "verificationUri": "https://example.com/verify",
            "userCode": "ABCD-1234",
            "expiresIn": 900
        }
    }

    with patch('qwen_acp_mcp.ws_call', return_value=mock_response) as mock_ws_call:
        result_json = qwen_auth_device_flow_start()
        result = json.loads(result_json)

        mock_ws_call.assert_called_once_with("_qwen/workspace/auth/device_flow/start", {"providerId": "qwen-oauth"})
        assert result == mock_response

def test_qwen_auth_device_flow_start_stdio_error():
    """Test the edge case where the daemon answers with -32601 on the stdio transport."""
    mock_response = {
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }

    with patch('qwen_acp_mcp.ws_call', return_value=mock_response) as mock_ws_call:
        result_json = qwen_auth_device_flow_start()
        result = json.loads(result_json)

        mock_ws_call.assert_called_once_with("_qwen/workspace/auth/device_flow/start", {"providerId": "qwen-oauth"})

        assert result["ok"] is False
        assert "not available on the stdio" in result["error"]
