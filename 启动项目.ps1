# PowerShell启动脚本
# 启动后端服务
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd e:\NewProject\taobao\backend; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

# 等待3秒
Start-Sleep -Seconds 3

# 启动前端服务  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd e:\NewProject\taobao\frontend; npm run dev" -WindowStyle Normal

Write-Host "========================================" -ForegroundColor Green
Write-Host "   项目启动中，请稍候..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 等待5秒后测试后端服务
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "正在检查后端服务状态..." -ForegroundColor Yellow

# 测试后端服务
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 后端服务启动成功！" -ForegroundColor Green
        Write-Host "   访问地址: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "   API文档: http://localhost:8000/docs" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ 后端服务可能还在启动中..." -ForegroundColor Yellow
}

# 测试前端服务
Write-Host ""
Write-Host "正在检查前端服务状态..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 前端服务启动成功！" -ForegroundColor Green
        Write-Host "   访问地址: http://localhost:3000" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ 前端服务可能还在启动中..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   项目已启动！" -ForegroundColor Green
Write-Host "   前端: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   后端: http://localhost:8000" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
