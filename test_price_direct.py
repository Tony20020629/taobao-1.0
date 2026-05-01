# -*- coding: utf-8 -*-
import asyncio
import sys
import os

sys.path.insert(0, r'e:\NewProject\taobao\backend')

from app.agents.price_collector import TaobaoPriceCollector

async def main():
    print("=" * 60)
    print("Testing Taobao Price Collection")
    print("=" * 60)
    
    goods_url = "https://detail.tmall.com/item.htm?id=814756521192"
    print(f"URL: {goods_url}")
    
    collector = TaobaoPriceCollector()
    result = await collector.collect_price(goods_url)
    
    print("\n" + "=" * 60)
    if result:
        print("SUCCESS!")
        print(f"Price: {result.get('price')}")
        print(f"Name: {result.get('name')}")
    else:
        print("FAILED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
