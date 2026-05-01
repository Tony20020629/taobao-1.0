import sqlite3

db_path = r'e:\NewProject\taobao\backend\taobao_monitor.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("Current Goods Price:")
print("=" * 60)
cursor.execute("SELECT id, name, current_price, avg_price, min_price, max_price FROM goods WHERE id = 7")
row = cursor.fetchone()
print(f"ID: {row[0]}")
print(f"Name: {row[1]}")
print(f"Current: {row[2]}")
print(f"Avg: {row[3]}")
print(f"Min: {row[4]}")
print(f"Max: {row[5]}")

print("\n" + "=" * 60)
print("Price History:")
print("=" * 60)
cursor.execute("SELECT id, price, promotion_info, change_type, collected_at FROM price_history WHERE goods_id = 7 ORDER BY id DESC LIMIT 5")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]}, Price: {r[1]}, Info: {r[2]}, Type: {r[3]}, Time: {r[4]}")

conn.close()
