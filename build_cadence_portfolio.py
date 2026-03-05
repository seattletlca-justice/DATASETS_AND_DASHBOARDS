"""
build_cadence_portfolio.py  v2
Map the full Cadence Real Estate / CRE / Peak Living Seattle portfolio
using King County Assessor EXTR_RPSale + EXTR_RPAcct_NoName + EXTR_AptComplex.
"""
import csv, sys, os
from collections import defaultdict
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\stlca\stlca_web'
OUT  = r'C:\Users\stlca\stlca_web\output'
os.makedirs(OUT, exist_ok=True)

# ── Tight match: only real Cadence/CRE/Peak Living entities ─────────────────
def is_cadence(name):
    n = name.upper().strip()
    if n.startswith('CRE '):          return True   # CRE SUMMIT, CRE 701, etc.
    if n.startswith('CADENCE '):      return True   # CADENCE CHATEAU, CADENCE REAL ESTATE, etc.
    if n == 'CADENCE':                return True
    if n.startswith('PEAK LIVING'):   return True   # PEAK LIVING PROPERTY SERVICES, etc.
    if n.startswith('SPV CADENCE'):   return True   # SPV CADENCE 39TH STREET, etc.
    if n.startswith('SPE CADENCE'):   return True   # SPE CADENCE 1631
    if 'GARVIN CHRIS' in n:          return True   # GARVIN CHRIS M / GARVIN CHRIS+KALLIE
    return False

def parse_date(d):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try: return datetime.strptime(d.strip(), fmt)
        except: pass
    return datetime.min

# ── 1. Load ALL sales per parcel, find current owner ────────────────────────
print("Step 1: Scanning EXTR_RPSale — building full ownership history...")
all_sales = defaultdict(list)   # pin -> [(date, buyer, seller, price)]

with open(os.path.join(BASE, 'EXTR_RPSale.csv'), encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        major = row.get('Major','').strip().zfill(6)
        minor = row.get('Minor','').strip().zfill(4)
        if not major or not minor: continue
        all_sales[major+minor].append((
            row.get('DocumentDate','').strip(),
            row.get('BuyerName','').strip(),
            row.get('SellerName','').strip(),
            row.get('SalePrice','').strip(),
        ))

# For each parcel: sort sales by date, find most recent + any cadence involvement
current_owner   = {}   # pin -> most recent buyer
cadence_current = {}   # pin -> sale info where cadence is current owner
cadence_past    = {}   # pin -> sale info where cadence was a past owner (already sold)

for pin, sales in all_sales.items():
    sorted_s = sorted(sales, key=lambda x: parse_date(x[0]), reverse=True)
    most_recent_buyer = sorted_s[0][1] if sorted_s else ''

    # Check if current owner is Cadence
    if is_cadence(most_recent_buyer):
        cadence_current[pin] = {
            'PIN': pin,
            'CADENCE_LLC': most_recent_buyer,
            'PURCHASE_DATE': sorted_s[0][0],
            'PURCHASE_PRICE': sorted_s[0][3],
            'SELLER_AT_PURCHASE': sorted_s[0][2],
        }
        current_owner[pin] = most_recent_buyer
    else:
        # Check if Cadence was a previous buyer
        for date, buyer, seller, price in sorted_s[1:]:
            if is_cadence(buyer):
                cadence_past[pin] = {
                    'PIN': pin,
                    'CADENCE_LLC': buyer,
                    'PURCHASE_DATE': date,
                    'PURCHASE_PRICE': price,
                    'SELLER_AT_PURCHASE': seller,
                    'CURRENT_BUYER': most_recent_buyer,
                }
                break

print(f"  Currently owned by Cadence: {len(cadence_current):,} parcels")
print(f"  Previously owned (sold):    {len(cadence_past):,} parcels")

# Show LLC names found as current owners
llc_counts = defaultdict(int)
for pin, d in cadence_current.items():
    llc_counts[d['CADENCE_LLC']] += 1
print(f"\n  Current owner LLC names found:")
for llc, cnt in sorted(llc_counts.items(), key=lambda x: -x[1]):
    print(f"    {cnt:>3}x  {llc}")

# ── 2. Load EXTR_RPAcct_NoName for assessed values ───────────────────────────
print("\nStep 2: Loading EXTR_RPAcct_NoName for assessed values...")
acct_data = {}   # pin -> {ApprLandVal, ApprImpsVal, AddrLine, CityState, ZipCode}
with open(os.path.join(BASE, 'EXTR_RPAcct_NoName.csv'), encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        major = row.get('Major','').strip().zfill(6)
        minor = row.get('Minor','').strip().zfill(4)
        if not major or not minor: continue
        pin = major + minor
        acct_data[pin] = {
            'LAND_VAL':  row.get('ApprLandVal','').strip(),
            'IMPR_VAL':  row.get('ApprImpsVal','').strip(),
            'ADDR_LINE': row.get('AddrLine','').strip(),
            'CITY_STATE':row.get('CityState','').strip(),
            'ZIP':       row.get('ZipCode','').strip(),
            'ACCT_NBR':  row.get('AcctNbr','').strip(),
        }
print(f"  Loaded {len(acct_data):,} account records")

# ── 3. Load AptComplex for unit/building data + property addresses ───────────
print("Step 3: Loading apartment complex data...")
apt_data = {}
with open(os.path.join(BASE, 'EXTR_AptComplex.csv'), encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        major = row.get('Major','').strip().zfill(6)
        minor = row.get('Minor','').strip().zfill(4)
        apt_data[major+minor] = {
            'APT_UNITS':        row.get('NbrUnits','').strip(),
            'APT_STORIES':      row.get('NbrStories','').strip(),
            'APT_YR_BUILT':     row.get('YrBuilt','').strip(),
            'APT_CONDITION':    row.get('Condition','').strip(),
            'HAS_ELEVATORS':    row.get('Elevators','').strip(),
            'APT_AVG_UNIT_SIZE':row.get('AvgUnitSize','').strip(),
            'APT_ADDRESS':      row.get('Address','').strip(),
        }

# ── 4. Load intel report for complaint data ───────────────────────────────────
print("Step 4: Loading STLCA intelligence report...")
intel = {}
intel_path = (os.path.join(BASE, 'STLCA_PROPERTY_INTELLIGENCE_REPORT_FULL.csv')
              if os.path.exists(os.path.join(BASE, 'STLCA_PROPERTY_INTELLIGENCE_REPORT_FULL.csv'))
              else r'D:\CASE_STUDIES\MASTER_DATA\audit_outputs\STLCA_PROPERTY_INTELLIGENCE_REPORT_FULL.csv')
try:
    with open(intel_path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            pin = row.get('PIN','').strip()
            if pin: intel[pin] = row
    print(f"  Loaded {len(intel):,} intelligence records from {intel_path}")
except Exception as e:
    print(f"  WARNING: {e}")

# ── 5. Build output rows ──────────────────────────────────────────────────────
print("Step 5: Building portfolio...")

def build_row(pin, sale_info, status):
    acct   = acct_data.get(pin, {})
    apt    = apt_data.get(pin, {})
    ir     = intel.get(pin, {})

    # Best address: apt complex address, then intel address, then mailing address
    address = apt.get('APT_ADDRESS','') or ir.get('ADDRESS','') or acct.get('ADDR_LINE','')
    city_state = acct.get('CITY_STATE','')
    city = city_state.split('  ')[0].strip() if '  ' in city_state else city_state.strip()

    # Assessed values
    try: land_v = int(acct.get('LAND_VAL','0') or 0)
    except: land_v = 0
    try: impr_v = int(acct.get('IMPR_VAL','0') or 0)
    except: impr_v = 0

    return {
        'STATUS':          status,
        'PIN':             pin,
        'ADDRESS':         address,
        'CITY':            city,
        'ZIP':             acct.get('ZIP','').strip(),
        'CADENCE_LLC':     sale_info.get('CADENCE_LLC',''),
        'CURRENT_BUYER':   sale_info.get('CURRENT_BUYER','') if status=='SOLD' else sale_info.get('CADENCE_LLC',''),
        'PURCHASE_DATE':   sale_info.get('PURCHASE_DATE',''),
        'PURCHASE_PRICE':  sale_info.get('PURCHASE_PRICE',''),
        'SELLER':          sale_info.get('SELLER_AT_PURCHASE',''),
        'LAND_VAL':        land_v,
        'IMPR_VAL':        impr_v,
        'TOTAL_VAL':       land_v + impr_v,
        'IMPR_FLAG':       'SUSPICIOUS_$1000' if impr_v == 1000 else '',
        'APT_UNITS':       apt.get('APT_UNITS',''),
        'APT_STORIES':     apt.get('APT_STORIES',''),
        'APT_YR_BUILT':    apt.get('APT_YR_BUILT',''),
        'HAS_ELEVATORS':   apt.get('HAS_ELEVATORS',''),
        'COMPLAINTS_90D':  ir.get('COMPLAINTS_IN_90_DAYS',''),
        'TOTAL_COMPLAINTS':ir.get('TOTAL_COMPLAINTS',''),
        'OPEN_UNRESOLVED': ir.get('OPEN_UNRESOLVED',''),
        'FLAGS':           ir.get('FLAGS',''),
        'KNOWN_CASE':      ir.get('KNOWN_CASE_LABEL',''),
        'BUILDING_NAME':   ir.get('BUILDING_NAME',''),
        'RANK':            ir.get('RANK',''),
        'ACCT_NBR':        acct.get('ACCT_NBR',''),
    }

rows = []
for pin, s in cadence_current.items():
    rows.append(build_row(pin, s, 'CURRENT'))
for pin, s in cadence_past.items():
    rows.append(build_row(pin, s, 'SOLD'))

# Sort: current first, then by total complaints desc
rows.sort(key=lambda r: (
    0 if r['STATUS']=='CURRENT' else 1,
    -int(r['TOTAL_COMPLAINTS'] or 0),
    -int(r['COMPLAINTS_90D'] or 0)
))

# ── 6. Save CSV ───────────────────────────────────────────────────────────────
out_path = os.path.join(OUT, 'CADENCE_FULL_PORTFOLIO.csv')
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nSaved: {out_path}")
print(f"Total rows: {len(rows):,}")

# ── 7. Summary print ──────────────────────────────────────────────────────────
current = [r for r in rows if r['STATUS']=='CURRENT']
sold    = [r for r in rows if r['STATUS']=='SOLD']
seattle_current = [r for r in current if 'SEATTLE' in r['CITY'].upper() or r['CITY'].strip()=='' ]

total_units = sum(int(r['APT_UNITS'] or 0) for r in current)
total_val   = sum(r['TOTAL_VAL'] for r in current)
total_cmplt = sum(int(r['TOTAL_COMPLAINTS'] or 0) for r in rows)
suspicious  = [r for r in current if r['IMPR_FLAG']]

print(f"\n{'='*80}")
print(f"CADENCE REAL ESTATE / CRE / PEAK LIVING — PORTFOLIO SUMMARY")
print(f"{'='*80}")
print(f"  Currently owned (King County): {len(current):>4}")
print(f"  Previously sold/transferred:   {len(sold):>4}")
print(f"  Total apt units (current):     {total_units:>4,}")
print(f"  Total assessed value:          ${total_val:>14,.0f}")
print(f"  SUSPICIOUS $1K improvement:    {len(suspicious):>4}")
print(f"  Total SDCI complaints (all):   {total_cmplt:>4,}")

print(f"\n{'='*80}")
print(f"CURRENTLY OWNED — Full List")
print(f"{'='*80}")
print(f"  {'ADDRESS':<38} {'LLC':<35} {'UNITS':>5} {'YR':>5} {'TOT_VAL':>12} {'90D':>4} {'TOT':>5}  FLAGS")
for r in current:
    addr = (r['ADDRESS'] or r['PIN'])[:38]
    llc  = r['CADENCE_LLC'][:35]
    tv   = f"${r['TOTAL_VAL']:,.0f}" if r['TOTAL_VAL'] else ''
    flag = ('⚠ $1K IMPR ' if r['IMPR_FLAG'] else '') + (r['KNOWN_CASE'] or '')
    print(f"  {addr:<38} {llc:<35} {r['APT_UNITS']:>5} {r['APT_YR_BUILT']:>5} "
          f"{tv:>12} {r['COMPLAINTS_90D'] or '':>4} {r['TOTAL_COMPLAINTS'] or '':>5}  {flag}")

print(f"\n{'='*80}")
print(f"PREVIOUSLY SOLD — Top 20 by Complaints")
print(f"{'='*80}")
for r in sold[:20]:
    addr = (r['ADDRESS'] or r['PIN'])[:38]
    print(f"  {addr:<38} sold {r['PURCHASE_DATE']:<12} {r['CADENCE_LLC'][:35]}")

print(f"\n{'='*80}")
print(f"SUSPICIOUS $1,000 IMPROVEMENT VALUE — CURRENTLY OWNED")
print(f"{'='*80}")
for r in suspicious:
    addr = (r['ADDRESS'] or r['PIN'])[:38]
    print(f"  {addr:<38} Land=${r['LAND_VAL']:>12,.0f}  Impr=$1,000  {r['CADENCE_LLC']}")

print("\nDONE.")
