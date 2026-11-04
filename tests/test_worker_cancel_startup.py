import threading
import unittest
from vapor_board.radio_worker import RadioWorker
from vapor_board.tcp import ConnectionState

class SlowSession:
    entered = threading.Event()
    release = threading.Event()
    def __init__(self, settings=None):
        self.state = ConnectionState.DISCONNECTED
    def connect(self):
        self.entered.set()
        self.release.wait(2)
        self.state = ConnectionState.CONNECTED
        return True
    def disconnect(self):
        self.state = ConnectionState.DISCONNECTED
    def receive(self):
        return []

class WorkerCancelTests(unittest.TestCase):
    def test_stop_during_connect_does_not_publish_tcp_open(self):
        SlowSession.entered.clear()
        SlowSession.release.clear()
        worker = RadioWorker(session_factory=SlowSession)
        self.assertTrue(worker.start())
        self.assertTrue(SlowSession.entered.wait(2))
        worker.stop()
        SlowSession.release.set()
        worker._thread.join(2)
        self.assertFalse(worker._thread.is_alive())
        self.assertIsNone(worker.poll())

if __name__ == "__main__": unittest.main()
