import asyncio
import json
import sys
import os

sys.path.insert(0, r'e:\NewProject\taobao\backend')

from app.agents.price_collector import TaobaoPriceCollector

async def main():
    url = 'https://detail.tmall.com/item.htm?id=814756521192'
    result_file = r'e:\NewProject\taobao\backend\result.json'
    
    print('Starting price collection...')
    
    collector = TaobaoPriceCollector()
    result = await collector.collect_price(url)
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    if result:
        print(f'Done! Price: {result.get("price")}')
    else:
        print('Failed! Check result.json for details')

if __name__ == '__main__':
    asyncio.run(main())
