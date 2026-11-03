"""Local read-only BBS inspection via SQLite read-only URI."""
import argparse
import json
import sqlite3
from pathlib import Path


def inspect_database(path, board_id=None):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError("BBS database does not exist")
    if board_id is not None and (type(board_id) is not int or board_id < 1):
        raise ValueError("invalid board id")
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        if board_id is None:
            rows = db.execute("SELECT id, name FROM boards ORDER BY id").fetchall()
            return {"boards": [dict(row) for row in rows]}
        rows = db.execute("SELECT id, board_id, author, body, created_at FROM posts WHERE board_id = ? ORDER BY id DESC LIMIT 50", (board_id,)).fetchall()
        return {"posts": [dict(row) for row in rows]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect local Vapor Board BBS data (read-only)")
    parser.add_argument("database", help="existing SQLite database path")
    parser.add_argument("--board", type=int, help="board ID for recent posts")
    args = parser.parse_args(argv)
    print(json.dumps(inspect_database(args.database, args.board), indent=2))


if __name__ == "__main__":
    main()
