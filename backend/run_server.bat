@echo off
cd /d e:\NewProject\taobao\backend
conda activate taobao
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
