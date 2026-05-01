# -*- coding: utf-8 -*-
import asyncio
import sys
import os
sys.path.insert(0, r'e:\NewProject\taobao\backend')

from app.agents.price_collector import TaobaoPriceCollector

async def main():
    print('='*60)
    print('Testing Price Collection...')
    print('='*60)
    
    url = 'https://detail.tmall.com/item.htm?id=814756521192'
    print(f'URL: {url}')
    
    collector = TaobaoPriceCollector()
    result = await collector.collect_price(url)
    
    print()
    print('='*60)
    print('Result:')
    print('='*60)
    if result:
        print(f'SUCCESS!')
        print(f'Price: {result.get("price")}')
        print(f'Name: {result.get("name")}')
    else:
        print('FAILED!')
    print('='*60)

if __name__ == '__main__':
    asyncio.run(main())
