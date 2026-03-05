"""
build_top100_landlords.py
Top 100 landlord/management companies by complaints — Seattle SDCI data.
Sources:
  - STLCA_FULL_INTEL_WITH_OWNERS.csv (property-level aggregated data + current owner)
  - Code_Complaints_and_Violations_YYYY_*.csv (individual complaint records)
Outputs:
  - TOP100_LANDLORDS.csv  (one row per landlord, ranked)
  - TOP100_LANDLORD_PROPERTIES.csv (one row per property under each landlord)
  - TOP100_COMPLAINT_DETAIL.csv (individual complaint records for top 100 landlord properties)
"""
import csv, sys, os, glob
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\stlca\stlca_web'
OUT  = r'C:\Users\stlca\stlca_web\output'
os.makedirs(OUT, exist_ok=True)

def parse_date(d):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%Y/%m/%d'):
        try: return datetime.strptime(d.strip(), fmt)
        except: pass
    return datetime.min

def safe_int(v):
    try: return int(v or 0)
    except: return 0

# ── 1. Load property-level intel with owners ───────────────────────────────────
print("Step 1: Loading property intelligence report with owners...")
intel_path = os.path.join(OUT, 'STLCA_FULL_INTEL_WITH_OWNERS.csv')
if not os.path.exists(intel_path):
    print("ERROR: Run build_owner_report.py first to generate STLCA_FULL_INTEL_WITH_OWNERS.csv")
    sys.exit(1)

properties = []
with open(intel_path, encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        owner = row.get('CURRENT_OWNER','').strip()
        if not owner:
            owner = 'UNKNOWN / NOT IN SALE RECORDS'
        row['_OWNER_NORM'] = owner
        properties.append(row)
print(f"  {len(properties):,} properties loaded")

# ── 2. Group properties by owner ───────────────────────────────────────────────
print("Step 2: Grouping by owner...")
by_owner = defaultdict(list)
for p in properties:
    by_owner[p['_OWNER_NORM']].append(p)

# Build landlord summary rows
landlord_rows = []
for owner, props in by_owner.items():
    total_complaints   = sum(safe_int(p.get('TOTAL_COMPLAINTS')) for p in props)
    total_90d          = sum(safe_int(p.get('COMPLAINTS_IN_90_DAYS')) for p in props)
    total_open         = sum(safe_int(p.get('OPEN_UNRESOLVED')) for p in props)
    total_units        = sum(safe_int(p.get('APT_UNITS')) for p in props)
    total_val          = sum(safe_int(p.get('TOTAL_ASSESSED_VALUE')) for p in props)
    # addresses as semicolon list (top 5)
    addresses = '; '.join(p.get('ADDRESS','') for p in sorted(props, key=lambda x: -safe_int(x.get('TOTAL_COMPLAINTS')))[:5])
    # building names
    names = '; '.join(p.get('BUILDING_NAME','') for p in props if p.get('BUILDING_NAME','').strip())[:200]
    # date range of complaints across all properties
    first_dates = [p.get('FIRST_COMPLAINT','') for p in props if p.get('FIRST_COMPLAINT','')]
    last_dates  = [p.get('LAST_COMPLAINT','') for p in props if p.get('LAST_COMPLAINT','')]
    first_overall = min((parse_date(d) for d in first_dates), default=datetime.min)
    last_overall  = max((parse_date(d) for d in last_dates),  default=datetime.min)

    landlord_rows.append({
        'OWNER':                owner,
        'TOTAL_PROPERTIES':     len(props),
        'TOTAL_UNITS':          total_units,
        'TOTAL_COMPLAINTS':     total_complaints,
        'COMPLAINTS_90D':       total_90d,
        'TOTAL_OPEN_UNRESOLVED':total_open,
        'TOTAL_ASSESSED_VALUE': total_val,
        'FIRST_COMPLAINT':      first_overall.strftime('%m/%d/%Y') if first_overall != datetime.min else '',
        'LAST_COMPLAINT':       last_overall.strftime('%m/%d/%Y')  if last_overall  != datetime.min else '',
        'BUILDING_NAMES':       names,
        'TOP_ADDRESSES':        addresses,
    })

# Sort by total complaints descending
landlord_rows.sort(key=lambda x: (-x['TOTAL_COMPLAINTS'], -x['COMPLAINTS_90D']))

# Assign rank
for i, r in enumerate(landlord_rows, 1):
    r['RANK'] = i

# Take top 100 with complaints
top100 = [r for r in landlord_rows if r['TOTAL_COMPLAINTS'] > 0][:100]
top100_owners = {r['OWNER'] for r in top100}

print(f"  {len(landlord_rows):,} unique owners found")
print(f"  Top 100 with complaints:")
for r in top100[:20]:
    print(f"    #{r['RANK']:>3} {r['TOTAL_COMPLAINTS']:>5} complaints | {r['TOTAL_PROPERTIES']:>3} props | {r['TOTAL_UNITS']:>4} units | {r['OWNER'][:60]}")
print(f"  ...")

# ── 3. Build property detail for top 100 ──────────────────────────────────────
print("\nStep 3: Building property detail for top 100...")
property_detail_rows = []
for p in properties:
    if p['_OWNER_NORM'] not in top100_owners:
        continue
    # Find this owner's rank
    rank = next((r['RANK'] for r in top100 if r['OWNER'] == p['_OWNER_NORM']), 999)
    property_detail_rows.append({
        'LANDLORD_RANK':        rank,
        'OWNER':                p['_OWNER_NORM'],
        'ADDRESS':              p.get('ADDRESS',''),
        'BUILDING_NAME':        p.get('BUILDING_NAME',''),
        'ZIP':                  p.get('ZIP',''),
        'APT_UNITS':            p.get('APT_UNITS',''),
        'APT_YR_BUILT':         p.get('APT_YR_BUILT',''),
        'APT_STORIES':          p.get('APT_STORIES',''),
        'TOTAL_COMPLAINTS':     p.get('TOTAL_COMPLAINTS',''),
        'COMPLAINTS_90D':       p.get('COMPLAINTS_IN_90_DAYS',''),
        'OPEN_UNRESOLVED':      p.get('OPEN_UNRESOLVED',''),
        'FIRST_COMPLAINT':      p.get('FIRST_COMPLAINT',''),
        'LAST_COMPLAINT':       p.get('LAST_COMPLAINT',''),
        'WORST_90D_WINDOW':     p.get('WORST_WINDOW',''),
        'FLAGS':                p.get('FLAGS',''),
        'KNOWN_CASE':           p.get('KNOWN_CASE_LABEL',''),
        'LAND_VALUE':           p.get('LAND_VALUE',''),
        'IMPROVEMENT_VALUE':    p.get('IMPROVEMENT_VALUE',''),
        'TOTAL_ASSESSED_VALUE': p.get('TOTAL_ASSESSED_VALUE',''),
        'SALE_HISTORY':         p.get('SALE_HISTORY','')[:300],
        'PIN':                  p.get('PIN',''),
        'LAST_SALE_DATE':       p.get('LAST_SALE_DATE',''),
        'LAST_SALE_PRICE':      p.get('LAST_SALE_PRICE',''),
        'PREVIOUS_OWNER':       p.get('PREVIOUS_OWNER',''),
    })

property_detail_rows.sort(key=lambda x: (x['LANDLORD_RANK'], -safe_int(x.get('TOTAL_COMPLAINTS'))))
print(f"  {len(property_detail_rows):,} property rows for top 100 landlords")

# ── 4. Load raw complaint records for top 100 property addresses ───────────────
print("\nStep 4: Loading raw complaint records for top 100 properties...")
top100_addresses = {r['ADDRESS'].upper().strip() for r in property_detail_rows if r['ADDRESS']}

complaint_files = sorted(glob.glob(os.path.join(BASE, 'Code_Complaints_and_Violations_*.csv')))
print(f"  Found {len(complaint_files)} annual complaint files")

complaint_detail = []
for fpath in complaint_files:
    year = os.path.basename(fpath)[:36]
    try:
        with open(fpath, encoding='utf-8', errors='replace') as f:
            for row in csv.DictReader(f):
                addr = row.get('Address','').upper().strip()
                if addr in top100_addresses:
                    complaint_detail.append({
                        'ADDRESS':      row.get('Address','').strip(),
                        'DATE':         row.get('Date','').strip(),
                        'CASE_NUM':     row.get('CaseNum','').strip(),
                        'RECORD_TYPE':  row.get('RecordType1','').strip(),
                        'STATUS':       row.get('StatusCurrent1','').strip(),
                        'DESCRIPTION':  row.get('Description1','').strip()[:300],
                    })
    except Exception as e:
        print(f"  WARNING: {fpath}: {e}")

# Join owner info
addr_to_owner = {p.get('ADDRESS','').upper().strip(): p['_OWNER_NORM'] for p in properties}
addr_to_rank  = {}
for r in property_detail_rows:
    addr_to_rank[r['ADDRESS'].upper().strip()] = r['LANDLORD_RANK']

for c in complaint_detail:
    addr_key = c['ADDRESS'].upper().strip()
    c['OWNER'] = addr_to_owner.get(addr_key, '')
    c['LANDLORD_RANK'] = addr_to_rank.get(addr_key, 999)

# Sort by rank, then address, then date
complaint_detail.sort(key=lambda x: (x['LANDLORD_RANK'], x['ADDRESS'], parse_date(x['DATE'])))

print(f"  {len(complaint_detail):,} individual complaint records for top 100 landlord properties")

# NOV counts
nov_count = sum(1 for c in complaint_detail if 'NOV' in c.get('RECORD_TYPE','').upper() or 'VIOLATION' in c.get('RECORD_TYPE','').upper())
print(f"  Notices of Violation (NOV): {nov_count:,}")

# ── 5. Save outputs ────────────────────────────────────────────────────────────
print("\nStep 5: Saving outputs...")

# Top 100 landlords summary
out1 = os.path.join(OUT, 'TOP100_LANDLORDS.csv')
fields1 = ['RANK','OWNER','TOTAL_PROPERTIES','TOTAL_UNITS','TOTAL_COMPLAINTS',
           'COMPLAINTS_90D','TOTAL_OPEN_UNRESOLVED','TOTAL_ASSESSED_VALUE',
           'FIRST_COMPLAINT','LAST_COMPLAINT','BUILDING_NAMES','TOP_ADDRESSES']
with open(out1, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields1)
    w.writeheader()
    w.writerows(top100)
print(f"  Saved: {out1}")

# Property detail
out2 = os.path.join(OUT, 'TOP100_LANDLORD_PROPERTIES.csv')
fields2 = ['LANDLORD_RANK','OWNER','ADDRESS','BUILDING_NAME','ZIP','APT_UNITS',
           'APT_YR_BUILT','APT_STORIES','TOTAL_COMPLAINTS','COMPLAINTS_90D',
           'OPEN_UNRESOLVED','FIRST_COMPLAINT','LAST_COMPLAINT','WORST_90D_WINDOW',
           'FLAGS','KNOWN_CASE','LAND_VALUE','IMPROVEMENT_VALUE','TOTAL_ASSESSED_VALUE',
           'LAST_SALE_DATE','LAST_SALE_PRICE','PREVIOUS_OWNER','SALE_HISTORY','PIN']
with open(out2, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields2)
    w.writeheader()
    w.writerows(property_detail_rows)
print(f"  Saved: {out2}")

# Individual complaint records
out3 = os.path.join(OUT, 'TOP100_COMPLAINT_DETAIL.csv')
fields3 = ['LANDLORD_RANK','OWNER','ADDRESS','DATE','CASE_NUM','RECORD_TYPE','STATUS','DESCRIPTION']
with open(out3, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields3)
    w.writeheader()
    w.writerows(complaint_detail)
print(f"  Saved: {out3}")

# ── 6. Print summary ───────────────────────────────────────────────────────────
print(f"\n{'='*90}")
print(f"TOP 100 LANDLORD/MANAGEMENT COMPANIES — SDCI COMPLAINT REGISTER")
print(f"{'='*90}")
print(f"  {'RANK':<5} {'COMPLAINTS':>10} {'90D':>6} {'OPEN':>5} {'PROPS':>5} {'UNITS':>5}  OWNER")
print(f"  {'-'*90}")
for r in top100:
    print(f"  #{r['RANK']:<4} {r['TOTAL_COMPLAINTS']:>10,} {r['COMPLAINTS_90D']:>6} {r['TOTAL_OPEN_UNRESOLVED']:>5} "
          f"{r['TOTAL_PROPERTIES']:>5} {r['TOTAL_UNITS']:>5}  {r['OWNER'][:60]}")

print(f"\n  Total complaints across top 100: {sum(r['TOTAL_COMPLAINTS'] for r in top100):,}")
print(f"  Total units across top 100:      {sum(r['TOTAL_UNITS'] for r in top100):,}")
print(f"  Individual complaint records:    {len(complaint_detail):,}")
print(f"  NOVs in detail records:          {nov_count:,}")
print("\nDONE.")
