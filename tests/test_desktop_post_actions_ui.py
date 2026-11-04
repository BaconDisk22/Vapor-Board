"""Drives the real Tk boards tab; skipped where no display is available."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest import mock
from vapor_board import desktop
from vapor_board.bbs import BulletinBoard


def _walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from _walk(child)


class DesktopPostActionsUiTests(unittest.TestCase):
    def setUp(self):
        try:
            tk.Tk().destroy()
        except tk.TclError as exc:
            self.skipTest(f"no display: {exc}")
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.home = Path(self.directory.name)
        (self.home / ".vapor-board").mkdir()
        self.database = self.home / ".vapor-board" / "bbs.sqlite"
        self.board_id = BulletinBoard(self.database).create_board("General")

    def run_desktop(self, scenario):
        def mainloop(root, *_args):
            try:
                root.attributes("-alpha", 0.0)  # invisible: nothing flashes on the operator's screen
                root.geometry("+4000+4000")
                notebook = next(w for w in _walk(root) if w.winfo_class() == "TNotebook")
                notebook.select(1)  # open the Boards tab, as the operator would
                root.update()  # map it so <<ListboxSelect>> bindings fire
                scenario(root)
            finally:
                for pending in root.tk.call("after", "info"):
                    root.after_cancel(pending)
                root.destroy()
        # Keep the window off-screen and fail on any dialog a scenario did not mock.
        unexpected = mock.Mock(side_effect=AssertionError("unexpected dialog"))
        with mock.patch.object(Path, "home", return_value=self.home), \
                mock.patch.object(tk.Tk, "mainloop", mainloop), \
                mock.patch.multiple(desktop.messagebox, showwarning=unexpected, showerror=unexpected, askyesno=unexpected):
            desktop.main()

    @staticmethod
    def widgets(root):
        widgets = list(_walk(root))
        board_list, post_list = [w for w in widgets if isinstance(w, tk.Listbox)]
        view, editor = [w for w in widgets if isinstance(w, tk.Text)]
        buttons = {w.cget("text"): w for w in widgets if w.winfo_class() == "TButton"}
        return board_list, post_list, view, editor, buttons

    def test_save_edit_and_delete_through_the_window(self):
        def scenario(root):
            board_list, post_list, view, editor, buttons = self.widgets(root)
            with mock.patch.object(desktop.messagebox, "showwarning") as warn:
                buttons["Save new post"].invoke()
                buttons["Update post"].invoke()
                buttons["Delete post"].invoke()
            self.assertEqual(warn.call_count, 3)

            board_list.selection_set(0)
            board_list.event_generate("<<ListboxSelect>>")
            root.update()
            editor.insert("1.0", "First post\n\nfrom the desktop")
            buttons["Save new post"].invoke()
            self.assertEqual(editor.get("1.0", "end-1c"), "")
            self.assertEqual(view.get("1.0", "end-1c"), "Operator: First post\n\nfrom the desktop")
            self.assertTrue(post_list.get(0).endswith("Operator: First post"))

            post_list.selection_set(0)
            post_list.event_generate("<<ListboxSelect>>")
            root.update()
            self.assertEqual(editor.get("1.0", "end-1c"), "First post\n\nfrom the desktop")
            editor.delete("1.0", "end")
            editor.insert("1.0", "Edited post")
            buttons["Update post"].invoke()
            self.assertEqual(view.get("1.0", "end-1c"), "Operator: Edited post")

            post_list.selection_set(0)
            with mock.patch.object(desktop.messagebox, "askyesno", return_value=False) as ask:
                buttons["Delete post"].invoke()
            ask.assert_called_once()
            self.assertEqual(len(BulletinBoard(self.database).list_posts(self.board_id)), 1)

            post_list.selection_set(0)
            with mock.patch.object(desktop.messagebox, "askyesno", return_value=True):
                buttons["Delete post"].invoke()
            self.assertEqual(BulletinBoard(self.database).list_posts(self.board_id), [])
            self.assertEqual(view.get("1.0", "end-1c"), "No posts yet.")
            self.assertEqual(post_list.size(), 0)

        self.run_desktop(scenario)

    def test_every_boards_control_fits_the_default_window(self):
        def scenario(root):
            page = next(w for w in _walk(root) if w.winfo_class() == "TNotebook").nametowidget(root.nametowidget(".!notebook").select())
            bottom = page.winfo_rooty() + page.winfo_height()
            right = page.winfo_rootx() + page.winfo_width()
            for widget in _walk(page):
                if widget is page or widget.winfo_class() == "TFrame":
                    continue
                with self.subTest(widget=str(widget)):
                    self.assertTrue(widget.winfo_ismapped(), "hidden by lack of space")
                    self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(), bottom)
                    self.assertLessEqual(widget.winfo_rootx() + widget.winfo_width(), right)

        self.run_desktop(scenario)

    def test_empty_edit_is_refused_and_post_kept(self):
        BulletinBoard(self.database).post(self.board_id, "Operator", "Keep me")

        def scenario(root):
            board_list, post_list, _view, editor, buttons = self.widgets(root)
            board_list.selection_set(0)
            board_list.event_generate("<<ListboxSelect>>")
            root.update()
            post_list.selection_set(0)
            editor.delete("1.0", "end")
            with mock.patch.object(desktop.messagebox, "showerror") as error:
                buttons["Update post"].invoke()
            self.assertEqual(error.call_args[0][0], "Post not updated")

        self.run_desktop(scenario)
        self.assertEqual(BulletinBoard(self.database).list_posts(self.board_id)[0]["body"], "Keep me")


if __name__ == "__main__":
    unittest.main()
