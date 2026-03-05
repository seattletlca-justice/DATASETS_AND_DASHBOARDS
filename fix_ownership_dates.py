"""Fix ownership date sorting in existing output CSV.
The first run sorted MM/DD/YYYY dates as strings (wrong).
This reads the SALE_HISTORY column, re-sorts by parsed date,
and writes corrected CURRENT_OWNER / PREVIOUS_OWNER / LAST_SALE_DATE / LAST_SALE_PRICE.
"""
import csv, sys, re
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

BASE_OUT = r'C:\Users\stlca\stlca_web\output'

def parse_date(d):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try: return datetime.strptime(d, fmt)
        except: pass
    return datetime.min

def parse_history(history_str):
    """Parse 'MM/DD/YYYY:BUYER($PRICE) | ...' into list of (date, buyer, price)."""
    if not history_str:
        return []
    entries = []
    for part in history_str.split(' | '):
        part = part.strip()
        if not part:
            continue
        # format: DATE:NAME($PRICE)
        m = re.match(r'^([^:]+):(.+)\(\$([^)]*)\)$', part)
        if m:
            entries.append((m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
    return entries

in_path  = rf'{BASE_OUT}\STLCA_FULL_INTEL_WITH_OWNERS.csv'
out_path = rf'{BASE_OUT}\STLCA_FULL_INTEL_WITH_OWNERS_FIXED.csv'
known_in  = rf'{BASE_OUT}\KNOWN_CASES_WITH_OWNERS.csv'
known_out = rf'{BASE_OUT}\KNOWN_CASES_WITH_OWNERS_FIXED.csv'

fixes = 0

def fix_rows(rows):
    global fixes
    out = []
    for row in rows:
        history = parse_history(row.get('SALE_HISTORY', ''))
        if len(history) >= 2:
            sorted_h = sorted(history, key=lambda x: parse_date(x[0]), reverse=True)
            # Check if current owner would change
            new_owner = sorted_h[0][1]
            old_owner = row.get('CURRENT_OWNER', '')
            if new_owner != old_owner:
                fixes += 1
                print(f"  FIX: {row['ADDRESS']}")
                print(f"       WAS:  {old_owner}")
                print(f"       NOW:  {new_owner}")
                print(f"       DATE: {sorted_h[0][0]} | ${sorted_h[0][2]}")
                row['CURRENT_OWNER']   = sorted_h[0][1]
                row['PREVIOUS_OWNER']  = sorted_h[1][1] if len(sorted_h) > 1 else ''
                row['LAST_SALE_DATE']  = sorted_h[0][0]
                row['LAST_SALE_PRICE'] = sorted_h[0][2]
        out.append(row)
    return out

# Fix full report
with open(in_path, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
fieldnames = list(rows[0].keys())
fixed = fix_rows(rows)
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(fixed)

# Fix known cases
with open(known_in, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
fixed_k = fix_rows(rows)
with open(known_out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(fixed_k)

print(f"\nTotal fixes: {fixes}")
print(f"Saved: {out_path}")
print(f"Saved: {known_out}")

# Print known cases ownership summary
print("\n" + "="*80)
print("CORRECTED OWNERSHIP — KNOWN CASE PROPERTIES")
print("="*80)
with open(known_out, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        print(f"\n  ADDRESS:        {r['ADDRESS']}")
        print(f"  BUILDING:       {r['BUILDING_NAME']} | {r['BUILDING_COMMENTS']}")
        print(f"  PIN:            {r['PIN']}")
        print(f"  CURRENT OWNER:  {r['CURRENT_OWNER'] or 'NOT IN SALE RECORDS'}")
        print(f"  PREV OWNER:     {r['PREVIOUS_OWNER']}")
        print(f"  LAST SALE:      {r['LAST_SALE_DATE']} | ${r['LAST_SALE_PRICE']}")
        print(f"  UNITS/STORIES:  {r['APT_UNITS']} units / {r['APT_STORIES']} stories")
        print(f"  YR BUILT:       {r['APT_YR_BUILT']} | ELEVATORS: {r['HAS_ELEVATORS']}")
        try:
            tv = int(r.get('TOTAL_ASSESSED_VALUE') or 0)
            lv = int(r.get('LAND_VALUE') or 0)
            iv = int(r.get('IMPROVEMENT_VALUE') or 0)
            print(f"  ASSESSED:       Land=${lv:,} | Impr=${iv:,} | Total=${tv:,}")
        except:
            print(f"  ASSESSED:       N/A")
        print(f"  FLAGS:          {r['FLAGS']}")
        if r['SALE_HISTORY']:
            print(f"  SALE HISTORY:   {r['SALE_HISTORY'][:250]}")
