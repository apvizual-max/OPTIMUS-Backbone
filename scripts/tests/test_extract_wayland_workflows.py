import unittest
from pathlib import Path
import json
import tempfile
import sys
import os

# Add scripts directory to path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract_wayland_workflows import load_index

class TestExtractWaylandWorkflows(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.src_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_index_success(self):
        # Create a mock offsets JSON file
        test_data = {
            "version": "1.0",
            "entries": {
                "test/SKILL.md": [0, 100]
            }
        }

        index_file = self.src_dir / "skill-bodies.offsets.json"
        index_file.write_text(json.dumps(test_data), encoding="utf-8")

        result = load_index(self.src_dir)
        self.assertEqual(result, test_data)

    def test_load_index_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_index(self.src_dir)

    def test_load_index_invalid_json(self):
        index_file = self.src_dir / "skill-bodies.offsets.json"
        index_file.write_text("invalid json content", encoding="utf-8")

        with self.assertRaises(json.JSONDecodeError):
            load_index(self.src_dir)

if __name__ == '__main__':
    unittest.main()
