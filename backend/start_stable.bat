@echo off
cd /d e:\NewProject\taobao\backend
echo Starting Backend Server (no reload)...
C:\Users\22343\.conda\envs\taobao\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
