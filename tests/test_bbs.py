import tempfile
import unittest
from pathlib import Path
from vapor_board.bbs import BulletinBoard


class BulletinBoardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "bbs.sqlite"
        self.bbs = BulletinBoard(self.path)

    def test_boards_and_posts_persist(self):
        board_id = self.bbs.create_board("Notices")
        self.bbs.post(board_id, "operator", "Store closed Monday")
        reopened = BulletinBoard(self.path)
        self.assertEqual(reopened.list_boards()[0]["name"], "Notices")
        self.assertEqual(reopened.list_posts(board_id)[0]["body"], "Store closed Monday")

    def test_mail_is_recipient_scoped(self):
        self.bbs.send_mail("alice", "bob", "Hello")
        self.assertEqual(len(self.bbs.inbox("bob")), 1)
        self.assertEqual(self.bbs.inbox("alice"), [])

    def test_read_only_commands(self):
        self.assertIn("/boards", self.bbs.command("alice", "/help"))
        self.assertEqual(self.bbs.command("alice", "/inbox"), "0 message(s) in inbox.")
        self.assertIn("Unknown", self.bbs.command("alice", "/delete"))

    def test_rejects_invalid_input(self):
        for value in ("", " " * 3, "x" * 4001):
            with self.assertRaises(ValueError):
                self.bbs.send_mail("alice", "bob", value)
        with self.assertRaises(ValueError):
            self.bbs.list_posts(1, 1000)
        with self.assertRaises(ValueError):
            self.bbs.post(999, "alice", "no board")


if __name__ == "__main__":
    unittest.main()
