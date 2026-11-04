import tempfile
import unittest
from pathlib import Path
from vapor_board.bbs import BulletinBoard
from vapor_board.board_browser import BoardBrowser

class BoardBrowserTests(unittest.TestCase):
    def test_lists_existing_boards_and_posts(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bbs.db"
            bbs = BulletinBoard(path)
            board_id = bbs.create_board("News")
            bbs.post(board_id, "operator", "Update")
            browser = BoardBrowser(path)
            self.assertEqual(browser.boards()[0]["name"], "News")
            self.assertEqual(browser.posts(board_id)[0]["body"], "Update")
    def test_missing_database_is_not_created(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError): BoardBrowser(Path(folder) / "missing.db").boards()

if __name__ == "__main__": unittest.main()
