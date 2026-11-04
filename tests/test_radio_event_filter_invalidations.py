import unittest
from vapor_board.radio_event_filter import EventGenerationFilter

class InvalidationsTests(unittest.TestCase):
    def test_multiple_stops_keep_prior_tokens_invalid(self):
        gate = EventGenerationFilter()
        token = gate.begin()
        gate.invalidate()
        gate.invalidate()
        self.assertIsNone(gate.accept(token, ("tcp_open", None)))
        current = gate.begin()
        self.assertEqual(gate.accept(current, ("connecting", None)), ("connecting", None))
    def test_reject_boolean_generation(self):
        gate = EventGenerationFilter()
        gate.begin()
        self.assertIsNone(gate.accept(True, ("tcp_open", None)))

if __name__ == "__main__": unittest.main()
