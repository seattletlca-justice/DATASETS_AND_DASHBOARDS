# Dashboard Traceability

## Scope
This dashboard analyzes Seattle SDCI housing-code records included in `payload.json`, with views for:
- `All Years`
- `2015-2025`
- `2025`

Geography is citywide plus district drill-down (`D1`–`D7`).

## Data files used by the dashboard
- `index.html` (published dashboard UI)
- `payload.json` (data payload loaded at runtime)

## Metric definitions
- **Complaints (-CP)**: `RecordNum` ending in `-CP`.
- **NOVs (-VI)**: `RecordNum` ending in `-VI`.
- **% NOV per Complaint**: `NOVs / Complaints * 100`.
- **Missing inspection date**: no `LastInspDate` or flagged “No Inspection Date”.
- **Closed/Completed with no inspection date**: status is exactly `Closed` or `Completed` and inspection date is missing.

## District consistency checks
Validation checks were run against `payload.json`.

### NOV-rate district rows vs citywide totals
| Time Range | District Complaint Sum | Citywide Complaints | Difference | District NOV Sum | Citywide NOVs | Difference |
|---|---:|---:|---:|---:|---:|---:|
| All Years | 175,171 | 177,431 | 2,260 | 31,130 | 31,409 | 279 |
| 2015-2025 | 122,650 | 124,194 | 1,544 | 13,536 | 13,701 | 165 |
| 2025 | 15,712 | 15,973 | 261 | 959 | 969 | 10 |

Interpretation: district sums are slightly lower than citywide totals, which indicates records without an assigned district (or out-of-scope district coding) are included in citywide totals but not in district breakout rows.

### NOV percentage formula integrity
For each district row, `%` matches `novs / complaints` (rounded to 2 decimals). No formula mismatches were detected.

## Repro command used for checks
```bash
python - <<'PY'
import json
from pathlib import Path
p=json.loads(Path('payload.json').read_text())
for tr,data in p.items():
    city=data.get('Citywide',{})
    rows=city.get('nov_rate_by_district',[])
    comp=sum(r.get('complaints',0) for r in rows)
    nov=sum(r.get('novs',0) for r in rows)
    t=city.get('totals',{})
    print(tr, comp, t.get('complaints'), nov, t.get('novs'))
PY
```
