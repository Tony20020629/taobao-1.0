# -*- coding: utf-8 -*-
import sqlite3

db_path = r'e:\NewProject\taobao\backend\taobao_monitor.db'
print(f"数据库路径: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('\n===== 商品列表 =====')
cursor.execute('SELECT id, name, url, current_price FROM goods')
rows = cursor.fetchall()
for row in rows:
    print(f'ID: {row[0]}')
    print(f'  名称: {row[1]}')
    print(f'  URL: {row[2][:80]}...')
    print(f'  当前价格: ¥{row[3]}')
    print()

print('\n===== 最近5条价格记录 =====')
cursor.execute('SELECT goods_id, price, collected_at FROM price_history ORDER BY collected_at DESC LIMIT 5')
rows2 = cursor.fetchall()
for row in rows2:
    print(f'商品ID: {row[0]}, 价格: ¥{row[1]}, 采集时间: {row[2]}')

conn.close()
