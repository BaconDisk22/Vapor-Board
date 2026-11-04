"""Offline-first local bulletin board engine. No radio transport or network I/O."""

import sqlite3
from pathlib import Path


class BulletinBoard:
    def __init__(self, database_path):
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self):
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS boards (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
            db.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, board_id INTEGER NOT NULL REFERENCES boards(id), author TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("CREATE TABLE IF NOT EXISTS mail (id INTEGER PRIMARY KEY, sender TEXT NOT NULL, recipient TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")

    @staticmethod
    def _text(value, field, limit):
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f"{field} must contain 1–{limit} characters")
        return value.strip()

    def create_board(self, name):
        name = self._text(name, "board name", 80)
        with self._connect() as db:
            cursor = db.execute("INSERT INTO boards (name) VALUES (?)", (name,))
            return cursor.lastrowid

    def list_boards(self):
        with self._connect() as db:
            return [dict(row) for row in db.execute("SELECT id, name FROM boards ORDER BY id")]

    def post(self, board_id, author, body):
        author = self._text(author, "author", 80)
        body = self._text(body, "post", 4000)
        if type(board_id) is not int or board_id < 1:
            raise ValueError("invalid board id")
        with self._connect() as db:
            cursor = db.execute("INSERT INTO posts (board_id, author, body) VALUES (?, ?, ?)", (board_id, author, body))
            return cursor.lastrowid

    def edit_post(self, post_id, body):
        """Replace a post's body; the original author is kept."""
        body = self._text(body, "post", 4000)
        if type(post_id) is not int or post_id < 1:
            raise ValueError("invalid post id")
        with self._connect() as db:
            if db.execute("UPDATE posts SET body = ? WHERE id = ?", (body, post_id)).rowcount != 1:
                raise ValueError("post not found")

    def delete_post(self, post_id):
        if type(post_id) is not int or post_id < 1:
            raise ValueError("invalid post id")
        with self._connect() as db:
            if db.execute("DELETE FROM posts WHERE id = ?", (post_id,)).rowcount != 1:
                raise ValueError("post not found")

    def list_posts(self, board_id, limit=50):
        if type(board_id) is not int or board_id < 1:
            raise ValueError("invalid board id")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be 1–100")
        with self._connect() as db:
            return [dict(row) for row in db.execute("SELECT id, board_id, author, body, created_at FROM posts WHERE board_id = ? ORDER BY id DESC LIMIT ?", (board_id, limit))]

    def send_mail(self, sender, recipient, body):
        sender = self._text(sender, "sender", 80)
        recipient = self._text(recipient, "recipient", 80)
        body = self._text(body, "mail", 4000)
        with self._connect() as db:
            cursor = db.execute("INSERT INTO mail (sender, recipient, body) VALUES (?, ?, ?)", (sender, recipient, body))
            return cursor.lastrowid

    def inbox(self, recipient, limit=50):
        recipient = self._text(recipient, "recipient", 80)
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be 1–100")
        with self._connect() as db:
            return [dict(row) for row in db.execute("SELECT id, sender, recipient, body, created_at FROM mail WHERE recipient = ? ORDER BY id DESC LIMIT ?", (recipient, limit))]

    def command(self, user, command):
        """Read-only commands only; writes require explicit application authorization."""
        user = self._text(user, "user", 80)
        command = self._text(command, "command", 200).lower().strip()
        if command in ("/help", "/menu"):
            return "Commands: /help, /menu, /boards, /inbox"
        if command == "/boards":
            boards = self.list_boards()
            return "\n".join(f"{board['id']}: {board['name']}" for board in boards) or "No boards yet."
        if command == "/inbox":
            return f"{len(self.inbox(user))} message(s) in inbox."
        return "Unknown command. Use /help."
