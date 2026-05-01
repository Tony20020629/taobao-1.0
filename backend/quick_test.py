import asyncio
import sys
sys.path.insert(0, r'e:\NewProject\taobao\backend')

from app.agents.price_collector import TaobaoPriceCollector

async def main():
    url = 'https://detail.tmall.com/item.htm?id=814756521192'
    
    collector = TaobaoPriceCollector()
    result = await collector.collect_price(url)
    
    if result:
        print(f"SUCCESS - Price: {result.get('price')}")
    else:
        print("FAILED")

if __name__ == '__main__':
    asyncio.run(main())
