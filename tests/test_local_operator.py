import tempfile
import unittest
from pathlib import Path
from vapor_board.bbs import BulletinBoard
from vapor_board.local_operator import inspect_database

class LocalOperatorTests(unittest.TestCase):
    def test_existing_database_listing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bbs.sqlite"
            bbs = BulletinBoard(path)
            board_id = bbs.create_board("Notices")
            bbs.post(board_id, "staff", "Hello")
            self.assertEqual(inspect_database(path)["boards"][0]["name"], "Notices")
            self.assertEqual(inspect_database(path, board_id)["posts"][0]["body"], "Hello")
    def test_missing_file_does_not_create_database(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing.sqlite"
            with self.assertRaises(FileNotFoundError): inspect_database(path)
            self.assertFalse(path.exists())

if __name__ == "__main__": unittest.main()
