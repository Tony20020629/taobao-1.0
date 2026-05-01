@echo off
chcp 65001 >nul
cd /d %~dp0backend
echo Starting FastAPI backend server...
conda run -n taobao python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
