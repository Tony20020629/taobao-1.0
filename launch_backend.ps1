$ErrorActionPreference = "Continue"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Backend Server..." -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
Set-Location -Path "e:\NewProject\taobao\backend"
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Check if python exists
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($pythonPath) {
    Write-Host "Python found at: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "Python not found, trying alternative..." -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting uvicorn server on http://0.0.0.0:8000" -ForegroundColor Green
Write-Host ""

# Start uvicorn
& python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
