import unittest
from vapor_board.protobuf_inspector import parse_from_radio, describe_from_radio

class FakeMessage:
    def ParseFromString(self, payload):
        self.payload = payload
    def WhichOneof(self, name):
        assert name == "payload_variant"
        return "packet"

class InspectorTests(unittest.TestCase):
    def test_schema_injection(self):
        parsed = parse_from_radio(b"payload", schema=FakeMessage)
        self.assertEqual(parsed.payload, b"payload")
        self.assertEqual(describe_from_radio(parsed), {"variant": "packet"})
    def test_empty_payload_rejected(self):
        with self.assertRaises(ValueError): parse_from_radio(b"", schema=FakeMessage)

if __name__ == "__main__": unittest.main()
