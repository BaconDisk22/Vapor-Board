import unittest
from vapor_board.radio_event_state import RadioDisplayState, reduce_event
from vapor_board.tcp import ConnectionState

class DisplayReducerRegressionTests(unittest.TestCase):
    def test_error_clears_verification(self):
        state = reduce_event(RadioDisplayState(), ("tcp_open", None))
        state = reduce_event(state, ("protobuf", {"variant": "packet"}))
        self.assertTrue(state.protocol_verified)
        state = reduce_event(state, ("error", "closed"))
        self.assertFalse(state.protocol_verified)
        self.assertEqual(state.tcp, ConnectionState.ERROR)
    def test_disconnected_protobuf_ignored(self):
        state = reduce_event(RadioDisplayState(), ("protobuf", {"variant": "packet"}))
        self.assertEqual(state.decoded, 0)
        self.assertFalse(state.protocol_verified)

if __name__ == "__main__": unittest.main()
