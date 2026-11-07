"""Local database backups: consistent snapshots, verification and an all-or-nothing restore.

Backups are plain SQLite files kept beside the database (``~/.vapor-board/backups``).
Nothing is uploaded or sent anywhere. A restore never deletes data: the current
database is snapshotted first, so the restore itself can be undone.
"""
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REQUIRED_TABLES = ("boards", "posts", "mail")
PREFIX = "bbs-"
SUFFIX = ".sqlite"


@dataclass(frozen=True)
class BackupInfo:
    path: Path
    created: datetime
    size: int
    boards: int
    posts: int
    messages: int
    label: str = ""  # "before restore" for the automatic safety copy

    @property
    def summary(self):
        def count(n, word):
            return f"{n} {word}" + ("" if n == 1 else "s")
        return ", ".join((count(self.boards, "board"), count(self.posts, "post"), count(self.messages, "message")))


class BackupError(ValueError):
    """A backup could not be made, read or restored; the message is shown to the operator."""


def _copy(source, destination):
    """Consistent copy with SQLite's online backup API (safe even while the source is open)."""
    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    try:
        dst = sqlite3.connect(destination)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()


def inspect(path):
    """Counts for a backup file, or BackupError if it is not a usable Vapor Board database."""
    path = Path(path)
    if not path.is_file():
        raise BackupError(f"{path.name} doesn't exist")
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise BackupError(f"{path.name} is damaged")
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            missing = [name for name in REQUIRED_TABLES if name not in tables]
            if missing:
                raise BackupError(f"{path.name} isn't a Vapor Board backup (no {', '.join(missing)} table)")
            counts = [db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in REQUIRED_TABLES]
        finally:
            db.close()
    except sqlite3.DatabaseError as exc:
        raise BackupError(f"{path.name} isn't a readable database ({exc})") from exc
    stem = path.stem[len(PREFIX):] if path.stem.startswith(PREFIX) else ""
    stamp, _, label = stem.partition("-before-")
    try:
        created = datetime.strptime(stamp[:15], "%Y%m%d-%H%M%S")
    except ValueError:
        created = datetime.fromtimestamp(path.stat().st_mtime)
    return BackupInfo(path, created, path.stat().st_size, *counts,
                      label="before restore" if label.startswith("restore") else "")


def _new_path(folder, now, tag=""):
    name = f"{PREFIX}{now:%Y%m%d-%H%M%S}{tag}"
    candidate = folder / f"{name}{SUFFIX}"
    number = 2
    while candidate.exists():  # two backups in the same second
        candidate = folder / f"{name}-{number}{SUFFIX}"
        number += 1
    return candidate


def create_backup(database, folder, now=None, tag=""):
    """Snapshot the database into folder and verify it. Returns the BackupInfo."""
    database, folder = Path(database), Path(folder)
    if not database.is_file():
        raise BackupError("There's no database to back up yet")
    folder.mkdir(parents=True, exist_ok=True)
    target = _new_path(folder, now or datetime.now(), tag)
    partial = target.with_suffix(".partial")
    try:
        _copy(database, partial)
        inspect(partial)
        os.replace(partial, target)
    except (OSError, sqlite3.DatabaseError, BackupError) as exc:
        partial.unlink(missing_ok=True)
        raise BackupError(f"Backup failed: {exc}") from exc
    return inspect(target)


def list_backups(folder):
    """Valid backups in folder, newest first. Unreadable files are skipped."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    found = []
    for path in folder.glob(f"{PREFIX}*{SUFFIX}"):
        try:
            found.append(inspect(path))
        except BackupError:
            continue
    return sorted(found, key=lambda info: (info.created, info.path.name), reverse=True)


def restore_backup(backup, database, folder, now=None):
    """Replace the database with backup, all or nothing.

    The backup is verified first and copied to a temporary file that is swapped in with an
    atomic rename, so a failure leaves the current database untouched. The current database
    is saved to folder beforehand; its BackupInfo is returned (None if there was none).
    """
    backup, database = Path(backup), Path(database)
    inspect(backup)
    if database.exists() and backup.resolve() == database.resolve():
        raise BackupError("That file is the live database, not a backup")
    safety = create_backup(database, folder, now, tag="-before-restore") if database.is_file() else None
    database.parent.mkdir(parents=True, exist_ok=True)
    staged = database.with_name(database.name + ".restoring")
    try:
        _copy(backup, staged)
        inspect(staged)
        os.replace(staged, database)
    except (OSError, sqlite3.DatabaseError, BackupError) as exc:
        staged.unlink(missing_ok=True)
        raise BackupError(f"Restore failed, nothing was changed: {exc}") from exc
    return safety
