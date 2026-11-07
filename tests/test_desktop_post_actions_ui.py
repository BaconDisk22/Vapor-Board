"""Drives the real Tk Boards page; skipped where no display is available."""
from unittest import mock
from desktop_harness import DesktopHarness, walk
from vapor_board import desktop
from vapor_board.bbs import BulletinBoard


class DesktopPostActionsUiTests(DesktopHarness):
    def setUp(self):
        super().setUp()
        self.board_id = BulletinBoard(self.database).create_board("General")

    def widgets(self, root):
        board_list, post_list = self.lists(root, "Boards")
        view, editor = self.texts(root, "Boards")
        return board_list, post_list, view, editor, self.buttons(root, "Boards")

    def test_publish_edit_and_delete_through_the_window(self):
        def scenario(root):
            board_list, post_list, view, editor, buttons = self.widgets(root)
            # The first board opens automatically; post actions wait for a post to be chosen.
            self.assertEqual(board_list.selection(), ("0",))
            self.assertFalse(self.enabled(buttons["Edit"]))
            self.assertFalse(self.enabled(buttons["Delete"]))
            self.assertFalse(self.enabled(buttons["Cancel"]))
            self.assertIn("New post in General", self.card_titles(root, self.page(root, "Boards")))

            editor.insert("1.0", "First post\n\nfrom the desktop")
            buttons["Publish post"].invoke()
            self.assertEqual(editor.get("1.0", "end-1c"), "")
            self.assertTrue(view.get("1.0", "end-1c").startswith("Operator  ·  #1  ·  Today "))
            self.assertTrue(view.get("1.0", "end-1c").endswith("\nFirst post\n\nfrom the desktop"))
            self.assertEqual(self.rows(post_list), ("Operator — First post",))
            self.assertEqual(self.toast(root), "Post published: Added to General.")

            self.pick(root, post_list, 0)
            self.assertTrue(self.enabled(buttons["Edit"]))
            self.assertTrue(self.enabled(buttons["Delete"]))
            buttons["Edit"].invoke()
            self.assertEqual(editor.get("1.0", "end-1c"), "First post\n\nfrom the desktop")
            self.assertIn("Editing post #1", self.card_titles(root, self.page(root, "Boards")))
            self.assertIn("Save changes", self.buttons(root, "Boards"))
            editor.delete("1.0", "end")
            editor.insert("1.0", "Edited post")
            self.buttons(root, "Boards")["Save changes"].invoke()
            self.assertTrue(view.get("1.0", "end-1c").endswith("\nEdited post"))
            self.assertEqual(self.toast(root), "Post updated")
            self.assertIn("Publish post", self.buttons(root, "Boards"))

            self.pick(root, post_list, 0)
            with mock.patch.object(desktop.messagebox, "askyesno", return_value=False) as ask:
                buttons["Delete"].invoke()
            ask.assert_called_once()
            self.assertEqual(ask.call_args.kwargs["default"], "no")
            self.assertEqual(len(BulletinBoard(self.database).list_posts(self.board_id)), 1)

            self.pick(root, post_list, 0)
            with mock.patch.object(desktop.messagebox, "askyesno", return_value=True):
                buttons["Delete"].invoke()
            self.assertEqual(BulletinBoard(self.database).list_posts(self.board_id), [])
            self.assertEqual(view.get("1.0", "end-1c"), "No posts yet.")
            self.assertEqual(self.rows(post_list), ())
            self.assertEqual(self.toast(root), "Post deleted")
            self.assertFalse(self.enabled(buttons["Delete"]))

        self.run_desktop(scenario)

    def test_editing_never_creates_a_duplicate_post(self):
        BulletinBoard(self.database).post(self.board_id, "Operator", "Original")

        def scenario(root):
            _boards, post_list, _view, editor, buttons = self.widgets(root)
            self.pick(root, post_list, 0)
            buttons["Edit"].invoke()
            editor.insert("end", " (changed)")
            self.buttons(root, "Boards")["Save changes"].invoke()

        self.run_desktop(scenario)
        posts = BulletinBoard(self.database).list_posts(self.board_id)
        self.assertEqual([p["body"] for p in posts], ["Original (changed)"])

    def test_editing_shows_the_posts_own_author_then_restores_yours(self):
        BulletinBoard(self.database).post(self.board_id, "Jess", "Staff note")

        def scenario(root):
            _boards, post_list, _view, _editor, buttons = self.widgets(root)
            author = [w for w in walk(self.page(root, "Boards")) if w.winfo_class() == "TEntry"][1]
            author.delete(0, "end")
            author.insert(0, "Sam")
            self.pick(root, post_list, 0)
            buttons["Edit"].invoke()
            self.assertEqual(author.get(), "Jess")
            self.assertTrue(author.instate(["disabled"]))
            buttons["Cancel"].invoke()
            self.assertEqual(author.get(), "Sam")
            self.assertFalse(author.instate(["disabled"]))

        self.run_desktop(scenario)

    def test_cancel_leaves_the_post_untouched(self):
        BulletinBoard(self.database).post(self.board_id, "Operator", "Keep me")

        def scenario(root):
            _boards, post_list, _view, editor, buttons = self.widgets(root)
            self.pick(root, post_list, 0)
            buttons["Edit"].invoke()
            editor.insert("end", " — draft change")
            buttons["Cancel"].invoke()
            self.assertEqual(editor.get("1.0", "end-1c"), "")
            self.assertIn("Publish post", self.buttons(root, "Boards"))
            self.assertFalse(self.enabled(buttons["Cancel"]))

        self.run_desktop(scenario)
        self.assertEqual(BulletinBoard(self.database).list_posts(self.board_id)[0]["body"], "Keep me")

    def test_two_posts_are_separated_by_a_blank_line(self):
        board = BulletinBoard(self.database)
        board.post(self.board_id, "Operator", "Older")
        board.post(self.board_id, "Staff", "Newer")

        def scenario(root):
            _boards, _posts, view, _editor, _buttons = self.widgets(root)
            lines = view.get("1.0", "end-1c").split("\n")
            self.assertEqual([lines[0].split("  ·  ")[0], lines[1], lines[2], lines[3].split("  ·  ")[0], lines[4]],
                             ["Staff", "Newer", "", "Operator", "Older"])

        self.run_desktop(scenario)

    def test_empty_edit_is_refused_and_post_kept(self):
        BulletinBoard(self.database).post(self.board_id, "Operator", "Keep me")

        def scenario(root):
            _boards, post_list, _view, editor, buttons = self.widgets(root)
            self.pick(root, post_list, 0)
            buttons["Edit"].invoke()
            editor.delete("1.0", "end")
            self.buttons(root, "Boards")["Save changes"].invoke()
            self.assertTrue(self.toast(root).startswith("Post not updated: "))
            self.assertIn("Save changes", self.buttons(root, "Boards"))  # still editing, nothing lost

        self.run_desktop(scenario)
        self.assertEqual(BulletinBoard(self.database).list_posts(self.board_id)[0]["body"], "Keep me")

    def test_create_board_from_the_entry_and_open_it(self):
        def scenario(root):
            board_list, _posts, _view, _editor, buttons = self.widgets(root)
            # The board-name field is the first input on the page (author comes later, in the composer).
            entry = next(w for w in walk(self.page(root, "Boards")) if w.winfo_class() == "TEntry")
            entry.insert(0, "Closures")
            buttons["Add board"].invoke()
            self.assertEqual(self.rows(board_list), ("General", "Closures"))
            self.assertEqual(board_list.selection(), ("1",))
            self.assertEqual(self.toast(root), "Board created: “Closures” is ready for posts.")
            buttons["Add board"].invoke()  # empty name
            self.assertTrue(self.toast(root).startswith("Board not created: "))

        self.run_desktop(scenario)

    def test_first_run_without_a_database_explains_what_to_do(self):
        self.database.unlink()

        def scenario(root):
            board_list, post_list, view, _editor, buttons = self.widgets(root)
            self.assertEqual(self.placeholder(board_list), "No boards yet — add one below")
            self.assertEqual(self.rows(board_list), ())
            self.assertFalse(self.enabled(buttons["Publish post"]))
            self.assertIn("Boards hold notices", view.get("1.0", "end-1c"))

        self.run_desktop(scenario)
        self.assertFalse(self.database.exists())

    def test_every_boards_control_fits_the_default_window(self):
        BulletinBoard(self.database).post(self.board_id, "Operator", "Hello")
        self.run_desktop(lambda root: self.assert_page_fits(root, "Boards"))


if __name__ == "__main__":
    import unittest
    unittest.main()
