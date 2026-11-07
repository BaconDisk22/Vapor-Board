"""Drives the real Tk Messages page; skipped where no display is available."""
from desktop_harness import DesktopHarness, walk
from vapor_board.bbs import BulletinBoard


class DesktopMessagesUiTests(DesktopHarness):
    def setUp(self):
        super().setUp()
        self.bbs = BulletinBoard(self.database)
        self.bbs.send_mail("alice", "Operator", "Can you hold the blue one?\nThanks")
        self.bbs.send_mail("bob", "Operator", "Running late today")
        self.bbs.send_mail("alice", "carol", "Private to carol")

    def widgets(self, root):
        page = self.page(root, "Messages")
        mail_list = self.lists(root, "Messages")[0]
        reader, editor = self.texts(root, "Messages")
        to_entry = next(w for w in walk(page) if w.winfo_class() == "TEntry")
        return mail_list, reader, editor, to_entry

    @staticmethod
    def badge(root):
        badge = next(w for w in walk(root) if w.winfo_name() == "messages_badge")
        return badge.cget("text") if badge.winfo_manager() else None

    def test_inbox_shows_only_the_operators_mail_and_marks_it_read(self):
        def scenario(root):
            mail_list, reader, _editor, _to = self.widgets(root)
            self.assertEqual(self.badge(root), "2")
            self.assertEqual(self.rows(mail_list), ("●  bob — Running late today", "●  alice — Can you hold the blue one?"))
            self.assertEqual(mail_list.item("1", "tags"), ("strong",))
            self.pick(root, mail_list, 1)
            self.assertEqual(reader.get("1.0", "end-1c"), "Can you hold the blue one?\nThanks")
            titles = self.card_titles(root, self.page(root, "Messages"))
            self.assertIn("From alice", titles)
            self.assertEqual(self.rows(mail_list)[1], "    alice — Can you hold the blue one?")
            self.assertEqual(mail_list.selection(), ("1",))  # stays selected after the list refreshes
            self.assertEqual(self.badge(root), "1")
            self.assertEqual(self.bbs.unread_count("Operator"), 1)
            self.assertEqual(self.bbs.unread_count("carol"), 1)

        self.run_desktop(scenario, page="Messages")

    def test_reply_sends_as_the_operator_and_shows_in_sent(self):
        def scenario(root):
            mail_list, reader, editor, to_entry = self.widgets(root)
            buttons = self.buttons(root, "Messages")
            self.assertFalse(self.enabled(buttons["Reply"]))
            self.pick(root, mail_list, 1)
            self.assertTrue(self.enabled(buttons["Reply"]))
            buttons["Reply"].invoke()
            self.assertEqual(to_entry.get(), "alice")
            self.assertIn("Reply to alice", self.card_titles(root, self.page(root, "Messages")))
            editor.insert("1.0", "Held at the counter")
            buttons["Send message"].invoke()
            self.assertEqual(to_entry.get(), "")
            self.assertEqual(editor.get("1.0", "end-1c"), "")
            self.assertEqual(self.toast(root), "Message sent: Delivered to alice's inbox on this Mac.")
            self.assertEqual(self.rows(mail_list), ("To alice — Held at the counter",))
            self.pick(root, mail_list, 0)
            self.assertIn("To alice", self.card_titles(root, self.page(root, "Messages")))
            self.assertFalse(self.enabled(buttons["Reply"]))  # replies come from the inbox

        self.run_desktop(scenario, page="Messages")
        sent = self.bbs.sent("Operator")
        self.assertEqual([(m["sender"], m["recipient"], m["body"]) for m in sent], [("Operator", "alice", "Held at the counter")])
        self.assertEqual(self.bbs.inbox("alice")[0]["body"], "Held at the counter")

    def test_invalid_send_is_refused_and_the_draft_kept(self):
        def scenario(root):
            _list, _reader, editor, _to = self.widgets(root)
            editor.insert("1.0", "No recipient")
            self.buttons(root, "Messages")["Send message"].invoke()
            self.assertTrue(self.toast(root).startswith("Message not sent: "))
            self.assertEqual(editor.get("1.0", "end-1c"), "No recipient")

        self.run_desktop(scenario, page="Messages")
        self.assertEqual(self.bbs.sent("Operator"), [])

    def test_no_database_means_empty_inbox_without_creating_one(self):
        self.database.unlink()

        def scenario(root):
            mail_list, reader, _editor, _to = self.widgets(root)
            self.assertEqual(self.rows(mail_list), ())
            self.assertEqual(self.placeholder(mail_list), "No messages yet")
            self.assertEqual(reader.get("1.0", "end-1c"), "No messages yet.")
            self.assertIsNone(self.badge(root))

        self.run_desktop(scenario, page="Messages")
        self.assertFalse(self.database.exists())

    def test_every_messages_control_fits_the_default_window(self):
        self.run_desktop(lambda root: self.assert_page_fits(root, "Messages"), page="Messages")


if __name__ == "__main__":
    import unittest
    unittest.main()
