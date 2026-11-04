# Operator Boards tab

The desktop Boards tab now reads boards and posts from an existing local SQLite database at `~/.vapor-board/bbs.sqlite`. Missing or invalid databases display an error rather than creating a new one. This is a **trusted local operator-only** viewer, not authenticated customer access. It intentionally does not display private mail or allow posting. No radio transmissions occur.
