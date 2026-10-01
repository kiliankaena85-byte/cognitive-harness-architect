# Preflight Diagnostic Script for cloudflare-workers
Write-Host "Checking preflight environment for cloudflare-workers..." -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($env:CLOUDFLARE_API_TOKEN)) {
    Write-Host "[FAIL] Missing environment variable: CLOUDFLARE_API_TOKEN" -ForegroundColor Red
    Write-Host "Please set CLOUDFLARE_API_TOKEN in your environment or project .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Credential CLOUDFLARE_API_TOKEN is present." -ForegroundColor Green
exit 0
