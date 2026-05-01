import sqlite3

db_path = r'e:\NewProject\taobao\backend\taobao_monitor.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('SELECT * FROM goods')
rows = c.fetchall()
print('All goods in database:')
for row in rows:
    print(row)

c.execute('SELECT * FROM price_history')
rows = c.fetchall()
print('\nAll price history:')
for row in rows:
    print(row)

conn.close()
