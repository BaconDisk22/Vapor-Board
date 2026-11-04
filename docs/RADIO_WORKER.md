# Opt-in background radio worker

RadioWorker provides explicit start/stop and a queue of connection/protobuf/disconnect events. It never modifies Tkinter widgets directly and never transmits radio packets. This is infrastructure only: the desktop does not yet call it. TCP-open events do not imply verified Meshtastic protocol. A successful protobuf parse is not device authentication. Worker shutdown, timeouts, and hardware disconnect behavior need validation on an actual radio and Intel Mac.
