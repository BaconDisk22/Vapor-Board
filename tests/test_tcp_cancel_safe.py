import threading
import unittest
from vapor_board.tcp import ReceiveOnlyTcpClient, ConnectionState

class FakeSocket:
    def __init__(self): self.closed = False
    def close(self): self.closed = True
    def shutdown(self, how): pass

class TcpCancellationTests(unittest.TestCase):
    def test_late_connect_cannot_reopen_after_disconnect(self):
        entered = threading.Event()
        release = threading.Event()
        sockets = []
        def factory(address, timeout):
            entered.set()
            self.assertTrue(release.wait(2))
            sock = FakeSocket()
            sockets.append(sock)
            return sock
        client = ReceiveOnlyTcpClient(socket_factory=factory)
        results = []
        thread = threading.Thread(target=lambda: results.append(client.connect()))
        thread.start()
        self.assertTrue(entered.wait(2))
        client.disconnect()
        release.set()
        thread.join(2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(results, [False])
        self.assertTrue(sockets[0].closed)
        self.assertEqual(client.state, ConnectionState.DISCONNECTED)

if __name__ == "__main__": unittest.main()
