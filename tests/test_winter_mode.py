"""Static checks for BrioWil winter-mode integration logic."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "briowil"

class WinterModeTests(unittest.TestCase):
    def test_python_syntax(self):
        for path in ROOT.glob("*.py"):
            ast.parse(path.read_text(), filename=str(path))

    def test_coordinator_skips_tcp_during_winter(self):
        content = (ROOT / "coordinator.py").read_text()
        self.assertIn("if self.is_winter_mode:", content)
        self.assertIn("return None", content)
        self.assertIn("WINTER_MODE_ENTITY_ID", content)

    def test_helper_creation_and_listener(self):
        content = (ROOT / "__init__.py").read_text()
        self.assertIn("InputBoolean.from_yaml", content)
        self.assertIn("async_track_state_change_event", content)
        self.assertIn("async_set_updated_data(None)", content)

    def test_all_platforms_unavailable(self):
        for name in ("light.py", "sensor.py", "select.py", "number.py"):
            content = (ROOT / name).read_text()
            self.assertIn("self.coordinator.is_winter_mode", content, name)

    def test_compatible_input_boolean_component_access(self):
        content = (ROOT / "__init__.py").read_text()
        self.assertIn("DATA_INSTANCES", content)
        self.assertIn("input_boolean_component.async_add_entities", content)
        self.assertIn("input_boolean_component.async_remove_entity", content)
        self.assertNotIn("from homeassistant.components.input_boolean.const import DATA_INPUT_BOOLEAN", content)

