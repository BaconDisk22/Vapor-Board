"""Board ordering and pinned posts on the real Tk Boards page."""
from desktop_harness import DesktopHarness
from vapor_board.bbs import BulletinBoard


class DesktopBoardOrderUiTests(DesktopHarness):
    def setUp(self):
        super().setUp()
        self.bbs = BulletinBoard(self.database)
        self.hours = self.bbs.create_board("Hours")
        self.bbs.create_board("News")
        self.bbs.create_board("Staff")

    def test_move_boards_up_and_down(self):
        def scenario(root):
            board_list = self.lists(root, "Boards")[0]
            buttons = self.buttons(root, "Boards")
            self.assertEqual(board_list.selection(), ("0",))
            self.assertFalse(self.enabled(buttons["↑"]))  # first board can't go higher
            self.assertTrue(self.enabled(buttons["↓"]))
            buttons["↓"].invoke()
            self.assertEqual(self.rows(board_list), ("News", "Hours", "Staff"))
            self.assertEqual(board_list.selection(), ("1",))  # the moved board stays selected
            buttons["↓"].invoke()
            self.assertEqual(self.rows(board_list), ("News", "Staff", "Hours"))
            self.assertFalse(self.enabled(buttons["↓"]))
            self.assertTrue(self.enabled(buttons["↑"]))
            buttons["↑"].invoke()
            self.assertEqual(self.rows(board_list), ("News", "Hours", "Staff"))

        self.run_desktop(scenario)
        self.assertEqual([b["name"] for b in self.bbs.list_boards()], ["News", "Hours", "Staff"])

    def test_pin_keeps_a_post_on_top(self):
        old = self.bbs.post(self.hours, "Operator", "Open 10–8")
        self.bbs.post(self.hours, "Jess", "Closing early Thursday")

        def scenario(root):
            post_list = self.lists(root, "Boards")[1]
            view = self.texts(root, "Boards")[0]
            buttons = self.buttons(root, "Boards")
            self.assertFalse(self.enabled(buttons["Pin"]))
            self.pick(root, post_list, 1)  # the older post
            buttons["Pin"].invoke()
            self.assertEqual(self.rows(post_list), ("◆  Operator — Open 10–8", "Jess — Closing early Thursday"))
            self.assertEqual(post_list.selection(), ("0",))
            self.assertEqual(buttons["Pin"].cget("text"), "Unpin")
            self.assertTrue(view.get("1.0", "1.end").endswith("  ·  Pinned"))
            self.assertEqual(self.toast(root), "Post pinned: It stays at the top of Hours.")
            self.assertIn("2 posts · pinned first, then newest", self.labels(self.page(root, "Boards")))
            buttons["Pin"].invoke()
            self.assertEqual(self.rows(post_list), ("Jess — Closing early Thursday", "Operator — Open 10–8"))
            self.assertEqual(self.toast(root), "Post unpinned: It's back in date order.")
            self.assertEqual(buttons["Pin"].cget("text"), "Pin")

        self.run_desktop(scenario)
        self.assertIsNone(self.bbs.list_posts(self.hours)[1]["pinned_at"])
        self.assertEqual(self.bbs.list_posts(self.hours)[1]["id"], old)


if __name__ == "__main__":
    import unittest
    unittest.main()
