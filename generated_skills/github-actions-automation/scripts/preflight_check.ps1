# Preflight Diagnostic Script for github-actions-automation
Write-Host "Checking preflight environment for github-actions-automation..." -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) {
    Write-Host "[FAIL] Missing environment variable: GITHUB_TOKEN" -ForegroundColor Red
    Write-Host "Please set GITHUB_TOKEN in your environment or project .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Credential GITHUB_TOKEN is present." -ForegroundColor Green
exit 0
