# -*- coding: utf-8 -*-
import subprocess
import os

frontend_dir = r"e:\NewProject\taobao\frontend"

print("Starting frontend server...")
print(f"Directory: {frontend_dir}")

# Start npm run dev in a new window
subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=frontend_dir,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

print("Frontend server started!")
print("Visit: http://localhost:3000")
