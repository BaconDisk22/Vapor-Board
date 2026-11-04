import ast
import unittest
from pathlib import Path

class DesktopRadioSourceTests(unittest.TestCase):
    def test_controls_and_safe_status(self):
        source = (Path(__file__).resolve().parents[1] / "vapor_board" / "desktop.py").read_text()
        ast.parse(source)
        self.assertIn("RadioWorker()", source)
        self.assertIn("worker.stop()", source)
        self.assertIn("protocol_verified=verified[0]", source)
        self.assertIn("root.after(100, poll_radio)", source)

if __name__ == "__main__": unittest.main()
