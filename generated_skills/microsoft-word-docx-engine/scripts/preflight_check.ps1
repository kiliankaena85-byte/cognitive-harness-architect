# Preflight Diagnostic Script for microsoft-word-docx-engine
Write-Host "Checking preflight environment for microsoft-word-docx-engine..." -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($env:DOCX_TEMPLATE_KEY)) {
    Write-Host "[FAIL] Missing environment variable: DOCX_TEMPLATE_KEY" -ForegroundColor Red
    Write-Host "Please set DOCX_TEMPLATE_KEY in your environment or project .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Credential DOCX_TEMPLATE_KEY is present." -ForegroundColor Green
exit 0
