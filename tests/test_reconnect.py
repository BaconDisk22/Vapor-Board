import unittest
from vapor_board.reconnect import ReconnectController, ReconnectPolicy
from vapor_board.tcp import ConnectionState

class FakeClient:
    def __init__(self, results):
        self.results = list(results)
        self.state = ConnectionState.DISCONNECTED
        self.calls = 0
    def connect(self):
        self.calls += 1
        result = self.results.pop(0)
        self.state = ConnectionState.CONNECTED if result else ConnectionState.ERROR
        return result

class ReconnectTests(unittest.TestCase):
    def test_bounded_attempts(self):
        client = FakeClient([False, False, False, False])
        ctl = ReconnectController(client)
        self.assertEqual([ctl.step()[1] for _ in range(5)], [1.0, 2.0, 4.0, None, None])
        self.assertEqual(client.calls, 4)
    def test_recovers_and_resets(self):
        client = FakeClient([False, True])
        ctl = ReconnectController(client)
        self.assertEqual(ctl.step(), (False, 1.0))
        self.assertEqual(ctl.step(), (True, None))
        self.assertEqual(ctl.failures, 0)
    def test_invalid_policy(self):
        with self.assertRaises(ValueError): ReconnectPolicy(max_attempts=0)
        with self.assertRaises(ValueError): ReconnectPolicy(initial_delay=0)

if __name__ == "__main__": unittest.main()
