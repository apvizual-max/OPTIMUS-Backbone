import unittest
import sys
import os

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.extract_wayland_workflows import render_index

class TestExtractWaylandWorkflows(unittest.TestCase):
    def test_render_index_success(self):
        manifest = {
            "source": "/fake/source",
            "output": "/fake/output",
            "blob_bytes": 1234567,
            "extracted": 2,
            "failed": 0,
            "workflows": [
                {
                    "path": "folder/workflow-one/SKILL.md",
                    "bytes": 5000,
                    "sha256": "abcdef1234567890"
                },
                {
                    "path": "workflow-two",
                    "bytes": 1500,
                    "sha256": "0987654321fedcba"
                }
            ]
        }

        result = render_index(manifest)

        # Check that header contains expected stats
        self.assertIn("**Source**: `/fake/source`", result)
        self.assertIn("**Output**: `/fake/output`", result)
        self.assertIn("**Extracted**: 2 workflows from a 1,234,567-byte packed blob", result)
        self.assertIn("**Failed**: 0", result)

        # Check that workflows are correctly parsed
        # folder/workflow-one/SKILL.md -> workflow-one (second to last component)
        self.assertIn("| 1 | `workflow-one` | 5,000 | `abcdef1234567890` |", result)
        # workflow-two -> workflow-two (no slashes, use full path)
        self.assertIn("| 2 | `workflow-two` | 1,500 | `0987654321fedcba` |", result)

    def test_render_index_empty_workflows(self):
        manifest = {
            "source": "/fake/source",
            "output": "/fake/output",
            "blob_bytes": 0,
            "extracted": 0,
            "failed": 0,
            "workflows": []
        }

        result = render_index(manifest)

        self.assertIn("**Extracted**: 0 workflows from a 0-byte packed blob", result)
        self.assertIn("|---|---|---|---|", result)

        # Verify that there are no workflow rows right after the header
        lines = result.split('\n')
        header_index = lines.index("|---|---|---|---|")
        next_line = lines[header_index + 1]
        self.assertEqual(next_line, "")

if __name__ == '__main__':
    unittest.main()
