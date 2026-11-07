"""Back up and restore from the Settings page of the real Tk window."""
from datetime import datetime
from unittest import mock
from desktop_harness import DesktopHarness
from vapor_board import backup, desktop
from vapor_board.bbs import BulletinBoard


class DesktopBackupUiTests(DesktopHarness):
    def setUp(self):
        super().setUp()
        self.bbs = BulletinBoard(self.database)
        self.bbs.create_board("General")
        self.folder = self.home / ".vapor-board" / "backups"

    def last_backup(self, root):
        labels = self.labels(self.page(root, "Settings"))
        # textvariable labels report their text through cget too
        return labels[labels.index("Last backup") + 1]

    def test_back_up_now_saves_a_copy_and_says_so(self):
        def scenario(root):
            self.assertEqual(self.last_backup(root), "None yet")
            self.buttons(root, "Settings")["Back up now"].invoke()
            root.update()
            self.assertTrue(self.toast(root).startswith("Backup saved: 1 board, 0 posts, 0 messages copied to bbs-"))
            self.assertTrue(self.last_backup(root).startswith("Today "))
            self.assert_page_fits(root, "Settings")

        self.run_desktop(scenario, page="Settings")
        self.assertEqual(len(backup.list_backups(self.folder)), 1)

    def test_back_up_is_unavailable_before_there_is_a_database(self):
        self.database.unlink()

        def scenario(root):
            self.assertFalse(self.enabled(self.buttons(root, "Settings")["Back up now"]))

        self.run_desktop(scenario, page="Settings")

    def test_restore_replaces_data_after_confirming(self):
        saved = backup.create_backup(self.database, self.folder, now=datetime(2026, 11, 1, 9, 30))
        self.bbs.create_board("Added later")

        def scenario(root):
            with mock.patch.object(desktop.filedialog, "askopenfilename", return_value=str(saved.path)), \
                    mock.patch.object(desktop.messagebox, "askyesno", return_value=True) as ask:
                self.buttons(root, "Settings")["Restore…"].invoke()
            self.assertIn("1 Nov 2026 at 9:30 AM", ask.call_args[0][1])
            self.assertEqual(ask.call_args.kwargs["default"], "no")
            self.assertTrue(self.toast(root).startswith("Backup restored: 1 board, 0 posts, 0 messages restored. Previous data saved as bbs-"))
            self.assertEqual(self.rows(self.lists(root, "Boards")[0]), ("General",))

        self.run_desktop(scenario, page="Settings")
        self.assertEqual([b["name"] for b in self.bbs.list_boards()], ["General"])
        self.assertEqual([b.label for b in backup.list_backups(self.folder)].count("before restore"), 1)

    def test_declining_or_cancelling_changes_nothing(self):
        saved = backup.create_backup(self.database, self.folder)
        self.bbs.create_board("Keep me")

        def scenario(root):
            restore = self.buttons(root, "Settings")["Restore…"]
            with mock.patch.object(desktop.filedialog, "askopenfilename", return_value=""):
                restore.invoke()
            with mock.patch.object(desktop.filedialog, "askopenfilename", return_value=str(saved.path)), \
                    mock.patch.object(desktop.messagebox, "askyesno", return_value=False):
                restore.invoke()

        self.run_desktop(scenario, page="Settings")
        self.assertEqual([b["name"] for b in self.bbs.list_boards()], ["General", "Keep me"])

    def test_a_file_that_is_not_a_backup_is_explained(self):
        junk = self.home / "notes.sqlite"
        junk.write_text("hello")

        def scenario(root):
            with mock.patch.object(desktop.filedialog, "askopenfilename", return_value=str(junk)):
                self.buttons(root, "Settings")["Restore…"].invoke()
            self.assertTrue(self.toast(root).startswith("Can't restore that file: notes.sqlite isn't a readable database"))

        self.run_desktop(scenario, page="Settings")


if __name__ == "__main__":
    import unittest
    unittest.main()
