# STLCA: Seattle Tenant & Landlord Compliance Audit

**Live site:** https://seattletlca-justice.github.io/DATASETS_AND_DASHBOARDS/STLCA_Home.html

---

## What This Is

STLCA is an independent, non-partisan data analytics and oversight project. It analyzes publicly available City of Seattle enforcement records, specifically complaint data from the Seattle Department of Construction and Inspections (SDCI), to produce structured, verifiable assessments of how code compliance is documented, and where the public record cannot confirm that enforcement occurred.

This is not a tenant advocacy organization. It is an oversight project that presents verified findings from public data. The work contains no political asks and no calls to action. The data speaks on its own terms, measured against itself.

The methodology is fully transparent and independently replicable from Seattle's Open Data Portal.

---

## Data Sources

All data is sourced from the [Seattle Open Data Portal](https://data.seattle.gov) and is publicly available.

| Dataset | Records | Date Range | Notes |
|---|---|---|---|
| SDCI Complaint Records (primary) | 233,543 | 2003–2025 | Enriched with district assignments |
| Building Permits | Multiple exports | 2024–2026 | Split into parts for upload |
| Electrical Permits | Multiple exports | 2024–2026 | Split into parts for upload |
| Construction Permits | Snapshot 2026-01-27 | 2026 | |
| Conveyance Permits | Snapshot 2026-01-27 | 2026 | |
| RRIO Rental Registration | Annual files | 2015–2025 | Year-by-year exports |

### Primary File

`CITYWIDE_ALL_20251231_ENRICHED_01272025.csv`: 233,543 complaint records, 2003–2025, enriched with council district assignments. This is the authoritative source for all counts in this project.

**Note on unassigned records:** 2,671 records (1.1% of 233,543) could not be assigned to a council district in the SDCI source data; geocoding was not available for these addresses. These records are analyzed separately and excluded from all district-level counts.

---

## LLT Filter Definition

Landlord-Tenant (LLT) records are defined by the following rule applied to the `RecordTypeDesc` field:

```
RecordTypeDesc IS NULL
  OR RecordTypeDesc contains "Emergency"
  OR RecordTypeDesc contains "LandLord/Tenant"
```

**Total LLT records (2003–2025): 58,761**

This rule was derived from direct inspection of SDCI record type categories. An earlier narrow version of this filter (label match only) produces a count of 20,325, which is incorrect. All figures in this project use the corrected broad rule.

---

## Dataset Counts

*Verified 2026-03-02. Source: `FOUR_DATASETS.txt`.*

### All Records

| Window | Total | Complaints | NOV | Citations | Tenant Relocation | Unfit Building |
|---|---|---|---|---|---|---|
| 2003–2025 | 233,543 | 177,431 | 31,409 | 20,340 | 4,045 | 318 |
| 2015–2025 | 148,349 | 124,194 | 13,701 | 8,032 | 2,360 | 62 |

### LLT Only (Corrected Rule)

| Window | Total | Complaints | NOV | Citations | Tenant Relocation | Unfit Building |
|---|---|---|---|---|---|---|
| 2003–2025 | 58,761 | 41,653 | 11,341 | 1,404 | 4,045 | 318 |
| 2015–2025 | 46,108 | 35,867 | 6,867 | 952 | 2,360 | 62 |

### LLT by Council District (All Years, 2003–2025)

| District | Council Member | Total LLT | Complaints | NOV | Citations | Tenant Relocation | Unfit Building |
|---|---|---|---|---|---|---|---|
| D1 (West Seattle) | Saka | 8,015 | 5,341 | 1,900 | 187 | 510 | 77 |
| D2 (Southeast) | Lin | 9,353 | 6,337 | 2,245 | 295 | 417 | 59 |
| D3 (Capitol Hill) | Hollingsworth | 11,351 | 8,419 | 1,856 | 207 | 813 | 56 |
| D4 (Northeast) | Rivera | 7,033 | 4,816 | 1,431 | 228 | 522 | 36 |
| D5 (North) | Juarez | 7,595 | 5,296 | 1,552 | 187 | 526 | 34 |
| D6 (Northwest) | Strauss | 6,634 | 4,371 | 1,234 | 185 | 817 | 27 |
| D7 (Downtown/Kettle) | Moore | 8,094 | 6,513 | 1,051 | 98 | 410 | 22 |

---

## Key Findings

These findings are derived directly from the SDCI complaint records. They describe what the public record does and does not contain, not what any party intended.

- **62.3%** of all LLT complaint records have no inspection date in SDCI's own data.
- **59.8%** of closed LLT cases show no documented inspection result.
- **D7 (Downtown/Kettle):** 69.7% no inspection date; 67.2% closed with no documented result; 16.1% NOV rate - the worst documentation gap of any district.
- **D3 (Capitol Hill/Hollingsworth):** highest LLT total citywide (11,351 records); 411% growth from 2015 to 2025.
- **D7 LLT volume grew 745%** from 2015 to 2025, the fastest growth rate of any district in the city.
- Seattle has no independent oversight body for SDCI comparable to the Office of Inspector General for SPD.

---

## Repository Contents

### Dashboards and Reports

| File | Description |
|---|---|
| `STLCA_Home.html` | Homepage - entry point and index for all district and citywide dashboards |
| `CITYWIDE KPI.html` | Citywide enforcement audit dashboard |
| District_1_Dossier.html through District_7_Dossier.html | Per-district data dashboards: LLT counts, disparity metrics, trend charts, keyword analysis |
| D1_Accountability_Dossier.html through D7_Accountability_Dossier.html | Narrative accountability documents with verbatim SDCI complaint case studies |
| `STLCA_City_Auditor_Report_2026.html` | City auditor-style enforcement findings report |
| `STLCA_Citywide_Enforcement_Report_2026.html` | Citywide enforcement findings |
| `STLCA_Council_Static_Report.html` | Council briefing, static format |
| `STLCA_Public_Report_2026.html` | Public-facing findings document |

All HTML files are self-contained and open directly in any browser. No server required.

### Analysis Scripts

| File | Description |
|---|---|
| `SCRIPTS/all_districts_keyword_analysis.py` | Processes all 7 districts and unassigned records in a single pass; produces ALL and LLT Smart Analysis CSVs |
| `SCRIPTS/d7_keyword_analysis.py` | D7 keyword analysis (initial run) |
| `SCRIPTS/d7_keyword_drilldown.py` | Per-keyword hit counts for D7 |
| `SCRIPTS/build_dossiers.py` | Generates district data dossier HTML files |
| `SCRIPTS/build_narrative_dossiers.py` | Generates narrative accountability dossier HTML files |
| `SCRIPTS/stlca_classify_with_permits.py` | Cross-references complaints against permit records |

### Analysis Outputs (CSV)

| File Pattern | Description |
|---|---|
| `D{n}_ALL_Smart_Analysis.csv` | All records for district N tagged across 19 keyword categories (D1–D7) |
| `D{n}_LLT_Smart_Analysis.csv` | LLT-filtered records for district N with keyword tags (D1–D7) |
| `D{n}_LLT_ALL_HARM_AND_RISK.csv` | Harm and risk term analysis per district (D1–D7) |
| `UNASSIGNED_Smart_Analysis.csv` | The 2,671 records with no district geocode, analyzed separately |
| `KEYWORD_PIVOT.csv` | Citywide keyword category pivot |
| `CITY_VP_FULL_ANALYSIS.csv` | Citywide violation pattern full analysis |
| `CITY_VP_ADDRESS_SUMMARY.csv` | Per-address complaint summary |
| `CITY_VP_PROOFS.csv` | Verified proof records for violation patterns |
| `DISPLACEMENT_HABITABILITY_HITS.csv` | Records matching displacement and habitability keyword categories |
| `PROPERTY_MASTER_CONFLICTS.csv` | Properties with conflicting permit and complaint records |
| `RRIO_PROPERTY_TIMELINE_CLEAN.csv` | RRIO rental registration timeline by property |
| `STLCA_Problem_Properties_Full.csv` | Compiled problem property records |

### Reference Files

| File | Description |
|---|---|
| `FOUR_DATASETS.txt` | Verified record counts for all four primary data windows with LLT rule documentation |
| `REPORT_STATS.txt` | Key statistics referenced across reports |
| `DISPLACEMENT_SUMMARY.txt` | Displacement-related findings summary |
| `RULEBOOK_KPI.txt` | KPI definitions and calculation rules |

### RRIO Rental Registration Data

Annual registration CSV files (2015–2025), sourced directly from the Seattle Open Data Portal. Used to cross-reference complaint properties against registered rental units.

### Permit Data

Building, electrical, construction, and conveyance permit exports from SDCI. Split into parts for upload due to file size. Used to cross-reference complaint properties against active permits and identify permit-complaint conflicts.

---

## Keyword Analysis Methodology

Keyword tagging applies two-stage matching to complaint `Description` text fields:

1. **spaCy lemmatization** (`en_core_web_sm`): normalizes verb forms and plurals before matching
2. **rapidfuzz fuzzy matching** (threshold: 85): catches spelling variations and transcription errors common in SDCI complaint text

**19 issue categories are tagged per record:**

| Category | Category | Category |
|---|---|---|
| No_Heat | No_Hot_Water | Gas_Shutoff |
| HAB | EVIC | DISP |
| RENT | PERMIT | LEGAL |
| Plumbing | Mold | Pests |
| Appliances | Electrical | Fire_Safety |
| Structural | Trash_Site | Tenant_Rights |
| Security_Retaliation | | |

Each output CSV contains binary tag columns for all 19 categories alongside the original SDCI record fields.

**Runtime:** Python 3.12, polars, spaCy, rapidfuzz, tqdm.

---

## Reproducing This Analysis

All source data is publicly available on the [Seattle Open Data Portal](https://data.seattle.gov). The LLT filter rule, district breakdowns, and keyword methodology are fully documented in this repository.

To reproduce the keyword analysis outputs, with the primary CSV in place:

```bash
python SCRIPTS/all_districts_keyword_analysis.py
```

This script reads `CITYWIDE_ALL_20251231_ENRICHED_01272025.csv` and produces per-district ALL and LLT Smart Analysis CSVs plus the unassigned records file.

---

## Scope and Limitations

- **This project does not determine causation.** It identifies what is and is not present in the public record.
- **Where an inspection date or result is absent from the SDCI record, this project reports it as absent.** No inference is made about whether activity occurred outside the public record. The absence of documentation is itself the finding.
- **Address matching between datasets uses normalized exact matching.** Formatting differences (e.g., "AVE" vs "AVENUE", unit number variations) may cause some records to fail matching. Affected counts are noted where material.
- **Permit data is partial.** Large permit files were split for upload; all parts are included in the repository. Any analysis noting partial permit coverage is flagged.
- **RRIO snapshot data reflects registration status at export date.** Status may have changed subsequently.

---

## What This Project Is Not

- This project is not affiliated with the City of Seattle, SDCI, or any City department.
- This project is not a tenant union, advocacy organization, or legal services provider.
- This project does not make referrals, provide legal advice, or represent any party in any proceeding.
- The findings described here reflect what is documented in the public record. They do not constitute legal conclusions about any individual landlord, property, or complaint.

---

*STLCA: Seattle Tenant & Landlord Compliance Audit*
*Data current through December 31, 2025. Last updated March 2026.*
*All source data is public record, available at data.seattle.gov.*
