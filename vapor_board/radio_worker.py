"""Opt-in background receive worker; never touches Tk widgets directly."""
from queue import Queue, Empty
from threading import Event, Thread
from .radio_session import RadioSession
from .tcp import ConnectionState

class RadioWorker:
    def __init__(self, session_factory=None):
        self.session_factory = session_factory or RadioSession
        self.events = Queue()
        self._stop = Event()
        self._thread = None
        self._session = None

    def start(self, settings=None):
        if self._thread is not None and self._thread.is_alive():
            return False
        self._stop.clear()
        self._thread = Thread(target=self._run, args=(settings,), daemon=True)
        self._thread.start()
        return True

    def _run(self, settings):
        session = None
        try:
            session = self.session_factory(settings=settings)
            self._session = session
            self.events.put(("connecting", None))
            if not session.connect():
                self.events.put(("error", "TCP connection failed"))
                return
            self.events.put(("tcp_open", None))
            while not self._stop.is_set():
                try:
                    variants = session.receive()
                except (TimeoutError, ConnectionError, OSError) as exc:
                    self.events.put(("error", str(exc)))
                    break
                except Exception as exc:
                    self.events.put(("error", str(exc)))
                    break
                for item in variants:
                    self.events.put(("protobuf", item))
                if session.state != ConnectionState.CONNECTED:
                    break
        finally:
            if session is not None:
                session.disconnect()
            self._session = None
            self.events.put(("disconnected", None))

    def stop(self):
        self._stop.set()
        # Closing the underlying socket unblocks recv on supported platforms.
        session = self._session
        if session is not None:
            session.disconnect()

    def poll(self):
        try:
            return self.events.get_nowait()
        except Empty:
            return None
