# Desktop TCP probe foundation

This explicit, one-shot TCP probe runs in a background thread so Tkinter need not block. It reports a snapshot and closes the socket immediately. A successful probe means the TCP port accepted a connection, **not** that the Meshtastic protocol is verified or that a live connection remains open. The desktop UI does not yet expose this probe; a follow-up PR must wire a button and show historical probe results separately from live status. No transmissions occur.

Run: `python3 -m unittest discover -s tests -v`.
