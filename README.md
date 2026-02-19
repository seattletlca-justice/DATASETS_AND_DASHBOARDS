# DATASETS_AND_DASHBOARDS
PAYLOAD GENERATOR


## Data + traceability files
- `payload.json` is the runtime data source for the dashboard.
- `TRACEABILITY.md` documents metric definitions and district reconciliation checks.

## Fastest publish (recommended)
If you already have `index.html` in this repo folder, just run:

```powershell
cd C:\Users\stlca\stlca_data\github\DATASETS_AND_DASHBOARDS
powershell -ExecutionPolicy Bypass -File .\publish.ps1
```

`publish.ps1` now auto-detects your source file:
- Uses `STLCA_homepage_dashboard_v7b_2026-01-15.html` if present
- If missing, uses the newest non-`index.html` file
- If only `index.html` exists, publishes that safely

---

## Do this now (Windows PowerShell)
Run these commands in **PowerShell** from your project folder.

```powershell
# 1) Make sure you're in the right folder
cd C:\Users\stlca\stlca_data\DATASETS_AND_DASHBOARDS
Get-ChildItem

# 2) If your dashboard filename is different, find it
Get-ChildItem *.html

# 3) Run the publish helper (auto-detects HTML source safely)
powershell -ExecutionPolicy Bypass -File .\publish.ps1
```

Then on GitHub website:
1. Repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / Folder: **(root)**
4. Save and wait 1–3 minutes

---

## If you get: `fatal: not a git repository`
You are in a normal folder, not a cloned git repo yet.

Run this once:

```powershell
cd C:\Users\stlca\stlca_data
git clone https://github.com/<your-github-username>/DATASETS_AND_DASHBOARDS.git
cd .\DATASETS_AND_DASHBOARDS
```

Now run the PowerShell publish block above.

---

## If you get: `Cannot find path ... STLCA_homepage_dashboard...`
That means your HTML file has a different name in that folder.

Find it:

```powershell
Get-ChildItem *.html
```

Then copy using the **actual** filename, for example:

```powershell
Copy-Item .\my-dashboard.html .\index.html -Force
```

---

## Fast no-terminal backup (works immediately)
If GitHub Pages is still blocked and you need a public URL now:
1. Open https://app.netlify.com/drop
2. Drag `index.html`
3. Share the URL Netlify gives you

---

## Which file to edit vs publish
- Edit: `STLCA_homepage_dashboard_v7b_2026-01-15.html` (or your current dashboard html filename)
- Publish: `index.html`

Before each publish, copy edit file → `index.html`.

---

## Quick 403 checklist
1. `index.html` exists in repo root on GitHub
2. GitHub Pages is set to `main` + `(root)`
3. You pushed to `main` (not another branch)
4. Wait 1–3 minutes and hard refresh

Expected URL format:
`https://<your-github-username>.github.io/DATASETS_AND_DASHBOARDS/`
