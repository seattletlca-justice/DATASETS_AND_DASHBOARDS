import datetime as dt
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fetch_sdci_data.py"
SPEC = importlib.util.spec_from_file_location("fetch_sdci_data", MODULE_PATH)
fetch_sdci_data = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(fetch_sdci_data)


class ParseDateTests(unittest.TestCase):
    def test_parse_iso_date(self) -> None:
        self.assertEqual(fetch_sdci_data.parse_date("2020-09-16"), dt.date(2020, 9, 16))

    def test_parse_slash_date(self) -> None:
        self.assertEqual(fetch_sdci_data.parse_date("09/16/2020"), dt.date(2020, 9, 16))

    def test_parse_seattle_export_timestamp(self) -> None:
        self.assertEqual(fetch_sdci_data.parse_date("2020 Sep 16 12:00:00 AM"), dt.date(2020, 9, 16))

    def test_parse_uppercase_month_timestamp(self) -> None:
        self.assertEqual(fetch_sdci_data.parse_date("2017 SEP 28 12:00:00 AM"), dt.date(2017, 9, 28))


if __name__ == "__main__":
    unittest.main()
