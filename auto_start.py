# -*- coding: utf-8 -*-
"""自动启动前后端服务"""
import subprocess
import os
import sys
import time

def start_backend():
    """启动后端服务"""
    print("=" * 60)
    print("Starting Backend Server...")
    print("=" * 60)
    
    backend_dir = r"e:\NewProject\taobao\backend"
    python_exe = sys.executable
    
    cmd = [
        python_exe, "-m", "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    print(f"Working directory: {backend_dir}")
    print(f"Python: {python_exe}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    proc = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print(f"Backend PID: {proc.pid}")
    time.sleep(3)
    return proc

def start_frontend():
    """启动前端服务"""
    print()
    print("=" * 60)
    print("Starting Frontend Server...")
    print("=" * 60)
    
    frontend_dir = r"e:\NewProject\taobao\frontend"
    
    cmd = ["npm", "run", "dev"]
    
    print(f"Working directory: {frontend_dir}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    proc = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print(f"Frontend PID: {proc.pid}")
    time.sleep(3)
    return proc

if __name__ == "__main__":
    print()
    print("#" * 60)
    print("#   淘宝价格监测系统 - 自动启动脚本")
    print("#" * 60)
    print()
    
    backend_proc = start_backend()
    frontend_proc = start_frontend()
    
    print()
    print("=" * 60)
    print("Services started!")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop all services...")
    
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done!")
