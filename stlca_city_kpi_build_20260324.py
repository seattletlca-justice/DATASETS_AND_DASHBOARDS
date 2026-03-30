import pandas as pd
import numpy as np

SOURCE_CSV = r'/mnt/data/CITYWIDE_ALL_20251231_ENRICHED_01272025__PLUS_RECORDLIST_TEXT_XXTRA.csv'
DATE_FMT = '%Y %b %d %I:%M:%S %p'
SNAPSHOT_DATE = pd.Timestamp('2025-12-31')

df = pd.read_csv(SOURCE_CSV, low_memory=False)
df['OPENDATE_DT'] = pd.to_datetime(df['OPENDATE'], format=DATE_FMT, errors='coerce')
df['LASTINSPDATE_DT'] = pd.to_datetime(df['LASTINSPDATE'], format=DATE_FMT, errors='coerce')

df['IS_CP'] = df['RECORDNUM'].astype(str).str.endswith('CP')
df['IS_VI'] = df['RECORDNUM'].astype(str).str.endswith('VI')
df['IS_CT'] = df['RECORDNUM'].astype(str).str.endswith('CT')

df['CP_STATUS_CLOSED_OR_COMPLETED'] = df['IS_CP'] & df['STATUSCURRENT'].isin(['CLOSED', 'COMPLETED'])
df['NO_INSP_DATE'] = df['NOINSPDATE T/F'].fillna(True).astype(bool)
df['NO_INSP_RESULT'] = df['NOINSPRESULT T/F'].fillna(True).astype(bool)
df['INSP_BOTH_MISSING'] = df['NO_INSP_DATE'] & df['NO_INSP_RESULT']
df['INSP_BOTH_PRESENT'] = (~df['NO_INSP_DATE']) & (~df['NO_INSP_RESULT'])

VI_FINAL = ['COMPLETED', 'COMPLIANCE ACHIEVED', 'WITHDRAWN']
df['VI_STATUS_ACTIVE_NONFINAL'] = df['IS_VI'] & ~df['STATUSCURRENT'].isin(VI_FINAL)
df['VI_STATUS_INITIATED'] = df['IS_VI'] & df['STATUSCURRENT'].eq('INITIATED')
df['VI_STATUS_UNDER_INVESTIGATION'] = df['IS_VI'] & df['STATUSCURRENT'].eq('UNDER INVESTIGATION')
df['VI_STATUS_NOV_ISSUED'] = df['IS_VI'] & df['STATUSCURRENT'].eq('NOV ISSUED')

def summarize_year(year: int) -> dict:
    sub = df[df['OPENYEAR'].eq(year)]
    cp = int(sub['IS_CP'].sum())
    vi = int(sub['IS_VI'].sum())
    return {
        'OPENYEAR': year,
        'ALL_RECORDS': int(len(sub)),
        'CP_COUNT': cp,
        'VI_COUNT': vi,
        'VI_AS_PCT_OF_CP': (vi / cp) if cp else np.nan,
        'CP_CLOSED_OR_COMPLETED': int(sub['CP_STATUS_CLOSED_OR_COMPLETED'].sum()),
        'CP_CLOSED_OR_COMPLETED_NO_INSP_DATE': int((sub['CP_STATUS_CLOSED_OR_COMPLETED'] & sub['NO_INSP_DATE']).sum()),
        'CP_CLOSED_OR_COMPLETED_NO_INSP_RESULT': int((sub['CP_STATUS_CLOSED_OR_COMPLETED'] & sub['NO_INSP_RESULT']).sum()),
        'CP_CLOSED_OR_COMPLETED_BOTH_MISSING': int((sub['CP_STATUS_CLOSED_OR_COMPLETED'] & sub['INSP_BOTH_MISSING']).sum()),
        'CP_CLOSED_OR_COMPLETED_BOTH_PRESENT': int((sub['CP_STATUS_CLOSED_OR_COMPLETED'] & sub['INSP_BOTH_PRESENT']).sum()),
        'VI_ACTIVE_NONFINAL': int(sub['VI_STATUS_ACTIVE_NONFINAL'].sum()),
        'VI_INITIATED': int(sub['VI_STATUS_INITIATED'].sum()),
        'VI_UNDER_INVESTIGATION': int(sub['VI_STATUS_UNDER_INVESTIGATION'].sum()),
        'VI_NOV_ISSUED': int(sub['VI_STATUS_NOV_ISSUED'].sum()),
    }

yearly = pd.DataFrame([summarize_year(y) for y in range(2003, 2026)])
print(yearly.to_string(index=False))

# Important limitation:
# This source file does NOT contain a direct complaint-to-violation join key.
# Any matching between a complaint and a violation must be labeled heuristic unless a source key is found.
