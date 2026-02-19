param(
  [string]$DashboardFile = "STLCA_homepage_dashboard_v7b_2026-01-15.html"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
  Write-Error "This folder is not a git repository. Run: git clone <repo-url> then cd into that folder."
}

function Resolve-DashboardFile {
  param([string]$Preferred)

  if (Test-Path $Preferred) {
    return $Preferred
  }

  $htmlFiles = Get-ChildItem -File *.html -ErrorAction SilentlyContinue
  if (-not $htmlFiles) {
    Write-Error "No .html files found in this folder."
  }

  # If only index exists, treat it as the dashboard source and continue.
  if ($htmlFiles.Count -eq 1 -and $htmlFiles[0].Name -ieq "index.html") {
    return "index.html"
  }

  # Otherwise prefer the newest non-index html as likely editable source.
  $candidate = $htmlFiles |
    Where-Object { $_.Name -ine "index.html" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if ($candidate) {
    Write-Host "Dashboard file '$Preferred' not found. Using '$($candidate.Name)' instead." -ForegroundColor Yellow
    return $candidate.Name
  }

  Write-Error "Dashboard file '$Preferred' not found, and no alternate source file is available."
}

$source = Resolve-DashboardFile -Preferred $DashboardFile

if ($source -ine "index.html") {
  Copy-Item $source "index.html" -Force
  Write-Host "Copied '$source' -> 'index.html'." -ForegroundColor Cyan
} else {
  Write-Host "Using existing 'index.html' (no separate source file found)." -ForegroundColor Cyan
}

New-Item ".nojekyll" -ItemType File -Force | Out-Null

git add index.html .nojekyll

$hasChanges = git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
  git commit -m "Publish dashboard"
} else {
  Write-Host "No new changes to commit. Continuing to push..." -ForegroundColor Yellow
}

git push origin main

Write-Host "Done. Now check GitHub: Settings > Pages > main /(root)." -ForegroundColor Green
