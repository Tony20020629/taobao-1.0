@echo off
title 淘宝价格监测系统 - 后端服务
chcp 65001 >nul 2>&1
cd /d "%~dp0backend"

echo.
echo ============================================================
echo    淘宝价格监测系统 - 后端服务
echo    访问地址: http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo ============================================================
echo.
echo [1/3] 正在切换到后端目录...
echo [2/3] 正在启动uvicorn服务器...
echo.
echo 等待服务器启动，看到 "Application startup complete" 表示成功
echo.
echo ============================================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ============================================================
echo    服务器已停止
echo ============================================================
pause
