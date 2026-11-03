import tempfile
import unittest
from pathlib import Path
from vapor_board.access import AccessDenied, AuthorizedBBS, Principal, Role
from vapor_board.bbs import BulletinBoard


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.api = AuthorizedBBS(BulletinBoard(Path(self.directory.name) / "bbs.sqlite"))
        self.staff = Principal("operator", Role.STAFF)
        self.customer = Principal("alice", Role.CUSTOMER, age_verified=True, approved=True)
        self.pending = Principal("pending", Role.CUSTOMER, age_verified=True, approved=False)
        self.unverified = Principal("unverified", Role.CUSTOMER, age_verified=False, approved=True)

    def test_staff_creates_board(self):
        board = self.api.create_board(self.staff, "Notices")
        self.api.post(self.customer, board, "Hello")
        self.assertEqual(self.api.list_posts(self.customer, board)[0]["author"], "alice")

    def test_customer_cannot_create_board(self):
        with self.assertRaises(AccessDenied):
            self.api.create_board(self.customer, "Admin")

    def test_denied_customers_cannot_read_or_write(self):
        board = self.api.create_board(self.staff, "Notices")
        for principal in (self.pending, self.unverified, None):
            with self.subTest(principal=principal):
                for call in (lambda: self.api.list_boards(principal),
                             lambda: self.api.list_posts(principal, board),
                             lambda: self.api.post(principal, board, "No"),
                             lambda: self.api.send_mail(principal, "operator", "No"),
                             lambda: self.api.inbox(principal),
                             lambda: self.api.command(principal, "/boards")):
                    with self.assertRaises(AccessDenied):
                        call()

    def test_sender_and_inbox_identity_are_not_caller_selected(self):
        self.api.send_mail(self.staff, "alice", "Private")
        self.assertEqual(self.api.inbox(self.customer)[0]["body"], "Private")
        self.assertEqual(self.api.inbox(self.staff), [])


if __name__ == "__main__":
    unittest.main()
