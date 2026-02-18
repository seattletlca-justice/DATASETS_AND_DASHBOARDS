# DATASETS_AND_DASHBOARDS
PAYLOAD GENERATOR

## Which file is the real dashboard file?
If you are confused about filenames, use this rule:

- **Main editable dashboard file**: `STLCA_homepage_dashboard_v7b_2026-01-15.html`
- **Publish file for hosting**: `index.html`

Right now those two files are the same content.
When you make dashboard edits, edit the main file first, then copy it to `index.html` before pushing.

```bash
cp STLCA_homepage_dashboard_v7b_2026-01-15.html index.html
```

---

## Super-simple: get your dashboard online (no Git required)
If GitHub feels confusing right now, use this first:

1. Open https://app.netlify.com/drop
2. Drag `index.html` from your computer into the page.
3. Netlify immediately gives you a public URL to share.

That is the fastest way to share your dashboard with people.

---

## GitHub Pages path (if you want a permanent repo URL)

### What goes where
- **Your computer**: where you edit `index.html`
- **GitHub.com**: where you upload files and turn on Pages

Both are required for a GitHub Pages link.

### 1) Keep dashboard file in repo root
Current dashboard file:
- `STLCA_homepage_dashboard_v7b_2026-01-15.html`

### 2) Create `index.html` in repo root
GitHub Pages serves `index.html` by default:

```bash
cp STLCA_homepage_dashboard_v7b_2026-01-15.html index.html
```

### 3) Push to GitHub (to the branch Pages uses)
Use your default branch (usually `main`):

```bash
git add index.html STLCA_homepage_dashboard_v7b_2026-01-15.html
git commit -m "Update dashboard"
git push origin main
```

### 4) Enable Pages
In GitHub:
- **Settings** → **Pages**
- **Source**: `Deploy from a branch`
- **Branch**: `main`, folder `/ (root)`
- Save

### 5) Your public URL format
- `https://<your-github-username>.github.io/DATASETS_AND_DASHBOARDS/`

---

## If you still see 403/404
Use this checklist in order:

1. `index.html` exists in the repository root on GitHub (not only locally).
2. Pages is set to **main** + `/ (root)`.
3. You pushed to `main` (not another branch).
4. Wait 1–3 minutes, then hard refresh (`Ctrl+Shift+R` or `Cmd+Shift+R`).
5. In **Settings → Pages**, check for build/deploy errors.

If all 5 are true and it still fails, deploy with Netlify Drop as the temporary share link, then come back to Pages.

---

## Mobile + interactivity notes
- The dashboard is client-side HTML/JS, so filters/charts remain interactive on mobile browsers.
- If charts look stale after deploy, hard refresh.
- Every change requires a new push to update GitHub Pages.
