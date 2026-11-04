# Radio display state reducer

This pure reducer handles worker events without modifying Tkinter. It refuses to treat a stale protobuf event as verified when disconnected. It is a foundation for a later UI integration and does not yet replace the desktop's existing event handler. Hardware and race tests are still required.
