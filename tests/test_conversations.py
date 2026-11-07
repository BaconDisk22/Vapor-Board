"""Conversation grouping in the BBS engine (no window needed)."""
import tempfile
import unittest
from pathlib import Path
from vapor_board.bbs import BulletinBoard


class ConversationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.bbs = BulletinBoard(Path(directory.name) / "bbs.sqlite")
        self.bbs.send_mail("alice", "Operator", "Can you hold the blue one?")
        self.bbs.send_mail("bob", "Operator", "Running late")
        self.bbs.send_mail("Operator", "alice", "Held at the counter")
        self.bbs.send_mail("alice", "Operator", "Thanks!")
        self.bbs.send_mail("alice", "carol", "Not for the operator")

    def test_one_row_per_person_newest_first(self):
        rows = self.bbs.conversations("Operator")
        self.assertEqual([r["other"] for r in rows], ["alice", "bob"])
        alice = rows[0]
        self.assertEqual((alice["last_body"], alice["last_from_user"], alice["unread"], alice["total"]), ("Thanks!", False, 2, 3))
        self.assertEqual((rows[1]["unread"], rows[1]["total"]), (1, 1))

    def test_last_message_from_the_operator_counts_as_read(self):
        self.bbs.send_mail("Operator", "bob", "No problem")
        bob = self.bbs.conversations("Operator")[0]
        self.assertEqual((bob["other"], bob["last_from_user"], bob["unread"]), ("bob", True, 1))

    def test_thread_reads_oldest_first_and_only_between_the_two(self):
        thread = self.bbs.conversation("Operator", "alice")
        self.assertEqual([(m["sender"], m["body"]) for m in thread],
                         [("alice", "Can you hold the blue one?"), ("Operator", "Held at the counter"), ("alice", "Thanks!")])
        self.assertEqual(self.bbs.conversation("Operator", "nobody"), [])

    def test_thread_limit_keeps_the_latest(self):
        thread = self.bbs.conversation("Operator", "alice", limit=2)
        self.assertEqual([m["body"] for m in thread], ["Held at the counter", "Thanks!"])
        with self.assertRaises(ValueError):
            self.bbs.conversation("Operator", "alice", limit=0)

    def test_mark_conversation_read_touches_only_that_person(self):
        self.assertEqual(self.bbs.mark_conversation_read("Operator", "alice"), 2)
        self.assertEqual(self.bbs.mark_conversation_read("Operator", "alice"), 0)
        self.assertEqual(self.bbs.unread_count("Operator"), 1)  # bob's is still new
        self.assertEqual(self.bbs.unread_count("carol"), 1)
        self.assertIsNone(self.bbs.conversation("Operator", "alice")[1]["read_at"])  # own sent message untouched

    def test_names_are_validated(self):
        for bad in ("", " ", "x" * 81):
            with self.assertRaises(ValueError):
                self.bbs.conversations(bad)
            with self.assertRaises(ValueError):
                self.bbs.conversation("Operator", bad)


if __name__ == "__main__":
    unittest.main()
