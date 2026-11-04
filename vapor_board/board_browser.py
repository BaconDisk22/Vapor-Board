"""Read-only desktop data model for an existing local BBS database."""
from .local_operator import inspect_database

class BoardBrowser:
    def __init__(self, database_path):
        self.database_path = database_path

    def boards(self):
        return inspect_database(self.database_path)["boards"]

    def posts(self, board_id):
        return inspect_database(self.database_path, board_id)["posts"]
