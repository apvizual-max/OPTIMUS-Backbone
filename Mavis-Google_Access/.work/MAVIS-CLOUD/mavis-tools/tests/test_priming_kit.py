import unittest
import subprocess
from unittest.mock import patch, MagicMock
import sys
import os
import importlib.util

spec = importlib.util.spec_from_file_location("priming_kit", os.path.join(os.path.dirname(__file__), '../priming-kit.py'))
priming_kit = importlib.util.module_from_spec(spec)
sys.modules["priming_kit"] = priming_kit
spec.loader.exec_module(priming_kit)

class TestPrimingKit(unittest.TestCase):

    @patch('subprocess.run')
    def test_git_state(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "output\n"
        mock_run.return_value = mock_result

        result = priming_kit.git_state()

        self.assertEqual(result, ("output", "output", "output"))
        mock_run.assert_any_call(
            ['git', 'rev-list', '--count', 'HEAD'],
            shell=False,
            cwd=priming_kit.REPO,
            capture_output=True,
            text=True,
            timeout=20
        )
        mock_run.assert_any_call(
            ['git', 'log', '--oneline', '-1'],
            shell=False,
            cwd=priming_kit.REPO,
            capture_output=True,
            text=True,
            timeout=20
        )
        mock_run.assert_any_call(
            ['git', 'remote', 'get-url', 'origin'],
            shell=False,
            cwd=priming_kit.REPO,
            capture_output=True,
            text=True,
            timeout=20
        )

if __name__ == '__main__':
    unittest.main()
