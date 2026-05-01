# -*- coding: utf-8 -*-
"""完整的价格采集流程测试"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.price_collector import TaobaoPriceCollector

async def main():
    print("=" * 60)
    print("开始完整测试淘宝价格采集流程")
    print("=" * 60)
    
    # 商品URL
    goods_url = "https://detail.tmall.com/item.htm?id=814756521192"
    
    print(f"\n[1] 商品URL: {goods_url}")
    print(f"[2] 开始启动价格采集...")
    print()
    
    collector = TaobaoPriceCollector()
    result = await collector.collect_price(goods_url)
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    if result:
        print(f"采集状态: 成功")
        print(f"商品名称: {result.get('name', '未知')}")
        print(f"当前价格: {result.get('price', 'N/A')}")
        print(f"促销信息: {result.get('promotion_info', '无')}")
        print(f"采集时间: {result.get('collected_at', 'N/A')}")
        
        # 验证价格是否合理
        price = result.get('price', 0)
        if price > 0 and price < 999999:
            print(f"\n价格验证: 通过 (价格 {price} 元在合理范围内)")
        else:
            print(f"\n价格验证: 失败 (价格 {price} 不在合理范围内)")
    else:
        print(f"采集状态: 失败")
        print("\n可能原因:")
        print("1. 淘宝反爬拦截")
        print("2. Cookie已过期")
        print("3. 页面结构变化")
        print("4. 网络问题")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
