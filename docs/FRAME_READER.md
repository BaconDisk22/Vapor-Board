# TCP frame reader

Combines the existing receive-only TCP socket client and incremental framing decoder. It yields raw framed protobuf bytes, **not** decoded Meshtastic messages. It does not send ToRadio messages or establish a protocol session. TCP socket open and receipt of framed data do not verify device identity or radio health. It clears partial buffers on disconnect and reconnect. No background worker is started.

Run: `python3 -m unittest discover -s tests -v`.
