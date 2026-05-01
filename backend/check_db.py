import sqlite3
import os

db_path = r'e:\NewProject\taobao\backend\taobao_monitor.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=' * 80)
print('DATABASE - Goods Table')
print('=' * 80)
cursor.execute('SELECT id, name, url, current_price, avg_price, min_price, max_price FROM goods')
rows = cursor.fetchall()
for row in rows:
    print(f'ID: {row[0]}')
    print(f'Name: {row[1]}')
    print(f'URL: {row[2][:60]}...')
    print(f'Current Price: {row[3]}')
    print(f'Avg Price: {row[4]}')
    print(f'Min Price: {row[5]}')
    print(f'Max Price: {row[6]}')
    print()

print('=' * 80)
print('DATABASE - Price History (Last 10 records)')
print('=' * 80)
cursor.execute('SELECT id, goods_id, price, promotion_info, change_type, collected_at FROM price_history ORDER BY id DESC LIMIT 10')
rows = cursor.fetchall()
for row in rows:
    print(f'ID: {row[0]}, GoodsID: {row[1]}, Price: {row[2]}, Type: {row[4]}, Time: {row[5]}')
    if row[3]:
        print(f'  Promotion: {row[3][:100]}')

conn.close()
