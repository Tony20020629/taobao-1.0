@echo off
title 淘宝价格监测系统 - 前端服务
chcp 65001 >nul 2>&1
cd /d %~dp0frontend
echo ============================================================
echo   正在启动淘宝价格监测系统前端服务...
echo   访问地址: http://localhost:3000
echo ============================================================
echo.
npm run dev
pause
