import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build

class TestBuild(unittest.TestCase):
    def test_initials(self):
        # Happy path
        self.assertEqual(build.initials('John Doe'), 'JD')
        self.assertEqual(build.initials('John'), 'J')
        self.assertEqual(build.initials('John Doe Smith'), 'JD')
        self.assertEqual(build.initials('john doe'), 'JD')

        # Edge cases: empty names
        self.assertEqual(build.initials(None), '—')
        self.assertEqual(build.initials(''), '—')
        self.assertEqual(build.initials('   '), '—')
        self.assertEqual(build.initials(None), '—')

if __name__ == '__main__':
    unittest.main()
