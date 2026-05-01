# -*- coding: utf-8 -*-
"""
测试通义千问模型连接和Agent功能
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

# 加载.env文件
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"[配置] {key} = {value[:20]}..." if len(value) > 20 else f"[配置] {key} = {value}")

load_env_file()

print(f"\n[测试] 环境变量已加载:")
print(f"  API Key: {os.environ.get('OPENAI_API_KEY', '未设置')[:20]}...")
print(f"  Base URL: {os.environ.get('OPENAI_BASE_URL', '未设置')}")
print(f"  Model: {os.environ.get('OPENAI_MODEL_NAME', '未设置')}")

print("\n[测试] 正在测试通义千问模型连接...")
try:
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL_NAME"),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        openai_api_base=os.environ.get("OPENAI_BASE_URL"),
        temperature=0.7,
    )
    
    print("[测试] LLM初始化成功，正在发送测试请求...")
    
    response = llm.invoke("你好，请简单介绍一下你自己。只用一句话回答。")
    print(f"\n[成功] 通义千问模型回复: {response.content}")
    
except Exception as e:
    print(f"\n[错误] 模型连接失败: {type(e).__name__}: {e}")

print("\n[测试] 测试完成")
