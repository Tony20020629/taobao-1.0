Set-Location -Path "e:\NewProject\taobao\backend"
Write-Host "========================================"
Write-Host "Starting Backend Server..."
Write-Host "========================================"
& conda run -n taobao python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
