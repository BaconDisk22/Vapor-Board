# Vapor Board desktop foundation

This is a **local-only UI preview**, not a complete BBS application or radio-connected Mac build. It uses Tkinter and the shop name from `~/.vapor-board/shop.json` when that file exists, otherwise safe defaults. The preview does not open a socket, start a BBS server, or send messages. The status bar explicitly states no radio connection.

From the repository root:

```sh
python3 -m vapor_board.desktop
python3 -m unittest discover -s tests -v
```

On macOS, install a Python distribution that includes working Tkinter. A packaged Intel Mac .app, code signing, notarization, secure customer authentication, live BBS integration, and actual Meshtastic TCP connectivity remain follow-up work. Do not treat this preview as evidence of radio connectivity or as a production release.
