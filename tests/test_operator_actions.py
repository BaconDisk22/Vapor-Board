import tempfile
import unittest
from pathlib import Path
from vapor_board.operator_actions import create_local_board, publish_local_post
from vapor_board.bbs import BulletinBoard

class OperatorActionsTests(unittest.TestCase):
    def test_create_and_publish_locally(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "local.sqlite"
            board_id = create_local_board(db, "Announcements")
            post_id = publish_local_post(db, board_id, "Operator", "Welcome")
            self.assertGreater(post_id, 0)
            posts = BulletinBoard(db).list_posts(board_id)
            self.assertEqual(posts[0]["body"], "Welcome")

    def test_empty_post_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "local.sqlite"
            board_id = create_local_board(db, "General")
            with self.assertRaises(ValueError):
                publish_local_post(db, board_id, "Operator", "   ")

if __name__ == "__main__":
    unittest.main()
