import ast
import unittest
from pathlib import Path


class DesktopSourceTests(unittest.TestCase):
    def test_desktop_module_parses(self):
        path = Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py"
        ast.parse(path.read_text(encoding="utf-8"))

    def test_no_network_or_radio_imports_in_preview(self):
        path = Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imported += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        for forbidden in ("socket", "meshtastic", "paho", "requests"):
            self.assertNotIn(forbidden, imported)


if __name__ == "__main__":
    unittest.main()
