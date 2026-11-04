# Explicit receive-only radio session

RadioSession combines TCP, framing, and optional FromRadio protobuf parsing. TCP connectivity alone is not a verified protocol session; protocol_verified becomes true only after a framed message parses successfully. It clears on disconnect, parse failure or receive failure. No background polling or outbound transmissions. The session is not yet connected to the desktop UI; actual firmware testing is still required. Parsing a protobuf message is not cryptographic device authentication.
