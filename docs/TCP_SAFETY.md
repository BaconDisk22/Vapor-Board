# Meshtastic TCP transport safety foundation

This module is a **receive-only raw TCP connection layer**. It does not parse Meshtastic packets, establish a Meshtastic protocol session, authenticate a node, or prove a radio is healthy. A connected state means only that the TCP socket was successfully opened. The socket can still fail later.

Defaults: `127.0.0.1:4403`, three-second connection timeout, no outbound data. Configure your own host explicitly. Never embed private LAN addresses or credentials in releases. `send()` always raises `PermissionError`, regardless of configuration. No automatic retries or background traffic are performed.

Example:

```python
from vapor_board.tcp import TcpSettings, ReceiveOnlyTcpClient
client = ReceiveOnlyTcpClient(TcpSettings(host="YOUR_RADIO_IP", port=4403))
if client.connect():
    print("TCP socket open (radio protocol not verified)")
    client.disconnect()
else:
    print("TCP connection failed:", client.last_error)
```

Run unit tests: `python3 -m unittest discover -s tests -v`.

Next steps: Meshtastic protocol framing, bounded reads and reconnection policy, explicit operator-approved transmit capability, secure credential handling, actual hardware tests, and desktop status integration. Do not claim full radio support based on a TCP socket probe alone.
