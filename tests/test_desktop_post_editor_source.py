import ast
import unittest
from pathlib import Path

class DesktopPostEditorTests(unittest.TestCase):
    def test_post_editor_has_explicit_save_handler(self):
        source = (Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py").read_text()
        tree = ast.parse(source)
        self.assertTrue(any(isinstance(node, ast.FunctionDef) and node.name == "save_local_post" for node in ast.walk(tree)))
        self.assertIn('BulletinBoard(database).post(', source)
        self.assertIn('post_editor.get("1.0", "end-1c")', source)
        self.assertIn('show_posts()', source)

if __name__ == "__main__":
    unittest.main()
