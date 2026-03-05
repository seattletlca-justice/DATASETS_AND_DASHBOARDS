"""
build_dashboard_html.py
Generate interactive LANDLORD_ACCOUNTABILITY_REGISTER.html
"""
import csv, json, os

OUT = r'C:\Users\stlca\stlca_web\output'
WEB = r'C:\Users\stlca\stlca_web'

# Load top 1500 properties from master register
rows = []
with open(os.path.join(OUT, 'MASTER_PROPERTY_REGISTER.csv'), encoding='utf-8', errors='replace') as f:
    for i, row in enumerate(csv.DictReader(f)):
        if i >= 1500: break
        addr = row.get('ADDRESS','').strip()
        if not addr or addr in ('SEATTLE', 'UNADDRESSABLE', ''): continue
        rows.append({
            'rank':        int(row.get('MASTER_RANK') or 0),
            'address':     addr,
            'owner':       (row.get('BEST_OWNER','') or 'UNKNOWN').strip(),
            'kc_owner':    row.get('KC_OWNER','').strip(),
            'rrio_contact':row.get('RRIO_CONTACT','').strip(),
            'building':    row.get('BUILDING_NAME','').strip(),
            'zip':         row.get('ZIP','').strip(),
            'units':       row.get('APT_UNITS','').strip(),
            'yr_built':    row.get('APT_YR_BUILT','').strip(),
            'stories':     row.get('APT_STORIES','').strip(),
            'complaints':  int(row.get('TOTAL_COMPLAINTS') or 0),
            'comp_90d':    int(row.get('COMPLAINTS_90D') or 0),
            'open':        int(row.get('OPEN_UNRESOLVED') or 0),
            'nov':         int(row.get('NOV_COUNT') or 0),
            'first_c':     row.get('FIRST_COMPLAINT','').strip(),
            'last_c':      row.get('LAST_COMPLAINT','').strip(),
            'rrio_status': row.get('RRIO_STATUS','').strip(),
            'rrio_type':   row.get('RRIO_TYPE','').strip(),
            'rrio_reg':    row.get('RRIO_REG_DATE','').strip(),
            'rrio_exp':    row.get('RRIO_EXPIRES','').strip(),
            'rrio_num':    row.get('RRIO_REG_NUM','').strip(),
            'land_val':    row.get('LAND_VALUE','').strip(),
            'impr_val':    row.get('IMPROVEMENT_VALUE','').strip(),
            'total_val':   row.get('TOTAL_ASSESSED_VALUE','').strip(),
            'flags':       row.get('FLAGS','').strip(),
            'known_case':  row.get('KNOWN_CASE','').strip(),
            'pin':         row.get('PIN','').strip(),
            'lat':         row.get('LAT','').strip(),
            'lon':         row.get('LON','').strip(),
            'prev_owner':  row.get('PREVIOUS_OWNER','').strip(),
            'last_sale_d': row.get('LAST_SALE_DATE','').strip(),
            'last_sale_p': row.get('LAST_SALE_PRICE','').strip(),
        })

print(f"Loaded {len(rows)} rows for dashboard")
data_json = json.dumps(rows, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>STLCA — Seattle Landlord Accountability Register</title>
<style>
:root{--red:#c0392b;--orange:#e67e22;--yellow:#f1c40f;--green:#27ae60;--blue:#2980b9;--dark:#1a1a2e;--mid:#16213e;--light:#e8e8e8;--white:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:var(--dark);color:var(--light);font-size:13px}
header{background:var(--mid);padding:16px 20px;border-bottom:2px solid var(--red)}
header h1{color:var(--red);font-size:1.35rem;letter-spacing:1px}
header p{color:#aaa;font-size:.82rem;margin-top:4px}
.stats-bar{display:flex;gap:10px;flex-wrap:wrap;padding:10px 20px;background:#0d0d1a;border-bottom:1px solid #333}
.stat-box{background:#1a1a2e;border:1px solid #333;border-radius:6px;padding:7px 13px;min-width:120px}
.stat-box .num{font-size:1.4rem;font-weight:700;color:var(--orange)}
.stat-box .lbl{font-size:.7rem;color:#888;text-transform:uppercase;letter-spacing:.5px}
.controls{display:flex;gap:10px;flex-wrap:wrap;padding:10px 20px;background:#12122a;border-bottom:1px solid #333;align-items:flex-end}
.controls input,.controls select{background:#222;border:1px solid #444;color:#ddd;padding:6px 9px;border-radius:4px;font-size:12px}
.controls input{width:240px}
.controls label{color:#888;font-size:11px;display:block;margin-bottom:3px}
.count-badge{background:var(--red);color:#fff;padding:5px 12px;border-radius:12px;font-size:12px;font-weight:700;white-space:nowrap}
.table-wrap{overflow-x:auto;max-height:calc(100vh - 215px);overflow-y:auto}
table{width:100%;border-collapse:collapse;font-size:12px}
thead th{position:sticky;top:0;background:#0d0d1a;color:#aaa;text-transform:uppercase;font-size:10px;letter-spacing:.5px;padding:8px 6px;text-align:left;border-bottom:2px solid #333;cursor:pointer;white-space:nowrap;user-select:none}
thead th:hover{color:var(--orange)}
thead th.sd::after{content:' ▼';color:var(--orange)}
thead th.sa::after{content:' ▲';color:var(--orange)}
tbody tr{border-bottom:1px solid #222;cursor:pointer}
tbody tr:hover{background:#1e1e3a}
tbody td{padding:5px 6px;vertical-align:top;max-width:210px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sc{background:rgba(192,57,43,.15);border-left:3px solid var(--red)}
.sh{background:rgba(230,126,34,.12);border-left:3px solid var(--orange)}
.sm{background:rgba(241,196,15,.08);border-left:3px solid var(--yellow)}
.sl{border-left:3px solid #333}
.badge{display:inline-block;padding:1px 5px;border-radius:3px;font-size:10px;font-weight:700;white-space:nowrap}
.br{background:rgba(192,57,43,.3);color:#ff8a80}
.bo{background:rgba(230,126,34,.3);color:#ffcc80}
.bg{background:rgba(39,174,96,.3);color:#a5d6a7}
.bk{background:#333;color:#888}
.bb{background:rgba(41,128,185,.3);color:#90caf9}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:1000;align-items:center;justify-content:center}
.modal-overlay.open{display:flex}
.modal{background:#1a1a2e;border:1px solid #444;border-radius:8px;padding:22px;max-width:660px;width:95%;max-height:85vh;overflow-y:auto;position:relative}
.modal h2{color:var(--orange);font-size:1.05rem;margin-bottom:3px}
.modal .sub{color:#888;font-size:.79rem;margin-bottom:14px}
.modal table{width:100%;font-size:12px}
.modal table td:first-child{color:#888;width:38%;padding-right:8px;font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.modal table td{padding:5px 4px;border-bottom:1px solid #2a2a4a}
.close-btn{position:absolute;top:10px;right:13px;background:none;border:none;color:#888;font-size:1.3rem;cursor:pointer}
.close-btn:hover{color:var(--red)}
.kc-banner{background:rgba(192,57,43,.2);border:1px solid var(--red);border-radius:4px;padding:7px 11px;margin-bottom:12px;color:#ff8a80;font-size:12px}
</style>
</head>
<body>
<header>
  <h1>STLCA — SEATTLE LANDLORD ACCOUNTABILITY REGISTER</h1>
  <p>Top 1,500 properties by complaint volume &nbsp;|&nbsp; Sources: SDCI Complaints 2003–2025 &nbsp;·&nbsp; RRIO Registration &nbsp;·&nbsp; King County Assessor</p>
</header>
<div class="stats-bar">
  <div class="stat-box"><div class="num" id="sTotal">—</div><div class="lbl">Properties Shown</div></div>
  <div class="stat-box"><div class="num" id="sComp">—</div><div class="lbl">Total Complaints</div></div>
  <div class="stat-box"><div class="num" id="sNov">—</div><div class="lbl">Total NOVs</div></div>
  <div class="stat-box"><div class="num" id="sOpen">—</div><div class="lbl">Open/Unresolved</div></div>
  <div class="stat-box"><div class="num" id="sUnits">—</div><div class="lbl">Total Units</div></div>
</div>
<div class="controls">
  <div><label>Search (owner, address, building, contact)</label><input type="text" id="search" placeholder="Type to filter..."></div>
  <div><label>RRIO Status</label>
    <select id="fRrio">
      <option value="">All</option>
      <option value="Active">Active</option>
      <option value="Violation">Violation</option>
      <option value="Late Violation">Late Violation</option>
      <option value="Expired">Expired</option>
      <option value="NONE">No RRIO (Unregistered)</option>
    </select>
  </div>
  <div><label>Min Complaints</label>
    <select id="fMinC"><option value="0">Any</option><option value="10">10+</option><option value="25">25+</option><option value="50">50+</option><option value="100">100+</option></select>
  </div>
  <div><label>Min NOVs</label>
    <select id="fMinN"><option value="0">Any</option><option value="1">1+</option><option value="5">5+</option><option value="10">10+</option></select>
  </div>
  <div><label>Sort By</label>
    <select id="fSort">
      <option value="complaints">Total Complaints ↓</option>
      <option value="comp_90d">90-Day Complaints ↓</option>
      <option value="nov">NOVs ↓</option>
      <option value="open">Open/Unresolved ↓</option>
      <option value="units">Units ↓</option>
    </select>
  </div>
  <span class="count-badge" id="cBadge">— shown</span>
</div>
<div class="table-wrap">
<table id="mainTable">
<thead><tr>
  <th data-c="rank">#</th>
  <th data-c="address">Address</th>
  <th data-c="kc_owner">Owner (KC Assessor)</th>
  <th data-c="rrio_contact">RRIO Contact</th>
  <th data-c="building">Building Name</th>
  <th data-c="units">Units</th>
  <th data-c="yr_built">Built</th>
  <th data-c="complaints">Complaints</th>
  <th data-c="comp_90d">90-Day</th>
  <th data-c="nov">NOVs</th>
  <th data-c="open">Open</th>
  <th data-c="rrio_status">RRIO Status</th>
  <th data-c="last_c">Last Complaint</th>
</tr></thead>
<tbody id="tbody"></tbody>
</table>
</div>
<div class="modal-overlay" id="modal">
  <div class="modal">
    <button class="close-btn" onclick="closeModal()">&#x2715;</button>
    <h2 id="mTitle"></h2>
    <div class="sub" id="mSub"></div>
    <div id="mBanner"></div>
    <table id="mTable"></table>
  </div>
</div>
<script>
const RAW = DATA_PLACEHOLDER;
let filtered=[...RAW], sCol='complaints', sDir=-1;

function num(n){return(typeof n==='number')?n.toLocaleString():(n||'—')}
function sev(r){if(r.complaints>=80||r.nov>=15)return'sc';if(r.complaints>=40||r.nov>=8)return'sh';if(r.complaints>=15||r.nov>=3)return'sm';return'sl'}
function rbadge(s){if(!s)return'<span class="badge bk">No RRIO</span>';const l=s.toLowerCase();if(l.includes('violation'))return'<span class="badge br">'+s+'</span>';if(l==='expired')return'<span class="badge bo">'+s+'</span>';if(l==='active')return'<span class="badge bg">'+s+'</span>';return'<span class="badge bb">'+s+'</span>'}

function applyFilters(){
  const q=document.getElementById('search').value.toLowerCase();
  const rf=document.getElementById('fRrio').value;
  const mc=parseInt(document.getElementById('fMinC').value)||0;
  const mn=parseInt(document.getElementById('fMinN').value)||0;
  sCol=document.getElementById('fSort').value;
  filtered=RAW.filter(r=>{
    if(q&&!(r.address+' '+r.kc_owner+' '+r.rrio_contact+' '+r.building+' '+r.owner).toLowerCase().includes(q))return false;
    if(rf){if(rf==='NONE'&&r.rrio_status)return false;if(rf!=='NONE'&&!r.rrio_status.toLowerCase().includes(rf.toLowerCase()))return false}
    if(r.complaints<mc)return false;
    if(r.nov<mn)return false;
    return true;
  });
  filtered.sort((a,b)=>sDir*((b[sCol]||0)-(a[sCol]||0)));
  render();
}

function render(){
  const tbody=document.getElementById('tbody');
  tbody.innerHTML='';
  const show=filtered.slice(0,500);
  show.forEach(r=>{
    const tr=document.createElement('tr');
    tr.className=sev(r);
    tr.innerHTML='<td>'+r.rank+'</td>'
      +'<td title="'+r.address+'">'+r.address+'</td>'
      +'<td title="'+r.kc_owner+'">'+r.kc_owner+'</td>'
      +'<td title="'+r.rrio_contact+'">'+r.rrio_contact+'</td>'
      +'<td title="'+r.building+'">'+r.building+'</td>'
      +'<td>'+r.units+'</td>'
      +'<td>'+r.yr_built+'</td>'
      +'<td><strong style="color:'+(r.complaints>=80?'#ff5252':r.complaints>=40?'#ffab40':'inherit')+'">'+r.complaints+'</strong></td>'
      +'<td>'+r.comp_90d+'</td>'
      +'<td><strong style="color:'+(r.nov>=10?'#ff5252':r.nov>=5?'#ffab40':'inherit')+'">'+r.nov+'</strong></td>'
      +'<td>'+r.open+'</td>'
      +'<td>'+rbadge(r.rrio_status)+'</td>'
      +'<td>'+r.last_c+'</td>';
    tr.onclick=()=>openModal(r);
    tbody.appendChild(tr);
  });
  const tot=filtered.reduce((s,r)=>s+r.complaints,0);
  const nov=filtered.reduce((s,r)=>s+r.nov,0);
  const opn=filtered.reduce((s,r)=>s+r.open,0);
  const unt=filtered.reduce((s,r)=>s+(parseInt(r.units)||0),0);
  document.getElementById('sTotal').textContent=filtered.length.toLocaleString();
  document.getElementById('sComp').textContent=tot.toLocaleString();
  document.getElementById('sNov').textContent=nov.toLocaleString();
  document.getElementById('sOpen').textContent=opn.toLocaleString();
  document.getElementById('sUnits').textContent=unt.toLocaleString();
  document.getElementById('cBadge').textContent=Math.min(show.length,filtered.length)+' of '+filtered.length+' shown';
}

function openModal(r){
  document.getElementById('mTitle').textContent=r.building||r.address;
  document.getElementById('mSub').textContent=r.address+(r.zip?', Seattle WA '+r.zip:'');
  document.getElementById('mBanner').innerHTML=r.known_case?'<div class="kc-banner">&#9888; KNOWN CASE: '+r.known_case+'</div>':'';
  const rows=[
    ['KC Assessor Owner',r.kc_owner||'—'],['RRIO Contact',r.rrio_contact||'—'],
    ['Previous Owner',r.prev_owner||'—'],['Last Sale Date',r.last_sale_d||'—'],
    ['Last Sale Price',r.last_sale_p?'$'+parseInt(r.last_sale_p).toLocaleString():'—'],
    ['PIN',r.pin||'—'],['',''],
    ['RRIO Reg #',r.rrio_num||'NOT REGISTERED'],['RRIO Status',r.rrio_status||'NOT REGISTERED'],
    ['RRIO Type',r.rrio_type||'—'],['Registered',r.rrio_reg||'—'],['Expires',r.rrio_exp||'—'],
    ['',''],
    ['Units',r.units||'—'],['Year Built',r.yr_built||'—'],['Stories',r.stories||'—'],
    ['',''],
    ['Total Complaints',r.complaints.toLocaleString()],['90-Day Complaints',r.comp_90d.toLocaleString()],
    ['NOVs Issued',r.nov.toLocaleString()],['Open/Unresolved',r.open.toLocaleString()],
    ['First Complaint',r.first_c||'—'],['Last Complaint',r.last_c||'—'],
    ['',''],
    ['Land Value',r.land_val?'$'+parseInt(r.land_val).toLocaleString():'—'],
    ['Improvement Value',r.impr_val?'$'+parseInt(r.impr_val).toLocaleString():'—'],
    ['Total Assessed',r.total_val?'$'+parseInt(r.total_val).toLocaleString():'—'],
    ['',''],
    ['Flags',r.flags||'—'],
  ];
  document.getElementById('mTable').innerHTML=rows.map(([k,v])=>k?'<tr><td>'+k+'</td><td>'+v+'</td></tr>':'').join('');
  document.getElementById('modal').classList.add('open');
}
function closeModal(){document.getElementById('modal').classList.remove('open')}
document.getElementById('modal').addEventListener('click',e=>{if(e.target===document.getElementById('modal'))closeModal()});

document.querySelectorAll('thead th[data-c]').forEach(th=>{
  th.addEventListener('click',()=>{
    const c=th.dataset.c;
    if(sCol===c){sDir*=-1}else{sCol=c;sDir=-1}
    document.querySelectorAll('thead th').forEach(t=>t.classList.remove('sd','sa'));
    th.classList.add(sDir===-1?'sd':'sa');
    document.getElementById('fSort').value=sCol;
    applyFilters();
  });
});
['search','fRrio','fMinC','fMinN','fSort'].forEach(id=>{
  const el=document.getElementById(id);
  el.addEventListener('change',applyFilters);
  if(id==='search')el.addEventListener('input',applyFilters);
});
applyFilters();
</script>
</body>
</html>"""

# Inject data
html = html.replace('DATA_PLACEHOLDER', data_json)

out_path = os.path.join(WEB, 'LANDLORD_ACCOUNTABILITY_REGISTER.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Saved: {out_path}")
print(f"File size: {os.path.getsize(out_path)/1024/1024:.1f} MB")
