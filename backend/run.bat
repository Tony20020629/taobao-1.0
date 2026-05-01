@echo off
cd /d e:\NewProject\taobao\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
