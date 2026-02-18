# DATASETS_AND_DASHBOARDS
PAYLOAD GENERATOR

## Publish the dashboard to a public URL (GitHub Pages)

You can host this dashboard as a static site in a few minutes and get a shareable link.

### 1) Keep the dashboard file in the repo root
Current file:
- `STLCA_homepage_dashboard_v7b_2026-01-15.html`

### 2) Create `index.html`
GitHub Pages serves `index.html` by default. Copy/rename your dashboard file:

```bash
cp STLCA_homepage_dashboard_v7b_2026-01-15.html index.html
```

### 3) Push to GitHub
Push this branch/repo to GitHub.

### 4) Enable GitHub Pages
In GitHub:
- **Settings** → **Pages**
- **Source**: `Deploy from a branch`
- **Branch**: `main` (or your default branch), folder `/ (root)`
- Save

### 5) Your public URL
GitHub will give you a URL in this format:
- `https://<your-github-username>.github.io/<repo-name>/`

Example for this repo name:
- `https://<your-github-username>.github.io/DATASETS_AND_DASHBOARDS/`

## Mobile + interactivity notes
- This dashboard is client-side HTML/JS and remains fully interactive on mobile browsers.
- If charts appear stale, do a hard refresh after deployment.
- If you change files, push again; GitHub Pages updates in ~1–3 minutes.

## Fast alternatives
If you want an even faster publish flow, drag-and-drop `index.html` into:
- Netlify Drop
- Cloudflare Pages
- Vercel

These also produce public shareable URLs.
