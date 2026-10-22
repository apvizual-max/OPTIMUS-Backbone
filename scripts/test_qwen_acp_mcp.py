import pytest
from unittest.mock import Mock

from scripts.qwen_acp_mcp import AcpSession

def test_acp_session_close_proc_none():
    """Test close when proc is None does not raise exception."""
    session = AcpSession()
    session.proc = None
    session.close()  # Should not raise any exception

def test_acp_session_close_proc_exited():
    """Test close when proc has already exited."""
    session = AcpSession()
    mock_proc = Mock()
    mock_proc.poll.return_value = 0  # Process has exited
    session.proc = mock_proc

    session.close()
    mock_proc.kill.assert_not_called()

def test_acp_session_close_proc_running():
    """Test close when proc is still running calls kill."""
    session = AcpSession()
    mock_proc = Mock()
    mock_proc.poll.return_value = None  # Process is still running
    session.proc = mock_proc

    session.close()
    mock_proc.kill.assert_called_once()

def test_acp_session_close_proc_kill_exception():
    """Test close when kill raises an exception it is caught silently."""
    session = AcpSession()
    mock_proc = Mock()
    mock_proc.poll.return_value = None  # Process is still running
    mock_proc.kill.side_effect = Exception("Kill failed")
    session.proc = mock_proc

    session.close()  # Should not raise exception
    mock_proc.kill.assert_called_once()
