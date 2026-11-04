import unittest
from vapor_board.radio_event_filter import EventGenerationFilter

class EventFilterTests(unittest.TestCase):
    def test_stale_events_ignored_after_new_connection(self):
        gate = EventGenerationFilter()
        old = gate.begin()
        new = gate.begin()
        self.assertIsNone(gate.accept(old, ("tcp_open", None)))
        self.assertEqual(gate.accept(new, ("tcp_open", None)), ("tcp_open", None))
    def test_disconnect_invalidates_events(self):
        gate = EventGenerationFilter()
        token = gate.begin()
        gate.invalidate()
        self.assertIsNone(gate.accept(token, ("protobuf", {})))

if __name__ == "__main__": unittest.main()
