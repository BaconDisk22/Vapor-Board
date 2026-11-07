import sqlite3
import tempfile
import unittest
from pathlib import Path
from vapor_board.access import AuthorizedBBS, Principal, Role
from vapor_board.bbs import BulletinBoard
from vapor_board.config import ShopConfig


class PrivateMailTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "bbs.sqlite"
        self.bbs = BulletinBoard(self.path)

    def test_new_mail_is_unread_until_its_recipient_opens_it(self):
        first = self.bbs.send_mail("alice", "Operator", "Restock the shelf")
        self.bbs.send_mail("bob", "Operator", "Running late")
        self.bbs.send_mail("alice", "carol", "Not for the operator")
        self.assertEqual(self.bbs.unread_count("Operator"), 2)
        self.assertIsNone(self.bbs.inbox("Operator")[1]["read_at"])
        self.bbs.mark_read("Operator", first)
        self.bbs.mark_read("Operator", first)  # marking twice is harmless
        self.assertEqual(self.bbs.unread_count("Operator"), 1)
        self.assertIsNotNone(self.bbs.inbox("Operator")[1]["read_at"])
        self.assertEqual(self.bbs.unread_count("carol"), 1)

    def test_only_the_recipient_can_mark_mail_read(self):
        mail_id = self.bbs.send_mail("alice", "Operator", "Private")
        for reader in ("alice", "bob"):
            with self.assertRaises(ValueError):
                self.bbs.mark_read(reader, mail_id)
        self.assertEqual(self.bbs.unread_count("Operator"), 1)

    def test_bad_message_ids_are_rejected(self):
        for mail_id in (999, 0, -1, "1", True, 1.0, None):
            with self.assertRaises(ValueError):
                self.bbs.mark_read("Operator", mail_id)

    def test_sent_lists_only_the_senders_mail_newest_first(self):
        self.bbs.send_mail("Operator", "alice", "First")
        self.bbs.send_mail("bob", "alice", "Someone else")
        self.bbs.send_mail("Operator", "bob", "Second")
        self.assertEqual([m["body"] for m in self.bbs.sent("Operator")], ["Second", "First"])
        with self.assertRaises(ValueError):
            self.bbs.sent("Operator", limit=0)

    def test_database_from_before_read_tracking_is_upgraded_in_place(self):
        old = Path(self.directory.name) / "old.sqlite"
        with sqlite3.connect(old) as db:
            db.execute("CREATE TABLE mail (id INTEGER PRIMARY KEY, sender TEXT NOT NULL, recipient TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("INSERT INTO mail (sender, recipient, body) VALUES ('alice', 'Operator', 'Kept')")
        db.close()
        upgraded = BulletinBoard(old)
        self.assertEqual(upgraded.inbox("Operator")[0]["body"], "Kept")
        self.assertEqual(upgraded.unread_count("Operator"), 1)
        BulletinBoard(old)  # opening again must not try to add the column twice


class AuthorizedMailTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.api = AuthorizedBBS(BulletinBoard(Path(directory.name) / "bbs.sqlite"))
        self.staff = Principal("Operator", Role.STAFF)
        self.alice = Principal("alice", Role.CUSTOMER, age_verified=True, approved=True)

    def test_sent_unread_and_mark_read_use_the_callers_own_identity(self):
        self.api.send_mail(self.staff, "alice", "Hello")
        self.assertEqual(self.api.sent(self.staff)[0]["recipient"], "alice")
        self.assertEqual(self.api.sent(self.alice), [])
        self.assertEqual(self.api.unread_count(self.alice), 1)
        mail_id = self.api.inbox(self.alice)[0]["id"]
        with self.assertRaises(ValueError):
            self.api.mark_read(self.staff, mail_id)
        self.api.mark_read(self.alice, mail_id)
        self.assertEqual(self.api.unread_count(self.alice), 0)


class OperatorNameConfigTests(unittest.TestCase):
    def test_operator_name_defaults_and_is_validated(self):
        self.assertEqual(ShopConfig().operator_name, "Operator")
        for bad in ("", "   ", "x" * 81, None):
            with self.assertRaises(ValueError):
                ShopConfig(operator_name=bad)


if __name__ == "__main__":
    unittest.main()
