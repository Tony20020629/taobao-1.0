import os
import subprocess
import sys

# Change to backend directory
backend_dir = r"e:\NewProject\taobao\backend"
os.chdir(backend_dir)

print(f"Working directory: {os.getcwd()}")
print("Starting FastAPI server...")

# Run uvicorn directly
result = subprocess.run(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    cwd=backend_dir
)

print(f"Server exited with code: {result.returncode}")
