import csv, sys, os
from collections import defaultdict
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\stlca\stlca_web'
OUT  = r'C:\Users\stlca\stlca_web\output'
os.makedirs(OUT, exist_ok=True)

# ── 1. Build owner lookup: most recent BuyerName per Major+Minor ──────────────
print("Step 1: Building ownership index from EXTR_RPSale...")
sales = defaultdict(list)  # key: (major, minor) -> list of (date, buyer, seller, price)
with open(os.path.join(BASE, 'EXTR_RPSale.csv'), encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        major = row.get('Major','').strip().zfill(6)
        minor = row.get('Minor','').strip().zfill(4)
        date  = row.get('DocumentDate','').strip()
        buyer = row.get('BuyerName','').strip()
        seller= row.get('SellerName','').strip()
        price = row.get('SalePrice','').strip()
        if major and minor and buyer:
            sales[(major, minor)].append((date, buyer, seller, price))

def parse_date(d):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try: return datetime.strptime(d, fmt)
        except: pass
    return datetime.min

# Most recent sale per parcel
owners = {}
for (major, minor), txns in sales.items():
    txns_sorted = sorted(txns, key=lambda x: parse_date(x[0]), reverse=True)
    latest = txns_sorted[0]
    pin = major + minor
    owners[pin] = {
        'PIN': pin,
        'CURRENT_OWNER': latest[1],
        'PREVIOUS_OWNER': txns_sorted[1][1] if len(txns_sorted) > 1 else '',
        'LAST_SALE_DATE': latest[0],
        'LAST_SALE_PRICE': latest[3],
        'PRIOR_SALE_DATE': txns_sorted[1][0] if len(txns_sorted) > 1 else '',
        'TOTAL_SALES': len(txns_sorted),
        'SALE_HISTORY': ' | '.join(f"{t[0]}:{t[1]}(${t[3]})" for t in txns_sorted[:5]),
    }
print(f"  {len(owners):,} parcels with ownership data")

# ── 2. Apartment complex data ──────────────────────────────────────────────────
print("Step 2: Loading apartment complex data...")
apt_data = {}
with open(os.path.join(BASE, 'EXTR_AptComplex.csv'), encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        major = row.get('Major','').strip().zfill(6)
        minor = row.get('Minor','').strip().zfill(4)
        pin = major + minor
        apt_data[pin] = {
            'APT_UNITS': row.get('NbrUnits','').strip(),
            'APT_STORIES': row.get('NbrStories','').strip(),
            'APT_YR_BUILT': row.get('YrBuilt','').strip(),
            'APT_CONDITION': row.get('Condition','').strip(),
            'APT_ELEVATORS': row.get('Elevators','').strip(),
            'APT_BLDG_QUALITY': row.get('BldgQuality','').strip(),
            'APT_AVG_UNIT_SIZE': row.get('AvgUnitSize','').strip(),
            'APT_ADDRESS': row.get('Address','').strip(),
        }
print(f"  {len(apt_data):,} apartment complexes indexed")

# ── 3. Commercial building data ────────────────────────────────────────────────
print("Step 3: Loading commercial building data...")
comm_data = {}
with open(os.path.join(BASE, 'EXTR_CommBldg.csv'), encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        major = row.get('Major','').strip().zfill(6)
        minor = row.get('Minor','').strip().zfill(4)
        pin = major + minor
        if pin not in comm_data:
            comm_data[pin] = {
                'COMM_USE': row.get('PredominantUse','').strip(),
                'COMM_STORIES': row.get('NbrStories','').strip(),
                'COMM_YR_BUILT': row.get('YrBuilt','').strip(),
                'COMM_GROSS_SQFT': row.get('BldgGrossSqFt','').strip(),
                'COMM_ELEVATORS': row.get('Elevators','').strip(),
            }
print(f"  {len(comm_data):,} commercial buildings indexed")

# ── 4. Load our intelligence report and join ───────────────────────────────────
print("Step 4: Joining with intelligence report...")
intel_path_c = os.path.join(BASE, 'STLCA_PROPERTY_INTELLIGENCE_REPORT_FULL.csv')
intel_path_d = r'D:\CASE_STUDIES\MASTER_DATA\audit_outputs\STLCA_PROPERTY_INTELLIGENCE_REPORT_FULL.csv'
intel_path = intel_path_c if os.path.exists(intel_path_c) else intel_path_d
try:
    rows = list(csv.DictReader(open(intel_path, encoding='utf-8')))
    print(f"  Loaded {len(rows):,} rows from: {intel_path}")
except:
    print("  Intel report not found. Copy STLCA_PROPERTY_INTELLIGENCE_REPORT_FULL.csv into stlca_web folder.")
    sys.exit(1)

merged = []
matched_owner = 0
matched_apt = 0
matched_comm = 0

for row in rows:
    pin = row.get('PIN','').strip()
    o = owners.get(pin, {})
    a = apt_data.get(pin, {})
    c = comm_data.get(pin, {})

    new_row = dict(row)
    new_row['CURRENT_OWNER']   = o.get('CURRENT_OWNER','')
    new_row['PREVIOUS_OWNER']  = o.get('PREVIOUS_OWNER','')
    new_row['LAST_SALE_DATE']  = o.get('LAST_SALE_DATE','')
    new_row['LAST_SALE_PRICE'] = o.get('LAST_SALE_PRICE','')
    new_row['TOTAL_SALES']     = o.get('TOTAL_SALES','')
    new_row['SALE_HISTORY']    = o.get('SALE_HISTORY','')
    new_row['APT_UNITS']       = a.get('APT_UNITS', c.get('',''))
    new_row['APT_STORIES']     = a.get('APT_STORIES', c.get('COMM_STORIES',''))
    new_row['APT_YR_BUILT']    = a.get('APT_YR_BUILT', c.get('COMM_YR_BUILT',''))
    new_row['APT_CONDITION']   = a.get('APT_CONDITION','')
    new_row['HAS_ELEVATORS']   = a.get('APT_ELEVATORS', c.get('COMM_ELEVATORS',''))
    new_row['APT_AVG_UNIT_SIZE'] = a.get('APT_AVG_UNIT_SIZE','')
    new_row['COMM_GROSS_SQFT'] = c.get('COMM_GROSS_SQFT','')

    # Enhance flags
    flags = row.get('FLAGS','')
    if o.get('CURRENT_OWNER','') and not flags.split('|')[0].strip() == 'NO_PARCEL_RECORD':
        if 'LLC' in o.get('CURRENT_OWNER','').upper() or 'INC' in o.get('CURRENT_OWNER','').upper():
            if 'LLC_OWNED' not in flags:
                flags += ' | LLC_OWNED'
    new_row['FLAGS'] = flags.strip(' |')

    if o: matched_owner += 1
    if a: matched_apt += 1
    if c: matched_comm += 1
    merged.append(new_row)

print(f"  Matched owner:      {matched_owner:,} / {len(rows):,}")
print(f"  Matched apt data:   {matched_apt:,}")
print(f"  Matched comm data:  {matched_comm:,}")

# ── 5. Save outputs ────────────────────────────────────────────────────────────
fieldnames = list(merged[0].keys())

# Full report with owners
out_full = os.path.join(OUT, 'STLCA_FULL_INTEL_WITH_OWNERS.csv')
with open(out_full, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(merged)
print(f"\nSaved: {out_full}")

# Known cases only
out_known = os.path.join(OUT, 'KNOWN_CASES_WITH_OWNERS.csv')
known = [r for r in merged if r.get('KNOWN_CASE_LABEL','')]
with open(out_known, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(known)
print(f"Saved: {out_known}")

# ── 6. Print known case ownership ─────────────────────────────────────────────
print("\n" + "="*80)
print("OWNERSHIP — KNOWN CASE PROPERTIES")
print("="*80)
for r in known:
    print(f"\n  ADDRESS:        {r['ADDRESS']}")
    print(f"  BUILDING:       {r['BUILDING_NAME']} | {r['BUILDING_COMMENTS']}")
    print(f"  PIN:            {r['PIN']}")
    print(f"  CURRENT OWNER:  {r['CURRENT_OWNER'] or 'NOT IN SALE RECORDS'}")
    print(f"  PREV OWNER:     {r['PREVIOUS_OWNER']}")
    print(f"  LAST SALE:      {r['LAST_SALE_DATE']} | ${r['LAST_SALE_PRICE']}")
    print(f"  TOTAL SALES:    {r['TOTAL_SALES']}")
    print(f"  UNITS/STORIES:  {r['APT_UNITS']} units / {r['APT_STORIES']} stories")
    print(f"  ELEVATORS:      {r['HAS_ELEVATORS']}")
    print(f"  YR BUILT:       {r['APT_YR_BUILT']}")
    try:
        lv = int(r.get('LAND_VALUE') or 0)
        iv = int(r.get('IMPROVEMENT_VALUE') or 0)
        tv = int(r.get('TOTAL_ASSESSED_VALUE') or 0)
        print(f"  ASSESSED:       Land=${lv:,} | Impr=${iv:,} | Total=${tv:,}")
    except:
        print(f"  ASSESSED: N/A")
    print(f"  FLAGS:          {r['FLAGS']}")
    if r['SALE_HISTORY']:
        print(f"  SALE HISTORY:   {r['SALE_HISTORY'][:200]}")

# ── 7. Top 30 LLC-owned bad actors ────────────────────────────────────────────
print("\n" + "="*80)
print("TOP 30 LLC-OWNED BAD ACTOR PROPERTIES")
print("="*80)
llc_bad = [r for r in merged if 'LLC' in r.get('CURRENT_OWNER','').upper() and int(r.get('COMPLAINTS_IN_90_DAYS',0) or 0) >= 5]
llc_bad.sort(key=lambda x: (-int(x.get('COMPLAINTS_IN_90_DAYS',0) or 0), -int(x.get('TOTAL_COMPLAINTS',0) or 0)))
for r in llc_bad[:30]:
    print(f"  #{r['RANK']:>4} | {r['ADDRESS']:<38} | {r['COMPLAINTS_IN_90_DAYS']:>3}/90d | {r['TOTAL_COMPLAINTS']:>5} tot | {r['CURRENT_OWNER'][:40]:<40} | {r['BUILDING_NAME'][:25]}")

print("\nDONE.")
