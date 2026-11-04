import unittest
from vapor_board.radio_event_state import RadioDisplayState, reduce_event
from vapor_board.tcp import ConnectionState

class RadioEventTests(unittest.TestCase):
    def test_no_verification_from_tcp_open(self):
        state = reduce_event(RadioDisplayState(), ("tcp_open", None))
        self.assertFalse(state.protocol_verified)
        self.assertEqual(state.tcp, ConnectionState.CONNECTED)
    def test_disconnected_clears_verification(self):
        state = reduce_event(RadioDisplayState(), ("tcp_open", None))
        state = reduce_event(state, ("protobuf", {"variant": "packet"}))
        self.assertTrue(state.protocol_verified)
        state = reduce_event(state, ("disconnected", None))
        self.assertFalse(state.protocol_verified)
    def test_stale_protobuf_does_not_verify_disconnected_session(self):
        state = reduce_event(RadioDisplayState(), ("protobuf", {}))
        self.assertFalse(state.protocol_verified)

if __name__ == "__main__": unittest.main()
