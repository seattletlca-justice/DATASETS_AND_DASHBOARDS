# DATASETS_AND_DASHBOARDS
PAYLOAD GENERATOR
STLCA — Seattle Tenant & Landlord Compliance Audit

**Live Site:**
[https://seattletlca-justice.github.io/DATASETS_AND_DASHBOARDS/STLCA_Home.html](https://seattletlca-justice.github.io/DATASETS_AND_DASHBOARDS/STLCA_Home.html)

---

## Overview

STLCA is an independent, non-partisan data oversight project analyzing publicly available enforcement records from the Seattle Department of Construction and Inspections (SDCI).

It measures SDCI’s own complaint dataset against itself to identify:

• What is documented in the public record
• What is not documented in the public record

The project makes no political recommendations and no legal conclusions. It reports only what the structured data fields do and do not contain.

All findings are derived from public data and are independently reproducible.

---

## Core Dataset

**Primary File**
`CITYWIDE_ALL_20251231_ENRICHED_01272025.csv`
233,543 complaint records
2003–2025
Enriched with council district assignments

This file is the authoritative source for all counts referenced in STLCA dashboards and reports.

**Unassigned Records**
2,671 records (1.1%) could not be geocoded to a council district in the SDCI source data.
These are analyzed separately and excluded from district-level calculations.

---

## LLT Classification Rule

Landlord-Tenant (LLT) records are defined using the `RecordTypeDesc` field:

```
RecordTypeDesc IS NULL
OR RecordTypeDesc contains "Emergency"
OR RecordTypeDesc contains "LandLord/Tenant"
```

Total LLT records (2003–2025): **58,761**

An earlier narrow label-based filter produced 20,325 records and was determined to be incomplete. All dashboards use the corrected rule.

---

## Verified Dataset Counts

### All Records — 2003–2025

| Total   | Complaints | NOV    | Citations | Tenant Relocation | Unfit Building |
| ------- | ---------- | ------ | --------- | ----------------- | -------------- |
| 233,543 | 177,431    | 31,409 | 20,340    | 4,045             | 318            |

### LLT Only — 2003–2025

| Total  | Complaints | NOV    | Citations | Tenant Relocation | Unfit Building |
| ------ | ---------- | ------ | --------- | ----------------- | -------------- |
| 58,761 | 41,653     | 11,341 | 1,404     | 4,045             | 318            |

Counts verified March 2, 2026.

---

## Key Documentation Findings

These findings describe structured data fields — not intent and not causation.

• 62.3% of LLT records contain no inspection date
• 59.8% of closed LLT cases contain no documented inspection result
• LLT volumes increased significantly between 2015–2025 across multiple districts
• Seattle has no independent oversight body for SDCI comparable to the Office of Inspector General for SPD

Where documentation is absent, STLCA reports it as absent. No inference is made about activity outside the public record.

---

## Data Sources

All datasets are publicly available via data.seattle.gov.

Primary sources include:

• SDCI Complaint Records (2003–2025)
• RRIO Rental Registration (2015–2025)
• Building, Electrical, Construction, and Conveyance Permits

Permit files were split for upload due to file size. All parts are included.

---

## Keyword Analysis Method

Complaint descriptions are analyzed using:

1. spaCy lemmatization (`en_core_web_sm`)
2. rapidfuzz fuzzy matching (threshold 85)

Nineteen issue categories are tagged per record, including:

Habitability, Plumbing, Mold, Eviction, Displacement, Electrical, Structural, No Heat, No Hot Water, Security, ADA Access, Rent, Illegal Unit, and others.

Each Smart Analysis CSV includes binary tag columns alongside original SDCI fields.

Environment:
Python 3.12
polars
spaCy
rapidfuzz

---

## Reproducing the Analysis

With the primary CSV in place:

```
python SCRIPTS/all_districts_keyword_analysis.py
```

This produces:

• Per-district ALL Smart Analysis files
• Per-district LLT Smart Analysis files
• Unassigned record analysis
• Citywide pivots

All scripts are included in the repository.

---

## Scope and Limitations

• STLCA does not determine causation.
• It does not assert that inspections did or did not occur.
• It reports whether inspection documentation appears in structured fields.
• Address matching uses normalized exact matching and may miss format variations.
• Permit data is partial but flagged where relevant.
• RRIO data reflects status at export date.

---

## Independence

STLCA is not affiliated with:

• The City of Seattle
• SDCI
• Any council office
• Any tenant or landlord organization

It does not provide legal advice or representation.

---

STLCA — Seattle Tenant & Landlord Compliance Audit
Data current through December 31, 2025
Last updated March 2026

All source data: data.seattle.gov
