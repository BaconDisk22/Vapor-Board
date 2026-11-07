"""Drives the real Tk Messages page; skipped where no display is available."""
import tkinter as tk
from unittest import mock
from desktop_harness import DesktopHarness, walk
from vapor_board import desktop
from vapor_board.bbs import BulletinBoard


class DesktopMessagesUiTests(DesktopHarness):
    def setUp(self):
        super().setUp()
        self.bbs = BulletinBoard(self.database)
        self.bbs.send_mail("alice", "Operator", "Can you hold the blue one?\nThanks")
        self.bbs.send_mail("bob", "Operator", "Running late today")
        self.bbs.send_mail("alice", "carol", "Private to carol")

    def widgets(self, root):
        widgets = list(walk(self.page(root, "Messages")))
        mail_list = next(w for w in widgets if isinstance(w, tk.Listbox))
        reader, editor = [w for w in widgets if isinstance(w, tk.Text)]
        to_entry = next(w for w in widgets if w.winfo_class() == "TEntry")
        return mail_list, reader, editor, to_entry

    @staticmethod
    def select(root, listbox, index):
        listbox.selection_clear(0, "end")
        listbox.selection_set(index)
        listbox.event_generate("<<ListboxSelect>>")
        root.update()

    def test_inbox_shows_only_the_operators_mail_and_marks_it_read(self):
        def scenario(root):
            mail_list, reader, _editor, _to = self.widgets(root)
            self.assertEqual(self.nav(root, "Messages").cget("text"), "Messages  (2)")
            self.assertEqual(mail_list.get(0, "end"), ("●  bob — Running late today", "●  alice — Can you hold the blue one?"))
            self.select(root, mail_list, 1)
            text = reader.get("1.0", "end-1c")
            self.assertTrue(text.startswith("From alice  ·  "))
            self.assertTrue(text.endswith("\nCan you hold the blue one?\nThanks"))
            self.assertEqual(mail_list.get(1), "    alice — Can you hold the blue one?")
            self.assertEqual(self.nav(root, "Messages").cget("text"), "Messages  (1)")
            self.assertEqual(self.bbs.unread_count("Operator"), 1)
            self.assertEqual(self.bbs.unread_count("carol"), 1)

        self.run_desktop(scenario, page="Messages")

    def test_reply_sends_as_the_operator_and_shows_in_sent(self):
        def scenario(root):
            mail_list, reader, editor, to_entry = self.widgets(root)
            buttons = self.buttons(root)
            self.select(root, mail_list, 1)
            buttons["Reply"].invoke()
            self.assertEqual(to_entry.get(), "alice")
            editor.insert("1.0", "Held at the counter")
            buttons["Send message"].invoke()
            self.assertEqual(to_entry.get(), "")
            self.assertEqual(editor.get("1.0", "end-1c"), "")
            self.assertEqual(mail_list.get(0, "end"), ("To alice — Held at the counter",))
            self.select(root, mail_list, 0)
            self.assertTrue(reader.get("1.0", "end-1c").startswith("To alice  ·  "))

        self.run_desktop(scenario, page="Messages")
        sent = self.bbs.sent("Operator")
        self.assertEqual([(m["sender"], m["recipient"], m["body"]) for m in sent], [("Operator", "alice", "Held at the counter")])
        self.assertEqual(self.bbs.inbox("alice")[0]["body"], "Held at the counter")

    def test_invalid_send_and_reply_without_selection_are_refused(self):
        def scenario(root):
            _list, _reader, editor, _to = self.widgets(root)
            buttons = self.buttons(root)
            with mock.patch.object(desktop.messagebox, "showwarning") as warn:
                buttons["Reply"].invoke()
            self.assertEqual(warn.call_args[0][0], "Select message")
            editor.insert("1.0", "No recipient")
            with mock.patch.object(desktop.messagebox, "showerror") as error:
                buttons["Send message"].invoke()
            self.assertEqual(error.call_args[0][0], "Message not sent")
            self.assertEqual(editor.get("1.0", "end-1c"), "No recipient")

        self.run_desktop(scenario, page="Messages")
        self.assertEqual(self.bbs.sent("Operator"), [])

    def test_no_database_means_empty_inbox_without_creating_one(self):
        self.database.unlink()

        def scenario(root):
            mail_list, reader, _editor, _to = self.widgets(root)
            self.assertEqual(mail_list.size(), 0)
            self.assertEqual(reader.get("1.0", "end-1c"), "No messages yet.")

        self.run_desktop(scenario, page="Messages")
        self.assertFalse(self.database.exists())

    def test_every_messages_control_fits_the_default_window(self):
        self.run_desktop(lambda root: self.assert_page_fits(root, "Messages"), page="Messages")


if __name__ == "__main__":
    import unittest
    unittest.main()
