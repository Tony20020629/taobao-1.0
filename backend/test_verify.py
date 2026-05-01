# -*- coding: utf-8 -*-
"""验证当前采集的价格是否正确"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.agents.price_collector import TaobaoPriceCollector
from app.agents.taobao_login import TaobaoLogin


async def verify():
    print("[验证] 开始验证价格采集...")
    
    login = TaobaoLogin()
    cookies = login.load_cookies()
    print(f"[验证] 已加载 {len(cookies)} 个Cookie")
    print(f"[验证] 登录状态: {'已登录' if login.is_logged_in() else '未登录'}")
    
    collector = TaobaoPriceCollector()
    goods_url = "https://detail.tmall.com/item.htm?id=814756521192"
    
    print(f"[验证] 采集商品: {goods_url}")
    result = await collector.collect_price(goods_url)
    
    if result:
        print(f"\n✅ 采集结果:")
        print(f"  商品名称: {result.get('name')}")
        print(f"  价格: ¥{result.get('price')}")
        print(f"  促销: {result.get('promotion_info')}")
    else:
        print("\n❌ 采集失败")


if __name__ == "__main__":
    asyncio.run(verify())
