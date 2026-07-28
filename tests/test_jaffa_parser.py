"""Tests for JAFFA parser header compatibility."""

import unittest
from pathlib import Path

from fusion_report.parsers.jaffa import Jaffa

TEST_DATA_DIR = Path(__file__).parent / "test_data"


class TestJaffaParser(unittest.TestCase):
    """Validate JAFFA parser against old and new output headers."""

    def _parse_first_data_row(self, fixture_name: str):
        fixture_path = TEST_DATA_DIR / fixture_name
        parser = Jaffa()

        with fixture_path.open("r", encoding="utf-8") as fixture:
            parser.set_header(fixture.readline().strip())
            return parser.parse(fixture.readline().strip())[0]

    def test_parse_old_header_format(self):
        """Old JAFFA files with `known` column are still supported."""
        fusion_name, details = self._parse_first_data_row("jaffa.csv")

        self.assertEqual(fusion_name, "GOPC--ROS1")
        self.assertEqual(details["position"], "6:117566854:-#6:117321394:-")
        self.assertEqual(details["spanning_pairs"], 65)
        self.assertEqual(details["spanning_reads"], 11)
        self.assertEqual(details["classification"], "HighConfidence")
        self.assertEqual(details["known"], "Yes")

    def test_parse_new_header_format(self):
        """New JAFFA files without `known` are mapped using mitelman/cosmic columns."""
        fusion_name, details = self._parse_first_data_row("jaffa_new.csv")

        self.assertEqual(fusion_name, "GOPC--ROS1")
        self.assertEqual(details["position"], "6:117566854:-#6:117321394:-")
        self.assertEqual(details["known"], "Yes")
        self.assertEqual(details["geneCounts1"], "4")
        self.assertEqual(details["geneCounts2"], "5")
        self.assertEqual(details["known_mitelman"], "No")
        self.assertEqual(details["known_cosmic"], "Yes")
        self.assertEqual(details["cosmic_tier"], "1")
        self.assertEqual(details["gtex_samples"], "0")

    def test_parse_double_colon_fusion_delimiter(self):
        """Newer JAFFA outputs using '::' separators are parsed correctly."""
        fixture_path = TEST_DATA_DIR / "jaffa_new.csv"
        parser = Jaffa()

        with fixture_path.open("r", encoding="utf-8") as fixture:
            parser.set_header(fixture.readline().strip())
            row = fixture.readline().strip().replace("GOPC:ROS1", "GOPC::ROS1", 1)

        fusion_name, details = parser.parse(row)[0]

        self.assertEqual(fusion_name, "GOPC--ROS1")
        self.assertEqual(details["known"], "Yes")


if __name__ == "__main__":
    unittest.main()
