"""Backup snapshots, verification and all-or-nothing restore (no window needed)."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from vapor_board import backup
from vapor_board.bbs import BulletinBoard

NOON = datetime(2026, 11, 7, 12, 0, 0)


class BackupTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.database = self.root / "bbs.sqlite"
        self.folder = self.root / "backups"
        self.bbs = BulletinBoard(self.database)
        board = self.bbs.create_board("General")
        self.bbs.post(board, "Operator", "Hello")
        self.bbs.send_mail("Sam", "Operator", "Hi")

    def test_backup_is_a_verified_copy_with_counts(self):
        info = backup.create_backup(self.database, self.folder, now=NOON)
        self.assertEqual(info.path.name, "bbs-20261107-120000.sqlite")
        self.assertEqual((info.boards, info.posts, info.messages), (1, 1, 1))
        self.assertEqual(info.created, NOON)
        self.assertEqual(info.summary, "1 board, 1 post, 1 message")
        self.assertEqual(BulletinBoard(info.path).list_boards(), [{"id": 1, "name": "General"}])
        self.assertEqual(list(self.folder.glob("*.partial")), [])

    def test_two_backups_in_one_second_do_not_overwrite(self):
        first = backup.create_backup(self.database, self.folder, now=NOON)
        second = backup.create_backup(self.database, self.folder, now=NOON)
        self.assertNotEqual(first.path, second.path)
        self.assertEqual(len(backup.list_backups(self.folder)), 2)

    def test_no_database_means_no_backup(self):
        with self.assertRaisesRegex(backup.BackupError, "no database"):
            backup.create_backup(self.root / "missing.sqlite", self.folder)
        self.assertFalse(self.folder.exists())

    def test_list_is_newest_first_and_skips_junk(self):
        backup.create_backup(self.database, self.folder, now=NOON)
        backup.create_backup(self.database, self.folder, now=NOON.replace(hour=13))
        (self.folder / "bbs-20261107-140000.sqlite").write_text("not a database")
        self.assertEqual([b.created.hour for b in backup.list_backups(self.folder)], [13, 12])
        self.assertEqual(backup.list_backups(self.root / "nowhere"), [])

    def test_inspect_rejects_files_that_are_not_backups(self):
        junk = self.root / "notes.sqlite"
        junk.write_text("hello")
        with self.assertRaisesRegex(backup.BackupError, "readable database"):
            backup.inspect(junk)
        other = self.root / "other.sqlite"
        import sqlite3
        with sqlite3.connect(other) as db:
            db.execute("CREATE TABLE things (id INTEGER)")
        with self.assertRaisesRegex(backup.BackupError, "isn't a Vapor Board backup"):
            backup.inspect(other)
        with self.assertRaisesRegex(backup.BackupError, "doesn't exist"):
            backup.inspect(self.root / "gone.sqlite")

    def test_restore_brings_back_old_data_and_keeps_a_safety_copy(self):
        saved = backup.create_backup(self.database, self.folder, now=NOON)
        self.bbs.create_board("Added later")
        self.bbs.delete_post(1)
        safety = backup.restore_backup(saved.path, self.database, self.folder, now=NOON.replace(hour=15))
        self.assertEqual([b["name"] for b in self.bbs.list_boards()], ["General"])
        self.assertEqual(len(self.bbs.list_posts(1)), 1)
        self.assertEqual(safety.label, "before restore")
        self.assertEqual(safety.path.name, "bbs-20261107-150000-before-restore.sqlite")
        self.assertEqual(safety.boards, 2)
        # The safety copy undoes the restore.
        backup.restore_backup(safety.path, self.database, self.folder)
        self.assertEqual([b["name"] for b in self.bbs.list_boards()], ["General", "Added later"])

    def test_failed_restore_changes_nothing(self):
        junk = self.root / "bbs-20261107-120000.sqlite"
        junk.write_text("garbage")
        with self.assertRaises(backup.BackupError):
            backup.restore_backup(junk, self.database, self.folder)
        self.assertEqual([b["name"] for b in self.bbs.list_boards()], ["General"])
        self.assertFalse(self.folder.exists())  # refused before any safety copy was needed
        self.assertFalse((self.root / "bbs.sqlite.restoring").exists())

    def test_restoring_the_live_database_onto_itself_is_refused(self):
        with self.assertRaisesRegex(backup.BackupError, "live database"):
            backup.restore_backup(self.database, self.database, self.folder)

    def test_restore_onto_a_fresh_install_needs_no_safety_copy(self):
        saved = backup.create_backup(self.database, self.folder, now=NOON)
        fresh = self.root / "new" / "bbs.sqlite"
        self.assertIsNone(backup.restore_backup(saved.path, fresh, self.folder))
        self.assertEqual(BulletinBoard(fresh).list_boards(), [{"id": 1, "name": "General"}])


if __name__ == "__main__":
    unittest.main()
