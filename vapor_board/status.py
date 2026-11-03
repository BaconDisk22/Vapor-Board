"""UI status projection. Never infer protocol health from a TCP socket alone."""
from dataclasses import dataclass
from .tcp import ConnectionState


@dataclass(frozen=True)
class StatusSnapshot:
    tcp_state: ConnectionState = ConnectionState.DISCONNECTED
    protocol_verified: bool = False
    tx_enabled: bool = False
    mqtt_enabled: bool = False

    def __post_init__(self):
        if not isinstance(self.tcp_state, ConnectionState):
            raise ValueError("invalid TCP state")
        for name in ("protocol_verified", "tx_enabled", "mqtt_enabled"):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"invalid {name}")
        if self.protocol_verified and self.tcp_state != ConnectionState.CONNECTED:
            raise ValueError("cannot verify protocol without TCP connection")

    @property
    def radio_label(self):
        if self.tcp_state == ConnectionState.CONNECTED:
            return "Meshtastic protocol verified" if self.protocol_verified else "TCP open; radio unverified"
        return {ConnectionState.CONNECTING: "TCP connecting", ConnectionState.ERROR: "TCP error", ConnectionState.DISCONNECTED: "Not connected"}[self.tcp_state]

    @property
    def footer(self):
        return f"Radio: {self.radio_label} | TX: {'ENABLED' if self.tx_enabled else 'DISABLED'} | MQTT: {'ENABLED' if self.mqtt_enabled else 'DISABLED'}"
