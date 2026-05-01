# -*- coding: utf-8 -*-
"""
独立测试价格采集脚本
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.price_collector import TaobaoPriceCollector

async def main():
    # 商品URL
    goods_url = "https://detail.tmall.com/item.htm?id=814756521192"
    
    print("=" * 60)
    print("开始测试淘宝价格采集功能")
    print(f"商品URL: {goods_url}")
    print("=" * 60)
    
    collector = TaobaoPriceCollector()
    result = await collector.collect_price(goods_url)
    
    print("\n" + "=" * 60)
    if result:
        print("✅ 采集成功！")
        print(f"商品名称: {result.get('name', '未知')}")
        print(f"当前价格: ¥{result.get('price', 'N/A')}")
        print(f"促销信息: {result.get('promotion_info', '无')}")
        print(f"采集时间: {result.get('collected_at', 'N/A')}")
    else:
        print("❌ 采集失败！")
        print("可能原因:")
        print("1. 淘宝反爬拦截")
        print("2. Cookie已过期")
        print("3. 页面结构变化")
        print("4. 网络问题")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
