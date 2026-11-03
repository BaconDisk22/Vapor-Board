# Intel Mac packaging verification checklist

1. Confirm GitHub Actions Intel macOS runner is available and build workflow passes.
2. Inspect uploaded .app and .dmg artifacts for x86_64 architecture.
3. Launch the app on an Intel Mac and verify the Tkinter UI opens.
4. Confirm radio status remains disconnected and TX disabled until an explicit connection feature is implemented.
5. Verify signing, hardened runtime, and notarization before public distribution.
6. Run physical Meshtastic Wi-Fi/TCP connection and disconnect tests separately.

The packaging unit tests validate source references only. They do not prove the binary launches or that macOS Gatekeeper accepts it.
