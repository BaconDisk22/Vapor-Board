"""Shared harness: opens the real Tk desktop invisibly against a temporary home."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest import mock
from vapor_board import desktop


def walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from walk(child)


class DesktopHarness(unittest.TestCase):
    """Base for window tests; skipped where no display is available (Linux CI)."""
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

    def run_desktop(self, scenario, page="Boards"):
        def mainloop(root, *_args):
            try:
                root.attributes("-alpha", 0.0)  # invisible: nothing flashes on the operator's screen
                root.geometry("+4000+4000")
                self.nav(root, page).invoke()  # open the page from the sidebar, as the operator would
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
    def buttons(root):
        return {w.cget("text"): w for w in walk(root) if w.winfo_class() == "TButton"}

    @staticmethod
    def nav(root, name):
        """Sidebar button for a page; its label may carry a count, e.g. "Messages  (2)"."""
        return next(w for w in walk(root) if w.winfo_class() == "TButton"
                    and w.cget("style") in ("Nav.TButton", "NavActive.TButton") and w.cget("text").startswith(name))

    @staticmethod
    def page(root, title):
        """The page frame whose heading label reads title."""
        return next(w.master for w in walk(root) if w.winfo_class() == "TLabel" and w.cget("style") == "Title.TLabel" and w.cget("text") == title)

    def assert_page_fits(self, root, title):
        page = self.page(root, title)
        bottom = page.winfo_rooty() + page.winfo_height()
        right = page.winfo_rootx() + page.winfo_width()
        for widget in walk(page):
            if widget is page or widget.winfo_class() == "TFrame":
                continue
            with self.subTest(widget=str(widget)):
                self.assertTrue(widget.winfo_ismapped(), "hidden by lack of space")
                self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(), bottom)
                self.assertLessEqual(widget.winfo_rootx() + widget.winfo_width(), right)
