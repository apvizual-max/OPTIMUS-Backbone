import unittest
from unittest.mock import patch, mock_open, call
import sys
import os

# Add mavis-tools to path to import log
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import log

class TestLog(unittest.TestCase):
    @patch('log.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('log.json.dump')
    def test_salvare_truncates_fifo_and_writes_file(self, mock_json_dump, mock_file, mock_makedirs):
        # 1. Arrange
        test_data = {
            'intrari': [{'id': i} for i in range(200)],
            'nivel': {'info': 5}
        }

        # 2. Act
        log.salvare(test_data)

        # 3. Assert
        # Check FIFO truncation (should keep the first 150, which are the newest in this logic)
        self.assertEqual(len(test_data['intrari']), 150)
        self.assertEqual(test_data['intrari'][0]['id'], 0)
        self.assertEqual(test_data['intrari'][149]['id'], 149)

        # Check filesystem operations
        mock_makedirs.assert_called_once_with(os.path.dirname(log.FIS), exist_ok=True)
        mock_file.assert_called_once_with(log.FIS, 'w', encoding='utf-8')

        # Check json dump call
        mock_json_dump.assert_called_once_with(
            test_data,
            mock_file.return_value,
            ensure_ascii=False,
            indent=1
        )


    @patch('log.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json {')
    def test_incarcare_invalid_json_returns_default(self, mock_file, mock_exists):
        # 1. Arrange
        mock_exists.return_value = True

        # 2. Act
        result = log.incarcare()

        # 3. Assert
        self.assertEqual(result, {'intrari': [], 'nivel': {}})
        mock_exists.assert_called_once_with(log.FIS)
        mock_file.assert_called_once_with(log.FIS, encoding='utf-8')

if __name__ == '__main__':
    unittest.main()
