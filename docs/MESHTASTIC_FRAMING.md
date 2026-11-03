# Receive-only Meshtastic TCP framing

The incremental parser extracts payloads from the TCP stream format (0x94 0xC3 + two-byte big-endian length + payload), rejects invalid lengths and resynchronizes after noise. It does not decode protobuf messages, identify nodes, prove radio health, or send traffic. Integrate only after testing against actual Meshtastic firmware and protocol fixtures. Do not claim verified radio connectivity from a parsed frame alone.

Run: `python3 -m unittest discover -s tests -v`.
