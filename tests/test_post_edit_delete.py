import tempfile
import unittest
from pathlib import Path
from vapor_board.bbs import BulletinBoard
from vapor_board.operator_actions import create_local_board, publish_local_post, edit_local_post, delete_local_post


class PostEditDeleteTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "bbs.sqlite"
        self.board_id = create_local_board(self.path, "General")
        self.post_id = publish_local_post(self.path, self.board_id, "Operator", "Open 9-5")

    def test_edit_replaces_body_and_keeps_author(self):
        edit_local_post(self.path, self.post_id, "  Open 10-6  ")
        post = BulletinBoard(self.path).list_posts(self.board_id)[0]
        self.assertEqual((post["author"], post["body"]), ("Operator", "Open 10-6"))

    def test_edit_rejects_empty_and_oversized_bodies(self):
        for body in ("", "   ", "x" * 4001, None):
            with self.assertRaises(ValueError):
                edit_local_post(self.path, self.post_id, body)
        self.assertEqual(BulletinBoard(self.path).list_posts(self.board_id)[0]["body"], "Open 9-5")

    def test_delete_removes_only_that_post(self):
        keep = publish_local_post(self.path, self.board_id, "Operator", "Keep me")
        delete_local_post(self.path, self.post_id)
        self.assertEqual([p["id"] for p in BulletinBoard(self.path).list_posts(self.board_id)], [keep])

    def test_missing_and_invalid_post_ids_are_rejected(self):
        for post_id in (999, 0, -1, "1", True, 1.0):
            with self.assertRaises(ValueError):
                edit_local_post(self.path, post_id, "body")
            with self.assertRaises(ValueError):
                delete_local_post(self.path, post_id)
        delete_local_post(self.path, self.post_id)
        with self.assertRaises(ValueError):
            delete_local_post(self.path, self.post_id)


if __name__ == "__main__":
    unittest.main()
