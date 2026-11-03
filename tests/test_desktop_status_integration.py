import ast
import unittest
from pathlib import Path

class DesktopStatusIntegrationTests(unittest.TestCase):
    def test_desktop_uses_status_snapshot(self):
        source = (Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py").read_text()
        ast.parse(source)
        self.assertIn("StatusSnapshot().footer", source)
        self.assertNotIn("Radio: NOT CONNECTED  |  TX:", source)

if __name__ == "__main__": unittest.main()
