# DATASETS_AND_DASHBOARDS
PAYLOAD GENERATOR

## TL;DR (just do this)
1. Open terminal in your local `DATASETS_AND_DASHBOARDS` folder.
2. Run this exact block:

```bash
cp STLCA_homepage_dashboard_v7b_2026-01-15.html index.html
touch .nojekyll
git add index.html STLCA_homepage_dashboard_v7b_2026-01-15.html .nojekyll
git commit -m "Publish dashboard"
git push origin main
```

3. On GitHub: **Settings → Pages → Deploy from a branch → main + /(root)**.
4. Wait 1–3 minutes, refresh your site.

---

## What does "from this repo folder" mean?
It means the folder that contains these files:
- `README.md`
- `STLCA_homepage_dashboard_v7b_2026-01-15.html`
- `index.html`

If you run `pwd` and see this (or your local equivalent), you are in the right place:

```bash
/workspace/DATASETS_AND_DASHBOARDS
```

On your own computer, first move into your local repo folder, then run publish commands:

```bash
cd <path-to-your-local>/DATASETS_AND_DASHBOARDS
```

Quick check before publishing:

```bash
pwd
ls
```

You should see `README.md`, `STLCA_homepage_dashboard_v7b_2026-01-15.html`, and `index.html` listed.

---

## STOP THE CHAOS: do these exact steps to publish
If you are getting 403 and just want this live, run these commands in this repo folder:

```bash
cp STLCA_homepage_dashboard_v7b_2026-01-15.html index.html
touch .nojekyll
git add index.html STLCA_homepage_dashboard_v7b_2026-01-15.html .nojekyll
git commit -m "Publish dashboard"
git push origin main
```

Then on GitHub (website):
1. Open this repository.
2. Click **Settings → Pages**.
3. Set **Source = Deploy from a branch**.
4. Set **Branch = main** and **Folder = /(root)**.
5. Save.
6. Wait 1–3 minutes and hard refresh.

Your URL should be:
- `https://<your-github-username>.github.io/DATASETS_AND_DASHBOARDS/`

---

## Which file is the real dashboard file?
Use this rule:

- **Main editable dashboard file**: `STLCA_homepage_dashboard_v7b_2026-01-15.html`
- **Publish file for hosting**: `index.html`

Right now those two files should match. Before every publish, run:

```bash
cp STLCA_homepage_dashboard_v7b_2026-01-15.html index.html
```

---

## If Git says you have "resolving" to do
That means merge conflicts happened. Run:

```bash
git status
```

If you want to throw away the broken merge and go back to normal:

```bash
git merge --abort || git rebase --abort
```

Then publish again with the 5-command block at the top.

---

## If you still see 403
Check these in order:

1. You are in the correct repo: `DATASETS_AND_DASHBOARDS` (not another repo).
2. `index.html` exists in this repo root on GitHub.
3. Pages is set to **main** + `/ (root)`.
4. You pushed to `main` (not another branch).
5. In **Settings → Pages**, check if the build failed.

If all are true and you still need a share link immediately, use:
- https://app.netlify.com/drop
- Drag `index.html`
- Share the URL it gives you

---

## Mobile + interactivity notes
- The dashboard is client-side HTML/JS, so filters/charts remain interactive on mobile browsers.
- If charts look stale after deploy, hard refresh.
- Every change requires a new push to update GitHub Pages.
