import sys
import os
import asyncio
from unittest.mock import patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import qwen_acp_mcp

def test_ws_call_success():
    """Test successful completion of ws_call."""
    async def mock_ws_call(method, params, timeout):
        return {"result": "success", "method": method, "params": params}

    with patch('qwen_acp_mcp._ws_call', side_effect=mock_ws_call):
        result = qwen_acp_mcp.ws_call("test_method", params={"key": "value"})
        assert result == {"result": "success", "method": "test_method", "params": {"key": "value"}}

def test_ws_call_exception():
    """Test that exceptions in _ws_call are caught and returned as a daemon_unreachable error."""
    async def mock_ws_call(method, params, timeout):
        raise ValueError("test error")

    with patch('qwen_acp_mcp._ws_call', side_effect=mock_ws_call):
        result = qwen_acp_mcp.ws_call("test_method")
        assert "error" in result
        assert result["error"]["code"] == "daemon_unreachable"
        assert result["error"]["message"] == "ValueError: test error"
        assert "optimus qwen serve" in result["error"]["hint"]

def test_ws_call_timeout():
    """Test that thread timeouts return a timeout error."""
    async def mock_ws_call(method, params, timeout):
        await asyncio.sleep(2.0)
        return {"result": "success"}

    # We mock _ws_call so it hangs, but wait, the timeout mechanism in ws_call
    # is `t.join(timeout + 10)`. To trigger the timeout without waiting 10+ seconds,
    # we patch thread join.
    def mock_join(*args, **kwargs):
        pass

    with patch('qwen_acp_mcp._ws_call', side_effect=mock_ws_call), \
         patch('threading.Thread.join', side_effect=mock_join):
        result = qwen_acp_mcp.ws_call("test_method", timeout=0.1)
        assert "error" in result
        assert result["error"]["code"] == "timeout"
        assert result["error"]["message"] == "test_method did not answer within 0.1s"

def test_ws_call_handles_none_params():
    """Test ws_call handles params=None by passing it through to _ws_call correctly."""
    async def mock_ws_call(method, params, timeout):
        return {"params_is_none": params is None}

    with patch('qwen_acp_mcp._ws_call', side_effect=mock_ws_call):
        result = qwen_acp_mcp.ws_call("test_method")
        assert result == {"params_is_none": True}
