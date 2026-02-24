#!/usr/bin/env python3
"""Build timeline-bucket datasets for closed complaints missing inspection dates.

Scans District_*_ALL_ENRICHED.json files and exports rows that are:
- RecordType complaint (when CP flag exists),
- StatusCurrent in Closed/Completed,
- LastInspDate blank.

Output columns are arranged for manual status-tab transcription in the SDCI portal.
"""

from __future__ import annotations

import csv
import glob
import json
from pathlib import Path

PORTAL_SEARCH_URL = "https://cosaccela.seattle.gov/Portal/cap/CapHome.aspx?module=SDCI&TabName=SDCI"

OUTPUT_COLUMNS = [
    "district_file",
    "RecordNum",
    "District",
    "StatusCurrent",
    "status_link",
    "intake_date",
    "intake_by",
    "assigned_date",
    "assigned_to",
    "initial_investigation",
    "initial_investigation_date",
    "initial_investigation_by",
    "pota_insp",
    "pota_insp_date",
    "pota_insp_by",
    "closed_date",
    "closed_by",
    "result_bucket",
    "timeline_notes",
]


def is_closed_status(value: str) -> bool:
    return value.strip().lower() in {"closed", "completed"}


def is_blank(value: object) -> bool:
    if value is None:
        return True
    return str(value).strip() == ""


def load_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_output_rows(source_file: Path, rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        status = str(row.get("StatusCurrent", "")).strip()
        if not is_closed_status(status):
            continue

        if not is_blank(row.get("LastInspDate")):
            continue

        cp_flag = str(row.get("CP", "True")).strip().lower()
        if cp_flag not in {"true", "1", "yes"}:
            continue

        rec = str(row.get("RecordNum", "")).strip()
        out.append(
            {
                "district_file": source_file.name,
                "RecordNum": rec,
                "District": str(row.get("District", "")).strip(),
                "StatusCurrent": status,
                "status_link": PORTAL_SEARCH_URL,
                "intake_date": str(row.get("OpenDate", "")).strip(),
                "intake_by": "",
                "assigned_date": "",
                "assigned_to": "",
                "initial_investigation": "",
                "initial_investigation_date": "",
                "initial_investigation_by": "",
                "pota_insp": "",
                "pota_insp_date": "",
                "pota_insp_by": "",
                "closed_date": "",
                "closed_by": "",
                "result_bucket": "",
                "timeline_notes": "Use RecordNum in SDCI portal Status tab; expand arrows for who/what/when/result.",
            }
        )
    return out


def main() -> None:
    files = sorted(Path(p) for p in glob.glob("District_*_ALL_ENRICHED.json"))
    if not files:
        raise SystemExit("No District_*_ALL_ENRICHED.json files found.")

    all_rows: list[dict] = []
    for file in files:
        rows = load_rows(file)
        all_rows.extend(build_output_rows(file, rows))

    all_rows.sort(key=lambda r: (r["District"], r["RecordNum"]))

    out_path = Path("closed_no_inspection_timeline_buckets.csv")
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Wrote {len(all_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
