import unittest, tempfile
from pathlib import Path
from core import run

class Tests(unittest.TestCase):

    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.db = str(Path(self.t.name) / 'test.sqlite3')

    def tearDown(self):
        self.t.cleanup()

    def test_persistence(self):
        run({'action': 'create', 'title': 'Export reports'}, self.db)
        self.assertEqual(len(run({'action': 'list'}, self.db)['ideas']), 1)

    def test_idempotent_vote(self):
        run({'action': 'create', 'title': 'Export reports'}, self.db)
        for _ in range(2):
            run({'action': 'vote', 'id': 1, 'voter': 'voter-1234'}, self.db)
        self.assertEqual(run({'action': 'list'}, self.db)['ideas'][0]['votes'], 1)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            run({'action': 'create', 'title': 'x'}, self.db)

    def test_missing_idea(self):
        with self.assertRaises(ValueError):
            run({'action': 'vote', 'id': 1, 'voter': 'voter-1234'}, self.db)

    def test_literal_content(self):
        self.assertEqual(run({'action': 'create', 'title': '<script>alert(1)</script>'}, self.db)['ideas'][0]['title'], '<script>alert(1)</script>')
