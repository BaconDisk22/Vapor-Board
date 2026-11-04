import ast
import unittest
from pathlib import Path

class LocalBoardCreationSourceTests(unittest.TestCase):
    def test_local_board_creation_is_explicit(self):
        source = (Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py").read_text()
        ast.parse(source)
        self.assertIn("def create_local_board():", source)
        self.assertIn("BulletinBoard(database).create_board(board_name.get())", source)
        self.assertIn("database.parent.mkdir", source)

if __name__ == "__main__": unittest.main()
