import pytest
from unittest.mock import patch
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared')))

from minimax_bridge_core import BridgeCore, Check
from minimax_hermes_bridge import HermesBridge

@pytest.fixture
def bridge():
    with patch.object(HermesBridge, '_register'):
        with patch.object(BridgeCore, '__init__', return_value=None):
            with patch.object(BridgeCore, 'audit'):
                with patch.object(BridgeCore, 'delegates'):
                    bridge = HermesBridge()
                    return bridge

def test_h_sync_success(bridge):
    with patch('minimax_hermes_bridge.run') as mock_run:
        mock_run.return_value = (0, "output text\n", "")

        result = bridge.h_sync({})

        assert isinstance(result, Check)
        assert result.id == "hermes.venv_sync"
        assert result.severity == "ok"
        assert result.title == "venv synced"
        assert result.detail == "output text"
        mock_run.assert_called_once()

        # Check that we run the right code
        args, kwargs = mock_run.call_args
        assert kwargs.get('timeout') == 900
        assert '-c' in args[0]
        assert 'pm.sync_venv' in args[0][-1]

def test_h_sync_failure(bridge):
    with patch('minimax_hermes_bridge.run') as mock_run:
        mock_run.return_value = (1, "output text", "error text")

        result = bridge.h_sync({})

        assert isinstance(result, Check)
        assert result.id == "hermes.venv_sync"
        assert result.severity == "fail"
        assert result.title == "sync failed"
        assert result.detail == "error text"
        mock_run.assert_called_once()

def test_h_sync_timeout_or_no_stderr(bridge):
    with patch('minimax_hermes_bridge.run') as mock_run:
        mock_run.return_value = (1, "only stdout output", "")

        result = bridge.h_sync({})

        assert isinstance(result, Check)
        assert result.id == "hermes.venv_sync"
        assert result.severity == "fail"
        assert result.title == "sync failed"
        assert result.detail == "only stdout output"
        mock_run.assert_called_once()
