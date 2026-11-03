"""Local read-only BBS inspection. No authentication or customer access implied."""
import argparse
import json
from pathlib import Path
from .bbs import BulletinBoard


def inspect_database(path, board_id=None):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError("BBS database does not exist")
    board = BulletinBoard(path)
    if board_id is None:
        return {"boards": board.list_boards()}
    return {"posts": board.list_posts(board_id)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect local Vapor Board BBS data (read-only)")
    parser.add_argument("database", help="existing SQLite database path")
    parser.add_argument("--board", type=int, help="board ID for recent posts")
    args = parser.parse_args(argv)
    print(json.dumps(inspect_database(args.database, args.board), indent=2))


if __name__ == "__main__":
    main()
