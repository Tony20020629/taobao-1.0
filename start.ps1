Set-Location -Path "e:\NewProject\taobao\backend"
Write-Host "Starting Backend Server..."
$env:Path = "C:\Users\22343\.conda\envs\taobao;" + $env:Path
& python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
