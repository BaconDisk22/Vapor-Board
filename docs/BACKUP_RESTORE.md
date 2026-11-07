# Database backup and restore

Settings → Storage has **Back up now** and **Restore…**. Code: `vapor_board/backup.py`.

## Back up
- Copies `~/.vapor-board/bbs.sqlite` to `~/.vapor-board/backups/bbs-YYYYMMDD-HHMMSS.sqlite`.
- Uses SQLite's online backup API, so the copy is consistent even while the app is open.
- Each copy is written as `.partial`, checked with `PRAGMA integrity_check` and the boards/posts/mail tables, then renamed. A failed backup leaves no file.
- Nothing is uploaded or sent over the radio. Backups are never deleted automatically.

## Restore
1. Pick a backup file (the picker opens in the backups folder).
2. The file is checked first; a damaged or non–Vapor Board file is refused with an explanation.
3. A confirmation (default **No**) shows the backup's date and what it contains.
4. The current database is saved as `bbs-…-before-restore.sqlite`, so a restore can be undone by restoring that file.
5. The backup is copied to a staging file, checked again, then swapped in with an atomic rename. If anything fails, the current database is untouched.
6. Boards, Messages, Overview and Storage refresh; any post being edited is discarded.

## Tests
- `tests/test_backup.py`: snapshots, same-second names, junk files, all-or-nothing restore, undo via the safety copy, fresh install.
- `tests/test_desktop_backup_ui.py`: buttons, confirmation wording and default, cancel/decline, bad file, page fit.

## Not yet verified
- Restoring a backup made by a much older Vapor Board (the engine adds missing columns on open, but only `read_at` exists so far).
- Backups on external or network drives (only the local backups folder is offered by default).
