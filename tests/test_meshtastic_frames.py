import unittest
from vapor_board.meshtastic_frames import FrameDecoder, MAGIC


def packet(payload):
    return MAGIC + len(payload).to_bytes(2, "big") + payload


class FrameTests(unittest.TestCase):
    def test_fragmented_packet(self):
        decoder = FrameDecoder()
        data = packet(b"abc")
        self.assertEqual(decoder.feed(data[:1]), [])
        self.assertEqual(decoder.feed(data[1:4]), [])
        self.assertEqual(decoder.feed(data[4:]), [b"abc"])

    def test_multiple_packets_and_noise(self):
        decoder = FrameDecoder()
        self.assertEqual(decoder.feed(b"noise" + packet(b"a") + packet(b"bc")), [b"a", b"bc"])

    def test_oversized_header_recovers(self):
        decoder = FrameDecoder()
        self.assertEqual(decoder.feed(MAGIC + (513).to_bytes(2, "big") + packet(b"ok")), [b"ok"])

    def test_split_magic_and_reset(self):
        decoder = FrameDecoder()
        self.assertEqual(decoder.feed(b"noise" + MAGIC[:1]), [])
        self.assertEqual(decoder.feed(MAGIC[1:] + b"\x00\x01x"), [b"x"])
        decoder.feed(packet(b"pending")[:5])
        decoder.reset()
        self.assertEqual(decoder.feed(packet(b"new")), [b"new"])

    def test_invalid_input(self):
        with self.assertRaises(TypeError): FrameDecoder().feed("not bytes")


if __name__ == "__main__": unittest.main()
