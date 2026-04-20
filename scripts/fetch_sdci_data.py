from __future__ import annotations

import csv
import datetime as dt
import os
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

COMPLAINTS_URL = os.getenv(
    "SDCI_COMPLAINTS_URL",
    "https://cos-data.seattle.gov/api/views/ez4a-iug7/rows.csv?accessType=DOWNLOAD",
)
RRIO_URL = os.getenv(
    "SDCI_RRIO_URL",
    "https://cos-data.seattle.gov/api/views/j2xh-c7vt/rows.csv?accessType=DOWNLOAD",
)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
AS_OF_DATE = dt.date(2025, 12, 31)
REQUEST_TIMEOUT = 120
USER_AGENT = "stlca-sdci-pipeline/1.0"

COMPLAINT_FIELDNAMES = [
    "case_number",
    "record_type",
    "record_type_mapped",
    "complaint_type",
    "description",
    "status",
    "status_date",
    "opened_date",
    "last_inspection_date",
    "last_inspection_result",
    "closed_date",
    "address",
    "city",
    "state",
    "zip",
    "parcel_id",
    "council_district",
    "lat",
    "lon",
    "source_url",
]

RRIO_FIELDNAMES = [
    "registration_num",
    "registered_type",
    "registered_type_desc",
    "registration_status",
    "status_date",
    "registration_effective_date",
    "registration_expiration_date",
    "inspection_date",
    "last_inspection_result",
    "address",
    "city",
    "state",
    "zip",
    "parcel_id",
    "council_district",
    "units_registered",
    "lat",
    "lon",
    "source_url",
]

CLOSED_STATUSES = {
    "completed",
    "closed",
    "withdrawn",
    "admin closure",
    "compliance achieved",
}


def fetch_rows(url: str) -> list[dict[str, str]]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        text = response.read().decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    return [dict(row) for row in reader]


def first_existing(row: dict[str, str], candidates: Iterable[str]) -> str:
    lowered = {key.lower(): key for key in row}
    for candidate in candidates:
        match = lowered.get(candidate.lower())
        if match is not None:
            return row.get(match, "") or ""
    return ""


def parse_date(value: str) -> dt.date | None:
    if not value:
        return None

    cleaned = value.strip()
    if not cleaned:
        return None

    normalized = cleaned.replace("Z", "+00:00")
    iso_candidates: list[str] = [normalized]
    if "T" in normalized:
        iso_candidates.append(normalized.split("T", 1)[0])

    for candidate in iso_candidates:
        try:
            return dt.date.fromisoformat(candidate)
        except ValueError:
            try:
                return dt.datetime.fromisoformat(candidate).date()
            except ValueError:
                continue

    for fmt in (
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%y %I:%M:%S %p",
        "%Y %b %d %I:%M:%S %p",
        "%Y %B %d %I:%M:%S %p",
    ):
        try:
            return dt.datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    return None


def iso_date(value: str) -> str:
    parsed = parse_date(value)
    return parsed.isoformat() if parsed else ""


def string_flag(value: bool) -> str:
    return "true" if value else "false"


def normalize_number(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        return ""
    try:
        return str(float(cleaned)).rstrip("0").rstrip(".")
    except ValueError:
        return cleaned


def normalize_complaints(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized_rows: list[dict[str, str]] = []
    for row in rows:
        normalized_rows.append(
            {
                "case_number": first_existing(row, ["recordnum", "case_number"]),
                "record_type": first_existing(row, ["recordtype", "record_type"]),
                "record_type_mapped": first_existing(row, ["recordtypemapped", "record_type_mapped"]),
                "complaint_type": first_existing(row, ["recordtypedesc", "complaint_type"]),
                "description": first_existing(row, ["description"]),
                "status": first_existing(row, ["statuscurrent", "status"]),
                "status_date": iso_date(first_existing(row, ["statusdate", "status_date", "currentstatusdate"])),
                "opened_date": iso_date(first_existing(row, ["opendate", "opened_date"])),
                "last_inspection_date": iso_date(first_existing(row, ["lastinspdate", "last_inspection_date"])),
                "last_inspection_result": first_existing(row, ["lastinspresult", "last_inspection_result"]),
                "closed_date": iso_date(first_existing(row, ["closeddate", "closed_date", "completeddate"])),
                "address": first_existing(row, ["originaladdress1", "address", "address1"]),
                "city": first_existing(row, ["originalcity", "city"]),
                "state": first_existing(row, ["originalstate", "state"]),
                "zip": first_existing(row, ["originalzip", "zip"]),
                "parcel_id": first_existing(row, ["parcelno", "parcelnumber", "parcel_id", "parcel"]),
                "council_district": first_existing(row, ["councildistrict", "council_district"]),
                "lat": normalize_number(first_existing(row, ["latitude", "lat", "ycoord"])),
                "lon": normalize_number(first_existing(row, ["longitude", "lon", "xcoord"])),
                "source_url": COMPLAINTS_URL,
            }
        )
    return normalized_rows


def normalize_rrio(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized_rows: list[dict[str, str]] = []
    for row in rows:
        normalized_rows.append(
            {
                "registration_num": first_existing(row, ["permitnum", "registrationnum", "registration_num"]),
                "registered_type": first_existing(row, ["permittypemapped", "registeredtypemapped"]),
                "registered_type_desc": first_existing(row, ["permittypedesc", "registeredtypedesc"]),
                "registration_status": first_existing(row, ["statuscurrent", "registrationstatus", "status"]),
                "status_date": iso_date(first_existing(row, ["statusdate", "status_date", "currentstatusdate"])),
                "registration_effective_date": iso_date(
                    first_existing(row, ["applicationdate", "registrationeffectivedate", "issueddate", "issued_date"])
                ),
                "registration_expiration_date": iso_date(
                    first_existing(row, ["expirationdate", "registrationexpirationdate", "expiresdate", "expires_date"])
                ),
                "inspection_date": iso_date(first_existing(row, ["lastinspdate", "inspectiondate", "inspection_date"])),
                "last_inspection_result": first_existing(row, ["lastinspresult", "inspectionresult"]),
                "address": first_existing(row, ["originaladdress1", "address", "address1"]),
                "city": first_existing(row, ["originalcity", "city"]),
                "state": first_existing(row, ["originalstate", "state"]),
                "zip": first_existing(row, ["originalzip", "zip"]),
                "parcel_id": first_existing(row, ["parcelno", "parcelnumber", "parcel_id", "parcel"]),
                "council_district": first_existing(row, ["councildistrict", "council_district"]),
                "units_registered": normalize_number(
                    first_existing(row, ["unitsregistered", "numberofunits", "units_registered"])
                ),
                "lat": normalize_number(first_existing(row, ["latitude", "lat", "ycoord"])),
                "lon": normalize_number(first_existing(row, ["longitude", "lon", "xcoord"])),
                "source_url": RRIO_URL,
            }
        )
    return normalized_rows


def complaints_as_of(rows: list[dict[str, str]], cutoff: dt.date) -> list[dict[str, str]]:
    snapshot: list[dict[str, str]] = []
    for row in rows:
        opened_date = parse_date(row.get("opened_date", ""))
        closed_date = parse_date(row.get("closed_date", ""))
        status_date = parse_date(row.get("status_date", ""))
        status = (row.get("status", "") or "").strip().lower()

        opened_by_cutoff = opened_date is not None and opened_date <= cutoff
        closed_by_cutoff = closed_date is not None and closed_date <= cutoff
        closed_by_status = status in CLOSED_STATUSES and status_date is not None and status_date <= cutoff

        snapshot_row = dict(row)
        snapshot_row["active_as_of"] = string_flag(opened_by_cutoff and not (closed_by_cutoff or closed_by_status))
        snapshot_row["as_of_date"] = cutoff.isoformat()
        snapshot.append(snapshot_row)
    return snapshot


def rrio_as_of(rows: list[dict[str, str]], cutoff: dt.date) -> list[dict[str, str]]:
    snapshot: list[dict[str, str]] = []
    for row in rows:
        effective = parse_date(row.get("registration_effective_date", ""))
        expiration = parse_date(row.get("registration_expiration_date", ""))
        active = effective is not None and effective <= cutoff and (expiration is None or expiration >= cutoff)

        snapshot_row = dict(row)
        snapshot_row["registration_active_as_of"] = string_flag(active)
        snapshot_row["as_of_date"] = cutoff.isoformat()
        snapshot.append(snapshot_row)
    return snapshot


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_outputs(output_dir: Path) -> None:
    complaints = normalize_complaints(fetch_rows(COMPLAINTS_URL))
    write_csv(output_dir / "complaints_latest.csv", COMPLAINT_FIELDNAMES, complaints)
    write_csv(
        output_dir / f"complaints_asof_{AS_OF_DATE.isoformat()}.csv",
        COMPLAINT_FIELDNAMES + ["active_as_of", "as_of_date"],
        complaints_as_of(complaints, AS_OF_DATE),
    )

    rrio = normalize_rrio(fetch_rows(RRIO_URL))
    write_csv(output_dir / "rrio_latest.csv", RRIO_FIELDNAMES, rrio)
    write_csv(
        output_dir / f"rrio_asof_{AS_OF_DATE.isoformat()}.csv",
        RRIO_FIELDNAMES + ["registration_active_as_of", "as_of_date"],
        rrio_as_of(rrio, AS_OF_DATE),
    )


def main() -> None:
    export_outputs(OUTPUT_DIR)


if __name__ == "__main__":
    main()
