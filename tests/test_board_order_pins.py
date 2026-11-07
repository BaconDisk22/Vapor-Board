"""Board ordering and pinned posts in the engine, including databases from older versions."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from vapor_board.bbs import BulletinBoard
from vapor_board.local_operator import inspect_database


class BoardOrderPinTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "bbs.sqlite"

    def names(self, bbs):
        return [b["name"] for b in bbs.list_boards()]

    def test_boards_keep_creation_order_until_moved(self):
        bbs = BulletinBoard(self.path)
        a, b, c = (bbs.create_board(n) for n in ("Hours", "News", "Staff"))
        self.assertEqual(self.names(bbs), ["Hours", "News", "Staff"])
        self.assertTrue(bbs.move_board(c, -1))
        self.assertEqual(self.names(bbs), ["Hours", "Staff", "News"])
        self.assertTrue(bbs.move_board(a, 1))
        self.assertEqual(self.names(bbs), ["Staff", "Hours", "News"])
        self.assertFalse(bbs.move_board(c, -1))  # already first
        self.assertFalse(bbs.move_board(b, 1))  # already last
        bbs.create_board("Deals")
        self.assertEqual(self.names(bbs)[-1], "Deals")  # new boards go to the end
        self.assertEqual([b["name"] for b in inspect_database(self.path)["boards"]], self.names(bbs))

    def test_move_board_validates(self):
        bbs = BulletinBoard(self.path)
        board = bbs.create_board("Hours")
        for args in ((board, 2), (board, 0), (0, 1), (99, 1)):
            with self.assertRaises(ValueError):
                bbs.move_board(*args)

    def test_pinned_posts_come_first_then_newest(self):
        bbs = BulletinBoard(self.path)
        board = bbs.create_board("Hours")
        first, second, third = (bbs.post(board, "Op", body) for body in ("Old", "Middle", "New"))
        bbs.pin_post(first)
        posts = bbs.list_posts(board)
        self.assertEqual([p["body"] for p in posts], ["Old", "New", "Middle"])
        self.assertIsNotNone(posts[0]["pinned_at"])
        self.assertIsNone(posts[1]["pinned_at"])
        self.assertEqual([p["body"] for p in inspect_database(self.path, board)["posts"]], ["Old", "New", "Middle"])
        pinned_at = posts[0]["pinned_at"]
        bbs.pin_post(first)  # pinning again keeps the original pin time
        self.assertEqual(bbs.list_posts(board)[0]["pinned_at"], pinned_at)
        bbs.pin_post(first, pinned=False)
        self.assertEqual([p["body"] for p in bbs.list_posts(board)], ["New", "Middle", "Old"])
        with self.assertRaises(ValueError):
            bbs.pin_post(999)

    def test_older_database_is_upgraded_in_place(self):
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE boards (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
            db.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, board_id INTEGER NOT NULL REFERENCES boards(id), author TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("CREATE TABLE mail (id INTEGER PRIMARY KEY, sender TEXT NOT NULL, recipient TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("INSERT INTO boards (name) VALUES ('Hours'), ('News')")
            db.execute("INSERT INTO posts (board_id, author, body) VALUES (1, 'Op', 'Hello')")
        db.close()
        # The read-only reader copes before any upgrade...
        self.assertEqual([b["name"] for b in inspect_database(self.path)["boards"]], ["Hours", "News"])
        self.assertIsNone(inspect_database(self.path, 1)["posts"][0]["pinned_at"])
        # ...and opening it for writing adds the new columns, keeping the old order.
        bbs = BulletinBoard(self.path)
        self.assertEqual(self.names(bbs), ["Hours", "News"])
        bbs.create_board("Staff")
        self.assertTrue(bbs.move_board(3, -1))
        self.assertEqual(self.names(bbs), ["Hours", "Staff", "News"])
        bbs.pin_post(1)
        self.assertIsNotNone(bbs.list_posts(1)[0]["pinned_at"])


if __name__ == "__main__":
    unittest.main()
