import unittest
from unittest.mock import patch, MagicMock
import importlib.util
import os
import sys
import subprocess

# Load module dynamically
spec = importlib.util.spec_from_file_location("build_dashboard_legacy", os.path.join(os.path.dirname(__file__), "build-dashboard-legacy.py"))
build_dashboard = importlib.util.module_from_spec(spec)
sys.modules["build_dashboard_legacy"] = build_dashboard
spec.loader.exec_module(build_dashboard)

class TestBuildDashboardLegacy(unittest.TestCase):
    @patch('subprocess.run')
    def test_sh_success(self, mock_run):
        # Setup mock
        mock_result = MagicMock()
        mock_result.stdout = "  hello world  \n"
        mock_run.return_value = mock_result

        # Call function
        result = build_dashboard.sh(["echo", "hello"])

        # Verify
        self.assertEqual(result, "hello world")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["echo", "hello"])
        self.assertEqual(kwargs['capture_output'], True)
        self.assertEqual(kwargs['text'], True)

    @patch('subprocess.run')
    def test_sh_custom_args(self, mock_run):
        # Setup mock
        mock_result = MagicMock()
        mock_result.stdout = "test\n"
        mock_run.return_value = mock_result

        # Call function
        result = build_dashboard.sh(["ls", "-l"], cwd="/tmp", t=10)

        # Verify
        self.assertEqual(result, "test")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["ls", "-l"])
        self.assertEqual(kwargs['cwd'], "/tmp")
        self.assertEqual(kwargs['timeout'], 10)

    @patch('subprocess.run')
    def test_sh_exception(self, mock_run):
        # Setup mock to raise Exception
        mock_run.side_effect = Exception("Command failed")

        # Call function
        result = build_dashboard.sh(["echo", "hello"])

        # Verify
        self.assertEqual(result, "")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_sh_timeout(self, mock_run):
        # Setup mock to raise TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="echo hello", timeout=25)

        # Call function
        result = build_dashboard.sh(["echo", "hello"])

        # Verify
        self.assertEqual(result, "")
        mock_run.assert_called_once()


    def test_esc(self):
        self.assertEqual(build_dashboard.esc("plain text"), "plain text")
        self.assertEqual(build_dashboard.esc("a & b"), "a &amp; b")
        self.assertEqual(build_dashboard.esc("<tag>"), "&lt;tag&gt;")
        self.assertEqual(build_dashboard.esc("1 < 2 & 2 > 1"), "1 &lt; 2 &amp; 2 &gt; 1")
        self.assertEqual(build_dashboard.esc(123), "123")
        self.assertEqual(build_dashboard.esc(None), "None")
        self.assertEqual(build_dashboard.esc(""), "")

if __name__ == '__main__':
    unittest.main()
