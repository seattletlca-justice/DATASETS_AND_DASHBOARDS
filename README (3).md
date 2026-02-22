# STLCA — Seattle Housing Enforcement Audit
## Public Records Analysis | February 2026

> **Seattle Tenants & Landlord Code Accountability (STLCA)**  
> Analysis of SDCI complaint records, RRIO registration data, and city permit files.  
> All source data obtained via public records request and Seattle Open Data Portal.

---

## What This Is

A data-driven audit of Seattle's Department of Construction and Inspections (SDCI) enforcement record, specifically examining how landlord/tenant complaints are documented, closed, and cross-referenced against rental registration and permit activity.

**Core finding:** 43.8% of all closed CP complaints citywide (73,212 records) have zero inspection documentation — no date, no result, nothing. For landlord/tenant cases the rate is 76.1%. The failure is not partial logging. It is total absence.

---

## Dashboard Suite

Six self-contained HTML files. Open in any browser. No server required.

| File | What It Shows |
|------|--------------|
| `STLCA_Verified_Audit_v6.html` | Main audit — verified vs unverified closures by district, L/T toggle, pre/post 2018 collapse, top 10 worst properties |
| `SDCI_NOV_Conversion_Collapse.html` | NOV issuance rate by year 2003–2025. Collapsed from ~15% to 6.1% in 2025 |
| `SDCI_Impossible_Chronology.html` | 40,328 records where inspection date precedes complaint open date — data integrity failure |
| `SDCI_RRIO_CrossReference.html` | Complaint data matched against RRIO registration — 4,803 unregistered properties with L/T complaints |
| `SDCI_Permit_Complaint_Disparity.html` | Permit vs complaint verification rate gap — LT complaints 40pp more likely to be closed unverified than non-LT complaints at same permitted addresses |

---

## Data Files

### JSON (analysis outputs)

| File | Contents | Size |
|------|----------|------|
| `STLCA_MASTER_DATA.json` | All findings in one file — complaint audit, NOV trend, RRIO crossref, permit disparity | ~67 KB |
| `rrio_summary.json` | RRIO registration counts by district and status | ~1 KB |
| `complaint_summary.json` | CP complaint counts, verified/unverified rates by district | ~1 KB |
| `permit_summary.json` | Permit counts by type, status, class | ~1 KB |

### Source Data (not in repo — large files)

| File | Source | Size | Notes |
|------|--------|------|-------|
| `District_1-7_ALL_ENRICHED.csv` | SDCI via public records | ~110 MB total | CP records 2003–2025, enriched with district assignment and LT classification |
| `RRIO_PROPERTY_TIMELINE_CLEAN.csv` | Seattle Open Data / SDCI | 77.8 MB | 656,510 rows, 21 columns, deduped and cleaned |
| `PERMITS_Building_Permits_20260206.csv` | Seattle Open Data | 92 MB | Partial — parts 1-2 not analyzed |
| `PERMITS_Electrical_Permits_20260206.csv` | Seattle Open Data | 179 MB | All 7 parts analyzed |
| `PERMITS_Land_Use_Permits_20260206.csv` | Seattle Open Data | 12 MB | Fully analyzed |
| `PERMITS_CONSTRUCTION_PERMITS_20260127.csv` | Seattle Open Data | 17 MB | Fully analyzed |
| `PERMITS_CONVEYANCE_PERMITS_20260127.csv` | Seattle Open Data | 2 MB | Fully analyzed |
| `PERMITS_Issued_Building_Permits_20260206.csv` | Seattle Open Data | 1 MB | Fully analyzed |

---

## Methodology

### Complaint Classification
- **CP records** — filtered to complaint type only (CP = True)
- **L/T classification** — explicit `LandLord/Tenant` RecordTypeDesc, plus keyword reclassification of blank/emergency types matching: `tenant, landlord, renter, rental, rent, lease, evict, trao, treo, pota, habitab, no heat, no water, bed bug, roach, mold, unfit, notice to vacate, lockout, deposit, housing code`
- **Verified** — Closed/Completed status AND both `LastInspDate` AND `LastInspResult` present
- **Unverified** — Closed/Completed status with missing date OR missing result (or both)

### RRIO Cross-Reference
- Address matching: exact match on normalized uppercase `ORIGINALADDRESS1`
- **Unregistered** — address in complaint data with no matching RRIO entry
- **Expired** — RRIO record present, `REGISTRATION_EXPIRED = REGISTRATION EXPIRED`, no active record
- **Late Violation** — `RECORD_TYPE = RENTAL PROPERTY LATE REGISTRATION VIOLATION`
- **Private Inspector** — `PRIVATE_INSPECTOR = PRIVATE INSPECTOR`

### Permit Cross-Reference
- Address matching: exact match on normalized uppercase `Address`
- **Active permit** — Status in: Issued, Application Completed, Reviews In Process, Scheduled, Ready for Issuance, Awaiting Information, Ready for Intake, Reviews Completed, Additional Info Requested, Corrections Required
- **Permit coverage is partial** — Building_20260206 parts 1–2 not yet analyzed. Numbers will shift with full dataset.

### Pre/Post 2018 Split
- 2018 chosen as threshold based on observed structural change in documentation rates
- Pre-2018: 14.4% unverified citywide / 16.9% L/T
- Post-2018: 67.3% unverified citywide / 90.8% L/T
- This is not a legacy data problem. Post-2018 data is recent and should be fully documented.

### NOV Conversion Rate
- `NOV rate = NOV Issued records / total CP complaints` by year
- 2025: 6.1% (959 NOVs / 15,711 CP complaints)
- Peak year identified in dashboard

### Impossible Chronology
- Flag: `LastInspDate < OpenDate`
- 40,328 records citywide where inspection is recorded before the complaint existed
- Disqualifies these records from use in enforcement proceedings

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Total CP complaints analyzed | 230,872 |
| Closed without any inspection record | 73,212 (43.8%) |
| L/T complaints closed unverified | 76.1% |
| Post-2018 L/T complaints closed unverified | 90.8% |
| NOV issuance rate 2025 | 6.1% |
| Impossible chronology records | 40,328 |
| Unregistered properties with L/T complaints | 4,803 |
| LT unverified rate at permitted addresses | 77.4% |
| Non-LT unverified rate at same addresses | 37.3% |
| Gap | **40.1 percentage points** |

---

## Tools Used

All analysis performed with Python (csv, collections, json, re — stdlib only, no pandas).  
Dashboards: HTML/CSS/JavaScript with Plotly.js (CDN).  
Word documents: docx npm package.  
No external APIs. No proprietary software.

---

## Files Generated

### Processing Scripts
| Script | Purpose |
|--------|---------|
| `dedup_rrio.py` | Remove exact duplicate rows from RRIO files |
| `clean_rrio_columns.py` | Drop sanity-check/pipeline columns from RRIO_PROPERTY_TIMELINE |
| `split_rrio_clean.py` | Split 77.8MB RRIO file into uploadable 25MB chunks |
| `chunk_permits.py` | Split large permit files into uploadable chunks |

---

## Limitations & Caveats

- **Permit data is partial.** Building_20260206 parts 1–2 missing from permit cross-reference. Full dataset will shift numbers.
- **Address matching is exact.** Fuzzy matching not applied. Some addresses may fail to match due to formatting differences (e.g., "AVE" vs "AVENUE", unit numbers). Unregistered count may be slightly overstated.
- **LT keyword classification** is conservative. Some L/T complaints may be missed; some non-LT complaints may be included. Error rate estimated low given explicit RecordTypeDesc anchor.
- **RRIO timeline data** is a snapshot. Registration status may have changed since export date.
- **This analysis does not determine causation.** It identifies patterns in public records. The inference that permit revenue incentivizes differential enforcement is supported by the data but requires further investigation.

---

*Analysis by STLCA — Seattle Tenants & Landlord Code Accountability*  
*February 2026 | All source data is public record*
