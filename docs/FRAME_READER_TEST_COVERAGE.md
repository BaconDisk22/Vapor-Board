# Frame reader regression tests

Adds unit tests for TCP chunk fragmentation, concatenated framed payloads, disconnected reads, and reset of partial data on reconnect. Uses in-memory fake clients; no real Meshtastic hardware, protobuf parsing, or transmissions are involved.
