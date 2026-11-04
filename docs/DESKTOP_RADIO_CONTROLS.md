# Receive-only desktop radio controls

Overview now offers explicit TCP Connect/Disconnect, host and port fields, live worker events, and an honest status footer. Default host is loopback; enter your actual radio's LAN IP. A TCP-open state is not protocol verification. Protobuf parsing requires a compatible installed Meshtastic Python package; no ToRadio packets are sent. This is an initial integration requiring Intel Mac and radio testing. The worker is not an authenticated connection and may require further shutdown/race handling.
