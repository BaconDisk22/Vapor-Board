"""Receive-only TCP connectivity probe. Does not implement Meshtastic framing."""
import socket
from threading import Lock
from dataclasses import dataclass
from enum import Enum


class ConnectionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass(frozen=True)
class TcpSettings:
    host: str = "127.0.0.1"
    port: int = 4403
    timeout: float = 3.0
    transmissions_enabled: bool = False

    def __post_init__(self):
        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("host is required")
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if not isinstance(self.timeout, (float, int)) or isinstance(self.timeout, bool) or not 0 < self.timeout <= 30:
            raise ValueError("timeout must be greater than zero and at most 30 seconds")
        if type(self.transmissions_enabled) is not bool:
            raise ValueError("transmissions_enabled must be a boolean")


class ReceiveOnlyTcpClient:
    """Socket lifecycle only; connected means TCP open, not Meshtastic radio health."""
    def __init__(self, settings=None, socket_factory=None):
        self.settings = settings or TcpSettings()
        self._socket_factory = socket_factory or socket.create_connection
        self._socket = None
        self.state = ConnectionState.DISCONNECTED
        self.last_error = None
        self._lock = Lock()
        self._generation = 0

    def connect(self):
        self.disconnect()
        with self._lock:
            generation = self._generation
            self.state = ConnectionState.CONNECTING
        try:
            sock = self._socket_factory((self.settings.host, self.settings.port), self.settings.timeout)
        except OSError as exc:
            with self._lock:
                if generation == self._generation:
                    self.state = ConnectionState.ERROR
                    self.last_error = str(exc)
            return False
        with self._lock:
            if generation != self._generation:
                sock.close()
                return False
            self._socket = sock
            self.state = ConnectionState.CONNECTED
            self.last_error = None
            return True

    def receive(self, size=4096):
        if type(size) is not int or not 1 <= size <= 65536:
            raise ValueError("invalid receive size")
        if self._socket is None or self.state != ConnectionState.CONNECTED:
            raise ConnectionError("TCP connection is not open")
        try:
            data = self._socket.recv(size)
        except (OSError, TimeoutError) as exc:
            self.last_error = str(exc)
            self.disconnect()
            self.state = ConnectionState.ERROR
            raise ConnectionError("TCP receive failed") from exc
        if not data:
            self.disconnect()
            return b""
        return data

    def send(self, data):
        raise PermissionError("outbound TCP transmission is unavailable in receive-only client")

    def disconnect(self):
        with self._lock:
            self._generation += 1
            sock, self._socket = self._socket, None
            self.state = ConnectionState.DISCONNECTED
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except (OSError, AttributeError):
                pass
            try:
                sock.close()
            except OSError:
                pass

    def __enter__(self):
        if not self.connect():
            raise ConnectionError(self.last_error or "TCP connection failed")
        return self

    def __exit__(self, *_):
        self.disconnect()
