# Background radio worker regression tests

Uses a fake session to check worker event ordering and disconnect cleanup without hardware or transmissions. Real TCP socket cancellation, protobuf compatibility, and rapid reconnect behavior remain to be verified on an Intel Mac with a Meshtastic radio.
