import unittest
from vapor_board.status import StatusSnapshot
from vapor_board.tcp import ConnectionState

class StatusTests(unittest.TestCase):
    def test_defaults_are_safe(self):
        snapshot = StatusSnapshot()
        self.assertIn("Not connected", snapshot.footer)
        self.assertIn("TX: DISABLED", snapshot.footer)
    def test_open_socket_is_not_verified_radio(self):
        snapshot = StatusSnapshot(tcp_state=ConnectionState.CONNECTED)
        self.assertEqual(snapshot.radio_label, "TCP open; radio unverified")
    def test_protocol_verified_requires_tcp(self):
        with self.assertRaises(ValueError): StatusSnapshot(protocol_verified=True)
    def test_error_state(self):
        self.assertEqual(StatusSnapshot(tcp_state=ConnectionState.ERROR).radio_label, "TCP error")

if __name__ == "__main__": unittest.main()
