@echo off
title Testing Price Collection
cd /d e:\NewProject\taobao\backend

echo ========================================
echo Starting Price Collection Test
echo ========================================
echo.

REM Run the price collector directly
python -c "import asyncio; import sys; sys.path.insert(0, '.'); from app.agents.price_collector import TaobaoPriceCollector; collector = TaobaoPriceCollector(); result = asyncio.run(collector.collect_price('https://detail.tmall.com/item.htm?id=814756521192')); print('\n========== RESULT =========='); print('Success:', result is not None); print('Price:', result.get('price') if result else 'N/A'); print('Name:', result.get('name') if result else 'N/A')"

echo.
echo ========================================
echo Test Complete
echo ========================================
pause
