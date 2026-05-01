import subprocess
import os
import sys

# Change to backend directory
os.chdir(r'e:\NewProject\taobao\backend')

# Start uvicorn
subprocess.run([
    sys.executable, '-m', 'uvicorn', 'main:app', 
    '--host', '0.0.0.0', '--port', '8000', '--reload'
])
