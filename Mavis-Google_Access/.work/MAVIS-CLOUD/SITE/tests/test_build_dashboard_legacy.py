import unittest
from unittest.mock import patch
import sys
import os

# Import using importlib to handle hyphens in the filename
import importlib.util
spec = importlib.util.spec_from_file_location("build_dashboard_legacy", os.path.join(os.path.dirname(__file__), '..', 'build-dashboard-legacy.py'))
bd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bd)


class TestBuildDashboardLegacy(unittest.TestCase):
    @patch('subprocess.run')
    def test_sh_exception_returns_empty_string(self, mock_run):
        # Configure mock to raise an exception
        mock_run.side_effect = Exception("Test Exception")

        # Call the function
        result = bd.sh(['some_command'])

        # Assert the result is an empty string
        self.assertEqual(result, '')
    def test_esc_basic_escaping(self):
        self.assertEqual(bd.esc('a & b < c > d'), 'a &amp; b &lt; c &gt; d')

    def test_esc_non_string(self):
        self.assertEqual(bd.esc(123), '123')

    def test_esc_empty_string(self):
        self.assertEqual(bd.esc(''), '')

    def test_esc_none(self):
        self.assertEqual(bd.esc(None), 'None')


    @patch('subprocess.run')
    def test_sh_success(self, mock_run):
        # Configure mock to return a successful result with whitespace
        mock_process = unittest.mock.Mock()
        mock_process.stdout = "   hello world \n "
        mock_run.return_value = mock_process

        result = bd.sh(['echo', 'hello'])

        self.assertEqual(result, 'hello world')
        mock_run.assert_called_once_with(['echo', 'hello'], shell=False, cwd=bd.REPO, capture_output=True, text=True, timeout=25)

    @patch('subprocess.run')
    def test_sh_custom_args(self, mock_run):
        # Configure mock
        mock_process = unittest.mock.Mock()
        mock_process.stdout = "custom output"
        mock_run.return_value = mock_process

        result = bd.sh(['ls', '-la'], cwd='/custom/dir', t=10)

        self.assertEqual(result, 'custom output')
        mock_run.assert_called_once_with(['ls', '-la'], shell=False, cwd='/custom/dir', capture_output=True, text=True, timeout=10)

if __name__ == '__main__':
    unittest.main()
