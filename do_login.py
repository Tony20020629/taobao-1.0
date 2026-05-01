# -*- coding: utf-8 -*-
"""
淘宝登录执行脚本
"""
import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.taobao_login import TaobaoLogin

async def main():
    login_manager = TaobaoLogin()
    
    # 使用用户提供的手机号
    phone = "15359679153"
    print(f"开始登录淘宝，手机号: {phone}")
    
    result = await login_manager.login(phone)
    
    if result:
        print("✅ 登录成功！")
        print(f"已保存 {len(result)} 个Cookie")
    else:
        print("❌ 登录失败，请检查浏览器窗口中的操作")

if __name__ == "__main__":
    asyncio.run(main())
