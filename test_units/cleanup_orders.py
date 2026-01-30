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

# Keep only the most recent 2 pending orders (for testing)
# Delete all other pending orders for customer_id = 2
cursor.execute('''
    DELETE FROM orders 
    WHERE customer_id = 2 
    AND status = 'pending' 
    AND id NOT IN (
        SELECT * FROM (
            SELECT id FROM orders 
            WHERE customer_id = 2 AND status = 'pending'
            ORDER BY id DESC 
            LIMIT 2
        ) AS keep_ids
    )
''')

deleted = cursor.rowcount
conn.commit()

print(f'Deleted {deleted} duplicate pending orders')

# Show remaining orders
cursor.execute('SELECT id, order_id, customer_id, item_id, status FROM orders ORDER BY id DESC')
rows = cursor.fetchall()

print(f'\nRemaining Orders: {len(rows)}')
for r in rows:
    print(f'ID:{r[0]} | OrderID:{r[1]} | CustID:{r[2]} | ItemID:{r[3]} | Status:{r[4]}')

conn.close()
