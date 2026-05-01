# -*- coding: utf-8 -*-
"""启动后端服务器"""
import uvicorn
import sys
import os

# 切换到backend目录
os.chdir(r"e:\NewProject\taobao\backend")
sys.path.insert(0, r"e:\NewProject\taobao\backend")

print("="*60)
print("正在启动淘宝价格监测系统后端服务...")
print("访问地址: http://localhost:8000")
print("API文档: http://localhost:8000/docs")
print("="*60)

# 启动服务器
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
