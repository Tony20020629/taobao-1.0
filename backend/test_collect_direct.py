# -*- coding: utf-8 -*-
"""直接测试价格采集器"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.price_collector import TaobaoPriceCollector
from app.agents.taobao_login import TaobaoLogin


async def test_collect():
    print("[测试] 开始测试价格采集器...")
    
    # 检查Cookie
    login = TaobaoLogin()
    cookies = login.load_cookies()
    print(f"[测试] 已加载 {len(cookies)} 个Cookie")
    print(f"[测试] 登录状态: {'已登录' if login.is_logged_in() else '未登录'}")
    
    # 创建采集器
    collector = TaobaoPriceCollector()
    
    goods_url = "https://detail.tmall.com/item.htm?id=814756521192"
    print(f"[测试] 开始采集: {goods_url}")
    
    try:
        result = await collector.collect_price(goods_url)
        
        if result:
            print(f"\n✅ 采集成功!")
            print(f"  商品名称: {result.get('name', '未知')}")
            print(f"  价格: ¥{result.get('price', 0)}")
            print(f"  促销信息: {result.get('promotion_info', '')}")
            print(f"  采集时间: {result.get('collected_at', '')}")
        else:
            print("\n❌ 采集失败: 返回结果为None")
    except Exception as e:
        import traceback
        print(f"\n❌ 采集异常:")
        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_collect())
