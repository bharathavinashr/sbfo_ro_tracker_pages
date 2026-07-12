import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import normalize_division_value, serialize_division_value


class DivisionNormalizationTests(unittest.TestCase):
    def test_normalize_division_value_handles_legacy_string(self):
        self.assertEqual(normalize_division_value("Alcohol"), "Alcohol")

    def test_normalize_division_value_handles_multi_select_list(self):
        self.assertEqual(normalize_division_value(["Alcohol", "Non-Alcohol"]), ["Alcohol", "Non-Alcohol"])

    def test_serialize_division_value_stores_json_for_multi_select(self):
        self.assertEqual(serialize_division_value(["Alcohol", "Non-Alcohol"]), '["Alcohol","Non-Alcohol"]')

    def test_serialize_division_value_keeps_legacy_string(self):
        self.assertEqual(serialize_division_value("Alcohol"), "Alcohol")


if __name__ == "__main__":
    unittest.main()
