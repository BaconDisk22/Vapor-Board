import unittest
from vapor_board.desktop_probe import TcpProbe
from vapor_board.tcp import ConnectionState


class FakeClient:
    def __init__(self, settings):
        self.last_error = None
        self.closed = False
    def connect(self):
        return True
    def disconnect(self):
        self.closed = True


class ProbeTests(unittest.TestCase):
    def test_success_is_unverified_and_socket_closed(self):
        clients = []
        def factory(settings):
            client = FakeClient(settings)
            clients.append(client)
            return client
        probe = TcpProbe(client_factory=factory)
        self.assertTrue(probe.start())
        probe._worker.join(timeout=2)
        result = probe.poll()
        self.assertEqual(result.snapshot.tcp_state, ConnectionState.CONNECTED)
        self.assertFalse(result.snapshot.protocol_verified)
        self.assertFalse(result.snapshot.tx_enabled)
        self.assertTrue(clients[0].closed)

    def test_failure_is_reported(self):
        class Broken(FakeClient):
            def connect(self):
                self.last_error = "offline"
                return False
        probe = TcpProbe(client_factory=Broken)
        probe.start()
        probe._worker.join(timeout=2)
        self.assertEqual(probe.poll().error, "offline")


if __name__ == "__main__": unittest.main()
