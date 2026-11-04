import ast
import unittest
from pathlib import Path

class PostFormattingTests(unittest.TestCase):
    def test_post_separator_is_newline_escape_not_literal_backslash(self):
        source = (Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py").read_text()
        tree = ast.parse(source)
        joins = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join"]
        self.assertTrue(any(isinstance(node.func.value, ast.Constant) and node.func.value.value == "\\n\\n" for node in joins))

if __name__ == "__main__": unittest.main()
