import sys
import os
from pathlib import Path

# Add project root to sys.path so we can import minimax_hermes_bridge
sys.path.insert(0, str(Path(__file__).parent.parent))

from minimax_hermes_bridge import HermesBridge, PY_EXE, HERMES_ROOT
from minimax_bridge_core import Check
import unittest
from unittest.mock import patch, MagicMock

class TestHSync(unittest.TestCase):
    def test_h_sync_success(self):
        bridge = HermesBridge()

        # Mock run to capture the call and return a dummy output
        with patch('minimax_hermes_bridge.run') as mock_run:
            mock_run.return_value = (0, "SYNCED True", "")

            result = bridge.h_sync({})

            self.assertIsInstance(result, Check)
            self.assertEqual(result.id, "hermes.venv_sync")
            self.assertEqual(result.severity, "ok")
            self.assertIn("venv synced", result.title)
            self.assertEqual(result.detail, "SYNCED True")

            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args

            command = args[0]
            self.assertEqual(command[0], PY_EXE)
            self.assertEqual(command[1], "-I")
            self.assertEqual(command[2], "-B")
            self.assertEqual(command[3], "-c")

            code = command[4]
            self.assertIn("from hermes_cli import plugin_manager as pm", code)
            self.assertIn(f"r=pm.sync_venv(set(), explicit=True, project_root=r'{HERMES_ROOT}', evict_incompatible_plugins=True)", code)

            self.assertEqual(kwargs['timeout'], 900)

    def test_h_sync_failure_stdout(self):
        bridge = HermesBridge()

        with patch('minimax_hermes_bridge.run') as mock_run:
            mock_run.return_value = (1, "SYNCED False", "")

            result = bridge.h_sync({})

            self.assertIsInstance(result, Check)
            self.assertEqual(result.id, "hermes.venv_sync")
            self.assertEqual(result.severity, "fail")
            self.assertEqual(result.title, "sync failed")
            self.assertEqual(result.detail, "SYNCED False")

    def test_h_sync_failure_stderr(self):
        bridge = HermesBridge()

        with patch('minimax_hermes_bridge.run') as mock_run:
            mock_run.return_value = (1, "", "Error syncing venv")

            result = bridge.h_sync({})

            self.assertIsInstance(result, Check)
            self.assertEqual(result.id, "hermes.venv_sync")
            self.assertEqual(result.severity, "fail")
            self.assertEqual(result.title, "sync failed")
            self.assertEqual(result.detail, "Error syncing venv")
