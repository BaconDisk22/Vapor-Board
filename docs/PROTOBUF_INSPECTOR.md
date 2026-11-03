# Optional Meshtastic protobuf inspector

Parses raw framed payload bytes as `FromRadio` using an installed compatible `meshtastic` Python package. Import is optional, so the existing desktop preview and offline tests remain dependency-free. Only reports protobuf variant metadata by default, not private message text. Parsing does not verify node identity, radio health, or authorization. This module is not yet wired to the live TCP reader or UI. Test compatibility with actual firmware before using it for operator decisions.
