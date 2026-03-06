import pandas as pd, warnings, json
warnings.filterwarnings('ignore')

CSV = r"C:/Users/stlca/stlca_web/DATA/CITYWIDE/CITYWIDE_ALL_20251231_ENRICHED_01272025.csv"
print("Loading...")
df = pd.read_csv(CSV, encoding='latin-1', on_bad_lines='warn', low_memory=False)
print(f"Loaded {len(df):,}")

df['RecordTypeDesc'] = df['RecordTypeDesc'].fillna('')
df['StatusCurrent']  = df['StatusCurrent'].fillna('')
df['District']       = pd.to_numeric(df['District'], errors='coerce')

def is_llt(r):
    rl = str(r).strip().lower()
    return rl == '' or 'emergency' in rl or 'landlord/tenant' in rl

df['LLT'] = df['RecordTypeDesc'].apply(is_llt)

# Open LLT cases = StatusCurrent not in Closed/Completed
open_statuses = ['Under Investigation','Initiated','NOV Issued','Warning',
                 'Citation Issued','Referred to Law','EO Vacate Close Issued',
                 'Hazard Correction Order Issued','Issued','Reviews Completed',
                 'Reviews In Process','Open Duplicate','EO Repair Restore Issued',
                 'Compliance Achieved','Open']

llt_open = df[df['LLT'] & df['StatusCurrent'].isin(open_statuses)].copy()
print(f"\nTotal open LLT cases: {len(llt_open):,}")

# Referred to Law - LLT only all years
rtl = df[df['LLT'] & (df['StatusCurrent'] == 'Referred to Law')]
print(f"LLT Referred to Law (all years): {len(rtl):,}")
rtl_all = df[df['StatusCurrent'] == 'Referred to Law']
print(f"ALL records Referred to Law: {len(rtl_all):,}")

# Per district - oldest 15 open LLT cases
for d in range(1,8):
    dist_open = llt_open[llt_open['District'] == d].copy()
    dist_open['OpenDate'] = pd.to_datetime(dist_open['OpenDate'], errors='coerce')
    dist_open = dist_open.dropna(subset=['OpenDate']).sort_values('OpenDate')
    top15 = dist_open.head(15)[['OpenDate','RecordNum','StatusCurrent','RecordTypeDesc','OriginalAddress1']]
    rows = []
    for _, r in top15.iterrows():
        rows.append({
            'date': r['OpenDate'].strftime('%Y-%m-%d') if pd.notna(r['OpenDate']) else '',
            'rec':  str(r['RecordNum']).strip(),
            'status': str(r['StatusCurrent']).strip(),
            'type': str(r['RecordTypeDesc']).strip() or 'Blank/LLT',
            'addr': str(r['OriginalAddress1']).strip()
        })
    print(f"\nD{d} open LLT top 15:")
    for row in rows:
        print(f"  {row['date']} | {row['rec']} | {row['status']} | {row['type']} | {row['addr']}")
    # save as json
    with open(f"C:/Users/stlca/stlca_web/SCRIPTS/D{d}_open_llt.json","w") as f:
        json.dump(rows, f)
