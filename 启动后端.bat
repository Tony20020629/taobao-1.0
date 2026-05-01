@echo off
title 淘宝价格监测系统 - 后端服务
chcp 65001 >nul 2>&1
cd /d %~dp0backend
echo ============================================================
echo   正在启动淘宝价格监测系统后端服务...
echo   访问地址: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo ============================================================
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
