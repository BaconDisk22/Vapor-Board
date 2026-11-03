"""Incremental receive-only Meshtastic TCP framing decoder (not protobuf)."""
MAGIC = b"\x94\xc3"
MAX_PAYLOAD = 512


class FrameDecoder:
    def __init__(self):
        self._buffer = bytearray()

    def feed(self, chunk):
        if not isinstance(chunk, (bytes, bytearray, memoryview)):
            raise TypeError("chunk must be bytes-like")
        self._buffer.extend(chunk)
        frames = []
        while True:
            index = self._buffer.find(MAGIC)
            if index < 0:
                self._buffer[:] = self._buffer[-1:] if self._buffer.endswith(MAGIC[:1]) else b""
                break
            if index:
                del self._buffer[:index]
            if len(self._buffer) < 4:
                break
            size = int.from_bytes(self._buffer[2:4], "big")
            if not 0 < size <= MAX_PAYLOAD:
                del self._buffer[0]
                continue
            if len(self._buffer) < size + 4:
                break
            frames.append(bytes(self._buffer[4:4 + size]))
            del self._buffer[:4 + size]
        return frames

    def reset(self):
        self._buffer.clear()
