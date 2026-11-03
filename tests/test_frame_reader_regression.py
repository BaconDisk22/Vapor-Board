import unittest
from vapor_board.frame_reader import FramedTcpReader
from vapor_board.tcp import ConnectionState

class StubClient:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.state = ConnectionState.DISCONNECTED
    def connect(self):
        self.state = ConnectionState.CONNECTED
        return True
    def receive(self, size):
        chunk = self.chunks.pop(0)
        if not chunk:
            self.state = ConnectionState.DISCONNECTED
        return chunk
    def disconnect(self):
        self.state = ConnectionState.DISCONNECTED

class FrameReaderRegressionTests(unittest.TestCase):
    def test_fragmented_and_concatenated_frames(self):
        data = b"\x94\xc3\x00\x01a\x94\xc3\x00\x01b"
        reader = FramedTcpReader(StubClient([data[:3], data[3:]]))
        reader.connect()
        self.assertEqual(reader.read_frames(), [])
        self.assertEqual(reader.read_frames(), [b"a", b"b"])
        self.assertEqual(reader.frames_received, 2)
    def test_disconnected_reader_rejects_reads(self):
        reader = FramedTcpReader(StubClient([]))
        with self.assertRaises(ConnectionError): reader.read_frames()
    def test_partial_data_cleared_after_disconnect(self):
        old = b"\x94\xc3\x00\x03old"
        client = StubClient([old[:5], b"\x94\xc3\x00\x03new"])
        reader = FramedTcpReader(client)
        reader.connect()
        self.assertEqual(reader.read_frames(), [])
        reader.disconnect()
        reader.connect()
        self.assertEqual(reader.read_frames(), [b"new"])

if __name__ == "__main__": unittest.main()
