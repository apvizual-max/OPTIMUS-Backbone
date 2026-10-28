import unittest
from unittest.mock import patch
import sys
import os

# Add mavis-tools to path to import log
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import log

class TestLog(unittest.TestCase):
    @patch('subprocess.run')
    def test_head_mocked(self, mock_run):
        class MockResult:
            def __init__(self):
                self.stdout = "abcdef1\n"

        mock_run.return_value = MockResult()

        result = log._head()

        self.assertEqual(result, "abcdef1")
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args

        self.assertEqual(args[0], ['git', 'rev-parse', '--short', 'HEAD'])
        self.assertFalse(kwargs.get('shell'))
        self.assertTrue(kwargs.get('capture_output'))

    def test_head_real(self):
        result = log._head()
        self.assertTrue(isinstance(result, str))
        self.assertTrue(len(result) >= 7 or result == '-')

if __name__ == '__main__':
    unittest.main()
