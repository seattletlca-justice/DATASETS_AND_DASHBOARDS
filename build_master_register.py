"""
build_master_register.py
MASTER PROPERTY REGISTER — combines:
  1. SDCI complaint records (all years 2003-2025)
  2. RRIO registration data (owner/contact name, status, units)
  3. KC Assessor ownership (BuyerName from EXTR_RPSale)
  4. Property intelligence (complaint aggregates, flags)

Outputs:
  MASTER_PROPERTY_REGISTER.csv     — one row per unique property address
  MASTER_COMPLAINT_RECORDS.csv     — every individual complaint with owner info
"""
import csv, sys, os, glob, re
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE  = r'C:\Users\stlca\stlca_web'
OUT   = r'C:\Users\stlca\stlca_web\output'
RRIO_DIR = r'D:\stlca\rental_property_registration'
os.makedirs(OUT, exist_ok=True)

def parse_date(d):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%Y/%m/%d'):
        try: return datetime.strptime(d.strip(), fmt)
        except: pass
    return datetime.min

def safe_int(v):
    try: return int(v or 0)
    except: return 0

def norm_addr(a):
    """Normalize address for matching: uppercase, strip, collapse spaces."""
    a = re.sub(r'\s+', ' ', a.upper().strip())
    # Standardize common abbreviations
    a = re.sub(r'\bAVENUE\b', 'AVE', a)
    a = re.sub(r'\bSTREET\b', 'ST', a)
    a = re.sub(r'\bBOULEVARD\b', 'BLVD', a)
    a = re.sub(r'\bDRIVE\b', 'DR', a)
    a = re.sub(r'\bPLACE\b', 'PL', a)
    a = re.sub(r'\bNORTH\b', 'N', a)
    a = re.sub(r'\bSOUTH\b', 'S', a)
    a = re.sub(r'\bEAST\b', 'E', a)
    a = re.sub(r'\bWEST\b', 'W', a)
    a = re.sub(r'\bROAD\b', 'RD', a)
    a = re.sub(r'\bLANE\b', 'LN', a)
    a = re.sub(r'\bCOURT\b', 'CT', a)
    a = re.sub(r',\s*SEATTLE.*$', '', a)  # strip city/state
    a = re.sub(r'\s+WA\s+\d{5}.*$', '', a)
    a = re.sub(r'\s+SEATTLE\s*$', '', a)
    a = a.split('#')[0].strip()  # strip unit numbers
    return a.strip()

# ── 1. Load RRIO data ──────────────────────────────────────────────────────────
print("Step 1: Loading RRIO registration data...")
rrio = {}  # norm_addr -> dict (keep most recent registration)
rrio_files = sorted(glob.glob(os.path.join(RRIO_DIR, 'Rental_Property_Registration_*.csv')), reverse=True)
print(f"  Found {len(rrio_files)} RRIO files: {[os.path.basename(f) for f in rrio_files]}")

for fpath in rrio_files:
    with open(fpath, encoding='utf-8', errors='replace') as f:
        for row in csv.DictReader(f):
            addr_raw = row.get('OriginalAddress1','').strip().strip('"')
            if not addr_raw: continue
            key = norm_addr(addr_raw)
            if key not in rrio:  # first file is most recent
                rrio[key] = {
                    'RRIO_REG_NUM':     row.get('RegistrationNum','').strip().strip('"'),
                    'RRIO_CONTACT':     row.get('PropertyContactName','').strip().strip('"'),
                    'RRIO_PROP_NAME':   row.get('PropertyName','').strip().strip('"'),
                    'RRIO_UNITS':       row.get('RentalHousingUnits','').strip().strip('"'),
                    'RRIO_STATUS':      row.get('StatusCurrent','').strip().strip('"'),
                    'RRIO_REG_DATE':    row.get('RegisteredDate','').strip().strip('"'),
                    'RRIO_EXPIRES':     row.get('ExpiresDate','').strip().strip('"'),
                    'RRIO_TYPE':        row.get('RegisteredTypeMapped','').strip().strip('"'),
                    'RRIO_ADDRESS':     addr_raw,
                }
print(f"  {len(rrio):,} unique RRIO addresses loaded")

# ── 2. Load KC Assessor ownership ─────────────────────────────────────────────
print("Step 2: Loading KC Assessor ownership (EXTR_RPSale)...")
sale_path = os.path.join(BASE, 'EXTR_RPSale.csv')
sales_by_addr = defaultdict(list)  # norm_addr -> [(date, buyer, seller, price)]

if os.path.exists(sale_path):
    with open(sale_path, encoding='utf-8', errors='replace') as f:
        for row in csv.DictReader(f):
            # We don't have address in sale file — use PIN to join later
            pass
    print("  NOTE: EXTR_RPSale joins by PIN, not address — using intel report for ownership")
else:
    print("  EXTR_RPSale not found — skipping")

# Load intel report (has address + current owner + complaint aggregates)
print("Step 3: Loading intel report with ownership...")
intel = {}  # norm_addr -> row
intel_path = os.path.join(OUT, 'STLCA_FULL_INTEL_WITH_OWNERS.csv')
if not os.path.exists(intel_path):
    print("  CRITICAL: Run build_owner_report.py first!")
    sys.exit(1)
with open(intel_path, encoding='utf-8', errors='replace') as f:
    for row in csv.DictReader(f):
        addr = row.get('ADDRESS','').strip()
        if addr:
            intel[norm_addr(addr)] = row
print(f"  {len(intel):,} properties in intel report")

# ── 3. Load all complaint records ─────────────────────────────────────────────
print("Step 4: Loading all annual complaint records...")
complaint_files = sorted(glob.glob(os.path.join(BASE, 'Code_Complaints_and_Violations_*.csv')))
print(f"  Found {len(complaint_files)} files")

all_complaints = []  # list of dicts
addr_complaint_counts = defaultdict(int)
addr_nov_counts       = defaultdict(int)
addr_first_date       = {}
addr_last_date        = {}
addr_complaints_list  = defaultdict(list)  # norm_addr -> [complaint dicts]

for fpath in complaint_files:
    try:
        with open(fpath, encoding='utf-8', errors='replace') as f:
            for row in csv.DictReader(f):
                addr_raw = row.get('Address','').strip()
                if not addr_raw: continue
                key = norm_addr(addr_raw)
                date_str = row.get('Date','').strip()
                rec_type = row.get('RecordType1','').strip()
                status   = row.get('StatusCurrent1','').strip()
                desc     = row.get('Description1','').strip()
                case_num = row.get('CaseNum','').strip()

                d = parse_date(date_str)
                addr_complaint_counts[key] += 1
                if 'NOV' in rec_type.upper() or 'NOTICE OF VIOLATION' in rec_type.upper():
                    addr_nov_counts[key] += 1
                if key not in addr_first_date or (d != datetime.min and d < addr_first_date[key]):
                    addr_first_date[key] = d
                if key not in addr_last_date or d > addr_last_date[key]:
                    addr_last_date[key] = d

                complaint_rec = {
                    'ADDRESS_RAW': addr_raw,
                    'ADDRESS_NORM': key,
                    'DATE':        date_str,
                    'CASE_NUM':    case_num,
                    'RECORD_TYPE': rec_type,
                    'STATUS':      status,
                    'DESCRIPTION': desc[:300],
                }
                addr_complaints_list[key].append(complaint_rec)
                all_complaints.append(complaint_rec)
    except Exception as e:
        print(f"  WARNING {os.path.basename(fpath)}: {e}")

print(f"  {len(all_complaints):,} total complaint records across all years")
print(f"  {len(addr_complaint_counts):,} unique addresses with complaints")

# ── 4. Build master property register ────────────────────────────────────────
print("Step 5: Building master property register...")

# Union of all addresses: intel + RRIO + complaints
all_norm_addrs = set(intel.keys()) | set(rrio.keys()) | set(addr_complaint_counts.keys())
print(f"  {len(all_norm_addrs):,} unique addresses across all sources")

master_rows = []
for key in all_norm_addrs:
    ir   = intel.get(key, {})
    rr   = rrio.get(key, {})
    comp_count = addr_complaint_counts.get(key, 0)
    nov_count  = addr_nov_counts.get(key, 0)

    # Best address
    address = ir.get('ADDRESS','') or rr.get('RRIO_ADDRESS','') or key

    # Owner hierarchy: KC Assessor > RRIO contact
    kc_owner  = ir.get('CURRENT_OWNER','').strip()
    rrio_contact = rr.get('RRIO_CONTACT','').strip()
    owner = kc_owner or rrio_contact or 'UNKNOWN'

    first_d = addr_first_date.get(key, datetime.min)
    last_d  = addr_last_date.get(key,  datetime.min)

    master_rows.append({
        'ADDRESS':              address,
        'KC_OWNER':             kc_owner,
        'RRIO_CONTACT':         rrio_contact,
        'BEST_OWNER':           owner,
        'BUILDING_NAME':        ir.get('BUILDING_NAME','') or rr.get('RRIO_PROP_NAME',''),
        'ZIP':                  ir.get('ZIP',''),
        'DISTRICT':             '',  # filled below if available
        'APT_UNITS':            ir.get('APT_UNITS','') or rr.get('RRIO_UNITS',''),
        'APT_YR_BUILT':         ir.get('APT_YR_BUILT',''),
        'APT_STORIES':          ir.get('APT_STORIES',''),
        'TOTAL_COMPLAINTS':     comp_count,
        'SDCI_COMPLAINTS':      safe_int(ir.get('TOTAL_COMPLAINTS',0)),
        'COMPLAINTS_90D':       safe_int(ir.get('COMPLAINTS_IN_90_DAYS',0)),
        'OPEN_UNRESOLVED':      safe_int(ir.get('OPEN_UNRESOLVED',0)),
        'NOV_COUNT':            nov_count,
        'FIRST_COMPLAINT':      first_d.strftime('%m/%d/%Y') if first_d != datetime.min else '',
        'LAST_COMPLAINT':       last_d.strftime('%m/%d/%Y')  if last_d  != datetime.min else '',
        'RRIO_STATUS':          rr.get('RRIO_STATUS',''),
        'RRIO_TYPE':            rr.get('RRIO_TYPE',''),
        'RRIO_REG_DATE':        rr.get('RRIO_REG_DATE',''),
        'RRIO_EXPIRES':         rr.get('RRIO_EXPIRES',''),
        'RRIO_REG_NUM':         rr.get('RRIO_REG_NUM',''),
        'LAND_VALUE':           ir.get('LAND_VALUE',''),
        'IMPROVEMENT_VALUE':    ir.get('IMPROVEMENT_VALUE',''),
        'TOTAL_ASSESSED_VALUE': ir.get('TOTAL_ASSESSED_VALUE',''),
        'PREVIOUS_OWNER':       ir.get('PREVIOUS_OWNER',''),
        'LAST_SALE_DATE':       ir.get('LAST_SALE_DATE',''),
        'LAST_SALE_PRICE':      ir.get('LAST_SALE_PRICE',''),
        'FLAGS':                ir.get('FLAGS',''),
        'KNOWN_CASE':           ir.get('KNOWN_CASE_LABEL',''),
        'RANK':                 ir.get('RANK',''),
        'PIN':                  ir.get('PIN',''),
        'LAT':                  ir.get('LAT',''),
        'LON':                  ir.get('LON',''),
    })

# Sort by total complaints desc
master_rows.sort(key=lambda x: -x['TOTAL_COMPLAINTS'])

# Re-rank
for i, r in enumerate(master_rows, 1):
    r['MASTER_RANK'] = i

print(f"  {len(master_rows):,} properties in master register")

# ── 5. Add owner info to complaint records ────────────────────────────────────
print("Step 6: Enriching complaint records with owner/RRIO data...")
addr_to_owner = {}
addr_to_rrio  = {}
for r in master_rows:
    key = norm_addr(r['ADDRESS'])
    addr_to_owner[key] = r['BEST_OWNER']
    addr_to_rrio[key]  = r.get('RRIO_CONTACT','')

enriched_complaints = []
for c in all_complaints:
    key = c['ADDRESS_NORM']
    c['OWNER'] = addr_to_owner.get(key, 'UNKNOWN')
    c['RRIO_CONTACT'] = addr_to_rrio.get(key,'')
    enriched_complaints.append(c)

print(f"  {len(enriched_complaints):,} enriched complaint records")

# ── 6. Save outputs ────────────────────────────────────────────────────────────
print("Step 7: Saving outputs...")

out1 = os.path.join(OUT, 'MASTER_PROPERTY_REGISTER.csv')
fields1 = ['MASTER_RANK','ADDRESS','BEST_OWNER','KC_OWNER','RRIO_CONTACT','BUILDING_NAME',
           'ZIP','APT_UNITS','APT_YR_BUILT','APT_STORIES','TOTAL_COMPLAINTS','SDCI_COMPLAINTS',
           'COMPLAINTS_90D','OPEN_UNRESOLVED','NOV_COUNT','FIRST_COMPLAINT','LAST_COMPLAINT',
           'RRIO_STATUS','RRIO_TYPE','RRIO_REG_DATE','RRIO_EXPIRES','RRIO_REG_NUM',
           'LAND_VALUE','IMPROVEMENT_VALUE','TOTAL_ASSESSED_VALUE',
           'PREVIOUS_OWNER','LAST_SALE_DATE','LAST_SALE_PRICE',
           'FLAGS','KNOWN_CASE','RANK','PIN','LAT','LON']
with open(out1, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields1, extrasaction='ignore')
    w.writeheader()
    w.writerows(master_rows)
print(f"  Saved: {out1}  ({len(master_rows):,} rows)")

out2 = os.path.join(OUT, 'MASTER_COMPLAINT_RECORDS.csv')
fields2 = ['ADDRESS_RAW','OWNER','RRIO_CONTACT','DATE','CASE_NUM','RECORD_TYPE','STATUS','DESCRIPTION']
with open(out2, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields2, extrasaction='ignore')
    w.writeheader()
    w.writerows(enriched_complaints)
print(f"  Saved: {out2}  ({len(enriched_complaints):,} rows)")

# ── 7. Print summary ───────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"MASTER PROPERTY REGISTER — SUMMARY")
print(f"{'='*80}")
print(f"  Total unique property addresses: {len(master_rows):,}")
print(f"  Total complaint records:         {len(all_complaints):,}")
total_in_rrio = sum(1 for r in master_rows if r['RRIO_STATUS'])
total_w_owner = sum(1 for r in master_rows if r['KC_OWNER'])
total_nov      = sum(r['NOV_COUNT'] for r in master_rows)
print(f"  Properties with RRIO data:       {total_in_rrio:,}")
print(f"  Properties with KC owner data:   {total_w_owner:,}")
print(f"  Total NOVs across all years:     {total_nov:,}")
print(f"\n  TOP 30 BY TOTAL COMPLAINTS:")
print(f"  {'RANK':<5} {'COMPLAINTS':>10} {'NOV':>5} {'UNITS':>5}  {'OWNER':<40}  ADDRESS")
print(f"  {'-'*100}")
for r in master_rows[:30]:
    print(f"  #{r['MASTER_RANK']:<4} {r['TOTAL_COMPLAINTS']:>10,} {r['NOV_COUNT']:>5} {str(r['APT_UNITS']):>5}  "
          f"{r['BEST_OWNER'][:40]:<40}  {r['ADDRESS'][:45]}")

print("\nDONE.")
