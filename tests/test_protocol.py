"""Static regression checks; not a replacement for real-controller tests."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "briowil"

class ProtocolTests(unittest.TestCase):
    def test_status_offsets(self):
        tree = ast.parse((ROOT / "coordinator.py").read_text())
        indexes = {
            ast.unparse(n.slice)
            for n in ast.walk(tree)
            if isinstance(n, ast.Subscript)
            and isinstance(n.value, ast.Name)
            and n.value.id == "response"
        }
        for index in ("33", "64:66", "70", "71"):
            self.assertIn(index, indexes)

    def test_commands(self):
        light = (ROOT / "light.py").read_text()
        speed = (ROOT / "select.py").read_text()
        for keyword in ("sprj", "prcn", "plum"):
            self.assertIn(keyword, light)
        self.assertIn("pspd", speed)

    def test_program_preservation(self):
        code = (ROOT / "light.py").read_text()
        self.assertIn("current_color_number", code)
        self.assertIn("send_color_program", code)

    def test_color_hex_sensor_mapping(self):
        self.assertIn('"color_hex": color_hex', (ROOT / "coordinator.py").read_text())

if __name__ == "__main__":
    unittest.main()
