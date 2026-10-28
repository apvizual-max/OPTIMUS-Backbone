import unittest
import subprocess
from unittest.mock import patch, MagicMock
import sys
import os

# Import directly using runpy or importlib because SITE is a directory with a dash in file name
import importlib.util

spec = importlib.util.spec_from_file_location("build_dashboard_legacy", os.path.join(os.path.dirname(__file__), '../../SITE/build-dashboard-legacy.py'))
build_dashboard_legacy = importlib.util.module_from_spec(spec)
sys.modules["build_dashboard_legacy"] = build_dashboard_legacy
spec.loader.exec_module(build_dashboard_legacy)

class TestBuildDashboardLegacy(unittest.TestCase):

    @patch('subprocess.run')
    def test_sh_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "output \n"
        mock_run.return_value = mock_result

        result = build_dashboard_legacy.sh(['echo', 'output '])

        self.assertEqual(result, "output")
        mock_run.assert_called_once_with(
            ['echo', 'output '],
            shell=False,
            cwd=build_dashboard_legacy.REPO,
            capture_output=True,
            text=True,
            timeout=25
        )

    @patch('subprocess.run')
    def test_sh_exception(self, mock_run):
        mock_run.side_effect = Exception("Command failed")

        result = build_dashboard_legacy.sh(["failing_command"])

        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_sh_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep 10", timeout=25)

        result = build_dashboard_legacy.sh(["sleep", "10"])

        self.assertEqual(result, "")

if __name__ == '__main__':
    unittest.main()
