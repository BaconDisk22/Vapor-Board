import ast
import unittest
from pathlib import Path

class PostFormattingTests(unittest.TestCase):
    def test_post_separator_is_newline_escape_not_literal_backslash(self):
        source = (Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py").read_text()
        tree = ast.parse(source)
        inserts = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "insert"]
        self.assertTrue(any(isinstance(arg, ast.Constant) and arg.value == chr(10) * 2 for node in inserts for arg in node.args))
        self.assertNotIn(chr(92) * 2 + "n" + chr(92) * 2 + "n", source)

if __name__ == "__main__": unittest.main()
