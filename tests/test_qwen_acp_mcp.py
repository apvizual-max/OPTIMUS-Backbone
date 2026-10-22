import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, './scripts')
from qwen_acp_mcp import AcpSession

class TestAcpSession(unittest.TestCase):
    @patch('qwen_acp_mcp.subprocess.Popen')
    def test_start_success(self, mock_popen):
        # Create a mock for the process
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        # Create our session
        session = AcpSession()

        # We need to mock _call so it doesn't actually try to write to stdin
        with patch.object(session, '_call') as mock_call:
            # We want _call to return different things for different calls
            def side_effect(method, params, timeout=None):
                if method == "initialize":
                    return {"id": 1, "jsonrpc": "2.0"}
                elif method == "session/new":
                    return {
                        "id": 2,
                        "jsonrpc": "2.0",
                        "result": {
                            "sessionId": "test-session-123",
                            "models": {"currentModelId": "test-model"}
                        }
                    }
                return {}

            mock_call.side_effect = side_effect

            # Run start
            session.start()

            # Assertions
            # Popen was called
            mock_popen.assert_called_once()

            # _call was called twice (initialize and session/new)
            self.assertEqual(mock_call.call_count, 2)

            # Important check: session/new was called with mcpServers: []
            # This is the specific fix mentioned in the file comments
            call_args_list = mock_call.call_args_list
            self.assertEqual(call_args_list[0][0][0], "initialize")

            self.assertEqual(call_args_list[1][0][0], "session/new")
            self.assertEqual(call_args_list[1][0][1]["mcpServers"], [])

            # State is updated
            self.assertEqual(session.session_id, "test-session-123")
            self.assertEqual(session.models, {"currentModelId": "test-model"})

    @patch('qwen_acp_mcp.subprocess.Popen')
    def test_start_error(self, mock_popen):
        # Create a mock for the process
        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        # Create our session
        session = AcpSession()

        # Mock _call to return an error for session/new
        with patch.object(session, '_call') as mock_call:
            def side_effect(method, params, timeout=None):
                if method == "initialize":
                    return {"id": 1, "jsonrpc": "2.0"}
                elif method == "session/new":
                    return {
                        "id": 2,
                        "jsonrpc": "2.0",
                        "error": {"code": 123, "message": "Test error"}
                    }
                return {}

            mock_call.side_effect = side_effect

            # start should raise RuntimeError
            with self.assertRaises(RuntimeError) as context:
                session.start()

            self.assertIn("session/new failed", str(context.exception))
