# STLCA Master TODO & Organization Plan
*Last updated: March 2026*

---

## STATUS — What Just Got Done (This Session)
- [x] Fixed Addison district label: D1 → **D7** in STLCA_Council_Briefing_2026.html
- [x] Rewrote STLCA_brief.html as a **proper council memo** (white bg, serif, printable format)
- [x] Moved STLCA_CaseStudy_MissingReports.html to root (now live on GitHub Pages)
- [x] Updated all links from `ORD 12/STLCA_CaseStudy_MissingReports.html` → root path
- [x] Added clickable "Full case study" links to CS-001 (Ord 125054) across all pages
- [x] Added cs002 / cs003 anchor IDs to CASE_STUDY_INDEX.html sections
- [x] Added case study index links to Addison + Everspring cards on STLCA_Home.html
- [x] Created DEAR CITY COUNCIL/COUNCIL_EMAIL_DRAFT_MARCH2026.txt
- [x] Portal scraper launched (background) — output → SCRIPTS/portal_scrape_results.csv

---

## IMMEDIATE NEXT — Finish This Round

### Council Outreach Package
- [ ] **Finalize council email** — use draft in DEAR CITY COUNCIL/COUNCIL_EMAIL_DRAFT_MARCH2026.txt
  - Customize per district (numbers already in the draft)
  - Strip personal name, use STLCA org identity only
  - Send to all 9 council offices simultaneously
- [ ] **STLCA_brief.html** — review reformatted memo, confirm all numbers correct, print-test
- [ ] **STLCA_Home.html** — remove sticky nav (Hostinger double-navbar fix for embedded version)
  - Option A: Strip nav entirely, rely on Hostinger nav
  - Option B: Keep nav, add CSS class `.hostinger-embed { nav { display:none } }` and apply in Hostinger
- [ ] **Confirm Hostinger deployment** — test all links, check double-nav issue is gone

### Portal Scraper
- [ ] Check output: SCRIPTS/portal_scrape_results.csv — did it work?
- [ ] Review scraped data for Addison fire timeline evidence
- [ ] Review scraped data for Everspring same-day closure evidence

---

## CASE STUDIES — Build Queue

### CS-001: Ordinance 125054 — COMPLETE ✅
- HTML: STLCA_CaseStudy_MissingReports.html (root, live)
- Key: Tallent denial in writing; 9 years zero reports; signed ordinance is public record

### CS-002: The Addison on 4th (308 4th Ave S, D7) — DOCS BUILT, NO HTML YET
- Folder: Addison/
- Evidence: Fire Jan 7 2020, SFD alert Nov 6 2019, 29-day inspection delay, post-fire records disappear
- TODO: Build HTML case study (model after STLCA_CaseStudy_MissingReports.html)
- SDCI records CSV: Addison/ADDISON Code_Complaints_and_Violations_20250509.csv
- Scraper data: check portal_scrape_results.csv after scraper completes

### CS-003: Everspring Inn (8201 Aurora Ave N, D6) — DOCS BUILT, NO HTML YET
- Folder: Everspring/
- Evidence: 13 complaints one day, all closed same day, zero inspections, COVID moratorium
- Closer names in record: Stella Washington + James Hammon
- TODO: Build HTML case study

### CS-004: Gallery Belltown Unit 515 (2911 2nd Ave #515, D7)
- Folder: THE CASE CASE STUDYS/GALLERY-BELLTOWN D/
- Evidence: Unauthorized demolition; Superior Court contempt; SDCI closed "No Violation Observed"
- TODO: Review docs, build case study outline, then HTML

### CS-005: Hiawatha/ARTSPACE (843 Hiawatha Pl S, D2)
- Folder: THE CASE CASE STUDYS/NO INVESTIGATION-COMPLETEDHIWATHA/
- Evidence: 40+ complaints 2023-2025, mass admin closures, improper eviction notices
- TODO: Pull complaint records from primary CSV, write outline

### CS-006: The Olivian (809 Olive Way, D7)
- Folder: THE CASE CASE STUDYS/THE OLIVIAN 809 OLIVE WAY/
- Files: Appeal narrative (Olivian_Appeal_Narrative_With_Dismissal.markdown in THE CASE CASE STUDYS/)
- TODO: Build case study outline

### CS-007: Larkspur Cadence (1727 Summit Ave, D3)
- Folder: THE CASE CASE STUDYS/LARKSPUR/
- Files: Property records, deed, elevator records
- TODO: Pull SDCI complaint data, write outline

### CS-008: Lake Washington Apartments (9061 Seward Park Ave S, D2)
- Folder: LAKE WASHINGTON APTS/ — WARNING: 9+ versions of HTML, very messy
- Multiple HTML drafts: V2, V3, V4, GPT versions — CONSOLIDATE to single final
- TODO: Pick best version, clean up, finalize single HTML

### CS-009: Lowell Emerson (1110 8th Ave, D7) — PERSONAL CASE, USE LAST
- Files scattered: Gmail PDFs at root, Lowell Emerson docs in THE CASE CASE STUDYS/
- Founded Lowell Emerson Tenant Association 2023; 80+ violations; flooding; $30M+ fines
- This is where Ord 125054 question originated (Tallent denial)
- TODO: Build last, after all third-party cases are published

### CS-010: CONVEYANCE (unknown address)
- Folder: THE CASE CASE STUDYS/CONVEYANCE/
- Files: Historical docs going back to 1997 (corrections, letters)
- TODO: Identify address/property, determine connection to current case

---

## NEW ADDRESSES TO INVESTIGATE

| Address | Notes | Status | Priority |
|---------|-------|--------|----------|
| 11008 Dayton Ave N | HotPads screenshot in file — possible illegal STR/illegal rental | New lead | Medium |
| 1413 E Spruce St (Knox) | CSV file exists: 1413 e spruce st knoxCode_Complaints...csv | Has data | High |
| 938 N 86th St (Lunde Salvage) | Demolition permit analysis doc in LUNDE/ | Research phase | Medium |
| 1412 Summit (Manchester Arms) | MP4 screenshot in root: record 000747-25CP | Single record | Low |
| 1102 8th Ave | Illegal eviction screenshot at root: 001117-25CP | Single record | Low |
| 1020 University | Empty folder in THE CASE CASE STUDYS/ | No data yet | Low |

**For each new address: pull from primary CSV → SDCI records → build complaint timeline → cross-ref RRIO**

---

## FILE ORGANIZATION — What Needs to Move

The root directory is very messy. Here is the target structure:

### Create: CASE_STUDIES/ folder (organized by address)
Move these into consistent named subfolders:
```
CASE_STUDIES/
  308_4TH_AVE_S__ADDISON/         ← move from Addison/
  8201_AURORA_AVE_N__EVERSPRING/   ← move from Everspring/
  1110_8TH_AVE__LOWELL_EMERSON/   ← move from scattered locations
  9061_SEWARD_PARK__LAKE_WA/      ← move from LAKE WASHINGTON APTS/
  2911_2ND_AVE_515__GALLERY/      ← move from THE CASE CASE STUDYS/GALLERY-BELLTOWN D/
  843_HIAWATHA__ARTSPACE/         ← move from THE CASE CASE STUDYS/NO INVESTIGATION.../
  809_OLIVE_WAY__OLIVIAN/         ← move from THE CASE CASE STUDYS/THE OLIVIAN 809 OLIVE WAY/
  1727_SUMMIT__LARKSPUR/          ← move from THE CASE CASE STUDYS/LARKSPUR/
  1413_E_SPRUCE__KNOX/            ← new
  11008_DAYTON__NEW/              ← move from THE CASE CASE STUDYS/11008 Dayton/
  938_N_86TH__LUNDE/              ← move from LUNDE/
  CONVEYANCE/                     ← move from THE CASE CASE STUDYS/CONVEYANCE/
```

### Clean up root:
- Move all `Code_Complaints_and_Violations_20XX_*.csv` → DATA/ (25 files)
- Move all `EXTR_*.csv` (King County assessor extracts) → DATA/KING_COUNTY_ASSESSOR/
- Move loose `.py` scripts (build_*.py, fix_*.py) → SCRIPTS/
- Move loose screenshots/PNGs with long names → IMAGES/
- Move `.docx` files → DOCS/
- Move `GROK OUTPUTS/`, `GPT/`, `COLAB2/` → ARCHIVE/
- `CLAUDE ORGANIZE/` can be archived or deleted (duplicate of working files)

### Partially-done web pages (do NOT touch yet — in progress):
- STLCA_RRIO_Compliance_Gap.html (684 lines)
- STLCA_RRIO_False_Compliance.html (216 lines)
- PAGE_CARDS.html (208 lines)
- stlca_push.html (empty — placeholder)

---

## AFTER COUNCIL OUTREACH — Next Phase

### Press / Public Phase
- [ ] Journalist packet — same as council package but with press release header
- [ ] Identify specific reporters: PubliCola (already cited: audit article in THE CASE CASE STUDYS/),
      Seattle Times housing, KUOW, Crosscut
- [ ] Simultaneous with or 72 hours after council notification

### Build Remaining HTML Case Studies (in order)
1. Addison (CS-002) — fire + enforcement delay, most visceral
2. Everspring (CS-003) — COVID moratorium + mass closure
3. Gallery Belltown (CS-004) — court contempt vs SDCI "no violation"
4. Lake Washington Apts (CS-008) — consolidate existing HTML drafts
5. Larkspur, Hiawatha, Olivian (CS-005, 006, 007)
6. Lowell Emerson (CS-009) — personal case, always last

### Data / Analysis Phase
- [ ] Run new addresses through primary CSV (1413 E Spruce, 11008 Dayton)
- [ ] Build Lake Washington complaint timeline from LAKE WASHINGTON APTS CSVs
- [ ] Check scraper results for Addison/Everspring portal data
- [ ] RRIO cross-reference for new addresses

### Web / GitHub Pages
- [ ] Rebuild SITEMAP.html to include new pages (CaseStudy_MissingReports, brief memo)
- [ ] Add STLCA_CaseStudy_MissingReports.html to GitHub Pages (commit it)
- [ ] Verify all 7 district dossiers display correctly at GitHub Pages URL
- [ ] Fix STLCA_brief.html in SITEMAP
- [ ] Add per-district "closed/no result" stat to STLCA_Home.html stats section

---

## KEY NUMBERS (always verify from here, do not override)
- Total records: 233,543 | LLT total: 58,761 | LLT 2015-2025: 46,108
- Citywide 59.8% closed/no result | 62.3% no inspection date | 5,936 open cases
- D1=8,015 | D2=9,353 | D3=11,351 | D4=7,033 | D5=7,595 | D6=6,634 | D7=8,094
- 2,671 records have NO district (always mention this)
- Ordinance 125054: required reports 2017-2025 = 9 years, ZERO filed

---

## COUNCIL CONTACT NOTES
- Send from STLCA org, NOT personal name
- Redact personal email from any exhibits before sending
- 30-day response window before press
- Rob Saka (D1): West Seattle + SODO — Addison data NOT his district (D7 = Kettle)
- Ord 125054 was authored as amendment by CM Herbold (no longer in office — passed 8-0, binding on city)
- Housing committee chair: check current assignment (may be Hollingsworth or Rivera)
