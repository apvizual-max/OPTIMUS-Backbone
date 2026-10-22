import json
import unittest
from unittest.mock import patch, MagicMock

import qwen_acp_mcp
from qwen_acp_mcp import qwen_session_probe, AcpSession

class TestQwenSessionProbe(unittest.TestCase):

    @patch('qwen_acp_mcp.AcpSession')
    def test_qwen_session_probe(self, MockAcpSession):
        # Arrange
        mock_session = MagicMock()
        mock_session.session_id = "test_session_id"
        mock_session.models = {"currentModelId": "test_model"}
        MockAcpSession.return_value = mock_session

        # Act
        result_json_str = qwen_session_probe()
        result = json.loads(result_json_str)

        # Assert
        self.assertTrue(result["ok"])
        self.assertEqual(result["session_id"], "test_session_id")
        self.assertEqual(result["models"], {"currentModelId": "test_model"})

        mock_session.start.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('qwen_acp_mcp.AcpSession')
    def test_qwen_session_probe_error(self, MockAcpSession):
        # Arrange
        mock_session = MagicMock()
        mock_session.start.side_effect = Exception("Test error")
        MockAcpSession.return_value = mock_session

        # Act & Assert
        with self.assertRaises(Exception) as context:
            qwen_session_probe()

        self.assertTrue("Test error" in str(context.exception))
        mock_session.start.assert_called_once()
        mock_session.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
