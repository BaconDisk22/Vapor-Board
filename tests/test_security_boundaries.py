import tempfile
import unittest
from pathlib import Path
from vapor_board.bbs import BulletinBoard
from vapor_board.access import AuthorizedBBS, Principal, Role, AccessDenied
from vapor_board.tcp import ReceiveOnlyTcpClient
from vapor_board.status import StatusSnapshot

class SecurityBoundaryTests(unittest.TestCase):
    def test_customer_denied_without_approval_or_age_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            bbs = AuthorizedBBS(BulletinBoard(Path(folder) / "bbs.db"))
            for principal in (
                Principal("customer", Role.CUSTOMER, approved=False, age_verified=True),
                Principal("customer", Role.CUSTOMER, approved=True, age_verified=False),
            ):
                with self.subTest(principal=principal), self.assertRaises(AccessDenied):
                    bbs.list_boards(principal)
    def test_customer_cannot_create_board(self):
        with tempfile.TemporaryDirectory() as folder:
            bbs = AuthorizedBBS(BulletinBoard(Path(folder) / "bbs.db"))
            with self.assertRaises(AccessDenied):
                bbs.create_board(Principal("customer", Role.CUSTOMER, approved=True, age_verified=True), "Notices")
    def test_radio_send_denied_even_when_settings_allow_it(self):
        with self.assertRaises(PermissionError):
            ReceiveOnlyTcpClient().send(b"message")
    def test_default_status_is_not_verified(self):
        self.assertFalse(StatusSnapshot().protocol_verified)
        self.assertFalse(StatusSnapshot().tx_enabled)

if __name__ == "__main__": unittest.main()
