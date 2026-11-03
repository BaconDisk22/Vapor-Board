import unittest
from vapor_board.frame_reader import FramedTcpReader
from vapor_board.tcp import ConnectionState

class FakeClient:
    state = ConnectionState.DISCONNECTED
    def connect(self):
        self.state = ConnectionState.CONNECTED
        return True
    def receive(self, size):
        return b"\x94\xc3\x00\x01x"
    def disconnect(self):
        self.state = ConnectionState.DISCONNECTED

class ReaderTests(unittest.TestCase):
    def test_frame(self):
        reader = FramedTcpReader(FakeClient())
        self.assertTrue(reader.connect())
        self.assertEqual(reader.read_frames(), [b"x"])
        self.assertEqual(reader.frames_received, 1)
    def test_send_denied(self):
        with self.assertRaises(PermissionError):
            FramedTcpReader(FakeClient()).send(b"x")
