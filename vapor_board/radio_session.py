"""Explicit receive-only radio session with honest TCP/protobuf state."""
from .frame_reader import FramedTcpReader
from .tcp import ReceiveOnlyTcpClient, ConnectionState
from .protobuf_inspector import parse_from_radio, describe_from_radio

class RadioSession:
    def __init__(self, settings=None, client=None, parser=None):
        self.reader = FramedTcpReader(client if client is not None else ReceiveOnlyTcpClient(settings))
        self.parser = parser if parser is not None else parse_from_radio
        self.protocol_verified = False
        self.last_error = None
        self.frames_seen = 0

    @property
    def state(self):
        return self.reader.client.state

    def connect(self):
        self.protocol_verified = False
        self.frames_seen = 0
        self.last_error = None
        return self.reader.connect()

    def receive(self):
        if self.state != ConnectionState.CONNECTED:
            self.protocol_verified = False
            raise ConnectionError("TCP disconnected")
        try:
            frames = self.reader.read_frames()
            results = []
            for frame in frames:
                message = self.parser(frame)
                results.append(describe_from_radio(message))
                self.frames_seen += 1
                self.protocol_verified = True
            if self.state != ConnectionState.CONNECTED:
                self.protocol_verified = False
            return results
        except Exception as exc:
            self.protocol_verified = False
            self.last_error = str(exc)
            raise

    def disconnect(self):
        self.protocol_verified = False
        self.reader.disconnect()

    def send(self, *_args, **_kwargs):
        raise PermissionError("outbound radio transmission disabled")
