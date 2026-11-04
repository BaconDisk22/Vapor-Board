import unittest
from vapor_board.radio_event_state import RadioDisplayState, reduce_event
from vapor_board.tcp import ConnectionState

class DisconnectSequenceTests(unittest.TestCase):
    def test_repeated_disconnect_keeps_state_safe(self):
        state = reduce_event(RadioDisplayState(), ("tcp_open", None))
        state = reduce_event(state, ("protobuf", {"variant": "packet"}))
        for _ in range(3):
            state = reduce_event(state, ("disconnected", None))
        self.assertEqual(state.tcp, ConnectionState.DISCONNECTED)
        self.assertFalse(state.protocol_verified)
    def test_old_packet_after_error_cannot_reverify(self):
        state = reduce_event(RadioDisplayState(), ("error", "closed"))
        state = reduce_event(state, ("protobuf", {"variant": "packet"}))
        self.assertFalse(state.protocol_verified)
        self.assertEqual(state.decoded, 0)

if __name__ == "__main__":
    unittest.main()
