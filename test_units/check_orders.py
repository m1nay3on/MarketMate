import pymysql
from backend.config import settings

conn = pymysql.connect(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME
)

cursor = conn.cursor()

# Check orders
cursor.execute('SELECT id, order_id, customer_id, item_id, status FROM orders ORDER BY id DESC LIMIT 20')
rows = cursor.fetchall()

print(f'\n===== ORDERS (Total: {len(rows)}) =====')
for r in rows:
    print(f'ID:{r[0]} | OrderID:{r[1]} | CustID:{r[2]} | ItemID:{r[3]} | Status:{r[4]}')

# Check for duplicates by order_id
cursor.execute('SELECT order_id, COUNT(*) as cnt FROM orders GROUP BY order_id HAVING cnt > 1')
dupes = cursor.fetchall()

if dupes:
    print(f'\n===== DUPLICATE ORDER IDs =====')
    for d in dupes:
        print(f'OrderID: {d[0]} appears {d[1]} times')
        
# Check customers
cursor.execute('SELECT id, customer_id, name, email FROM customers ORDER BY id DESC LIMIT 10')
customers = cursor.fetchall()

print(f'\n===== CUSTOMERS (Total: {len(customers)}) =====')
for c in customers:
    print(f'ID:{c[0]} | CustID:{c[1]} | Name:{c[2]} | Email:{c[3]}')

conn.close()
