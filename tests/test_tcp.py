import unittest
from vapor_board.tcp import ConnectionState, ReceiveOnlyTcpClient, TcpSettings


class FakeSocket:
    def __init__(self, chunks=()):
        self.chunks = list(chunks)
        self.closed = False
    def recv(self, size):
        return self.chunks.pop(0) if self.chunks else b""
    def close(self):
        self.closed = True


class TcpTests(unittest.TestCase):
    def test_safe_defaults(self):
        settings = TcpSettings()
        self.assertFalse(settings.transmissions_enabled)
        self.assertEqual(settings.port, 4403)

    def test_connection_and_disconnect(self):
        sock = FakeSocket([b"test", b""])
        client = ReceiveOnlyTcpClient(socket_factory=lambda addr, timeout: sock)
        self.assertTrue(client.connect())
        self.assertEqual(client.state, ConnectionState.CONNECTED)
        self.assertEqual(client.receive(), b"test")
        self.assertEqual(client.receive(), b"")
        self.assertEqual(client.state, ConnectionState.DISCONNECTED)
        self.assertTrue(sock.closed)

    def test_send_always_denied(self):
        client = ReceiveOnlyTcpClient(socket_factory=lambda addr, timeout: FakeSocket())
        client.connect()
        with self.assertRaises(PermissionError):
            client.send(b"unsafe")

    def test_failed_connection(self):
        def fail(addr, timeout):
            raise OSError("offline")
        client = ReceiveOnlyTcpClient(socket_factory=fail)
        self.assertFalse(client.connect())
        self.assertEqual(client.state, ConnectionState.ERROR)
        self.assertIn("offline", client.last_error)

    def test_bad_settings(self):
        for kwargs in ({"port": 0}, {"port": 65536}, {"timeout": 0},
                       {"transmissions_enabled": "false"}, {"host": ""}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                TcpSettings(**kwargs)


if __name__ == "__main__":
    unittest.main()
