"""Pure reducer for desktop radio event display, independent of Tkinter."""
from dataclasses import dataclass
from .tcp import ConnectionState

@dataclass(frozen=True)
class RadioDisplayState:
    tcp: ConnectionState = ConnectionState.DISCONNECTED
    protocol_verified: bool = False
    decoded: int = 0
    detail: str = "Disconnected"


def reduce_event(state, event):
    kind, data = event
    if kind == "connecting":
        return RadioDisplayState(ConnectionState.CONNECTING, False, state.decoded, "Connecting")
    if kind == "tcp_open":
        return RadioDisplayState(ConnectionState.CONNECTED, False, state.decoded, "TCP open; protocol unverified")
    if kind == "protobuf" and state.tcp == ConnectionState.CONNECTED:
        return RadioDisplayState(ConnectionState.CONNECTED, True, state.decoded + 1, "Protobuf received")
    if kind == "error":
        return RadioDisplayState(ConnectionState.ERROR, False, state.decoded, str(data))
    if kind == "disconnected":
        return RadioDisplayState(ConnectionState.DISCONNECTED, False, state.decoded, "Disconnected")
    return state
