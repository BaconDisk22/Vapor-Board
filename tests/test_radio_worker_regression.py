import unittest
from vapor_board.radio_worker import RadioWorker
from vapor_board.tcp import ConnectionState

class FakeSession:
    state = ConnectionState.DISCONNECTED
    closed = False
    def __init__(self, settings=None): pass
    def connect(self):
        self.state = ConnectionState.CONNECTED
        return True
    def receive(self):
        self.state = ConnectionState.DISCONNECTED
        return []
    def disconnect(self):
        self.closed = True
        self.state = ConnectionState.DISCONNECTED

class RadioWorkerRegressionTests(unittest.TestCase):
    def test_lifecycle_and_disconnect_event(self):
        worker = RadioWorker(session_factory=FakeSession)
        self.assertTrue(worker.start())
        worker._thread.join(timeout=2)
        events = []
        while True:
            event = worker.poll()
            if event is None: break
            events.append(event[0])
        self.assertEqual(events, ["connecting", "tcp_open", "disconnected"])
    def test_does_not_start_two_concurrent_workers(self):
        worker = RadioWorker(session_factory=FakeSession)
        self.assertTrue(worker.start())
        worker._thread.join(timeout=2)
        worker.stop()

if __name__ == "__main__": unittest.main()
