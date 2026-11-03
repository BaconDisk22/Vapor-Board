import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PackagingTests(unittest.TestCase):
    def test_entry_imports_package_main(self):
        source = (ROOT / "packaging" / "desktop_entry.py").read_text()
        tree = ast.parse(source)
        self.assertTrue(any(isinstance(node, ast.ImportFrom) and node.module == "vapor_board.desktop" for node in ast.walk(tree)))
    def test_build_targets_intel(self):
        source = (ROOT / "packaging" / "build_macos_intel.sh").read_text()
        self.assertIn('x86_64', source)
        self.assertIn('packaging/desktop_entry.py', source)
        self.assertIn('Vapor-Board-Intel.dmg', source)

if __name__ == "__main__": unittest.main()
