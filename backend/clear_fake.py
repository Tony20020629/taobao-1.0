import sqlite3

db_path = r'e:\NewProject\taobao\backend\taobao_monitor.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("UPDATE goods SET current_price = 0, avg_price = 0, min_price = 0, max_price = 0 WHERE id = 7")
cursor.execute("DELETE FROM price_history WHERE goods_id = 7")
conn.commit()

cursor.execute("SELECT id, name, current_price FROM goods WHERE id = 7")
row = cursor.fetchone()
print(f"Cleared! ID: {row[0]}, Name: {row[1]}, Price: {row[2]}")

conn.close()
print("Database cleared. Ready for real price collection.")
