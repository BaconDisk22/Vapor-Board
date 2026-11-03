import unittest
from vapor_board.radio_session import RadioSession
from vapor_board.tcp import ConnectionState

class FakeClient:
    state = ConnectionState.DISCONNECTED
    def __init__(self, chunks): self.chunks = list(chunks)
    def connect(self): self.state = ConnectionState.CONNECTED; return True
    def receive(self, size):
        chunk = self.chunks.pop(0)
        if not chunk: self.state = ConnectionState.DISCONNECTED
        return chunk
    def disconnect(self): self.state = ConnectionState.DISCONNECTED

class FakeMessage:
    def WhichOneof(self, name): return "packet"

class RadioSessionTests(unittest.TestCase):
    def test_protocol_not_verified_until_parse(self):
        session = RadioSession(client=FakeClient([b"\x94\xc3\x00\x01x", b""]), parser=lambda data: FakeMessage())
        self.assertTrue(session.connect())
        self.assertFalse(session.protocol_verified)
        self.assertEqual(session.receive(), [{"variant": "packet"}])
        self.assertTrue(session.protocol_verified)
        self.assertEqual(session.receive(), [])
        self.assertFalse(session.protocol_verified)
    def test_send_denied(self):
        session = RadioSession(client=FakeClient([]))
        with self.assertRaises(PermissionError): session.send(b"x")

if __name__ == "__main__": unittest.main()
