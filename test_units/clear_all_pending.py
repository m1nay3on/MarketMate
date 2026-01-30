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

# Delete all pending orders
cursor.execute("DELETE FROM orders WHERE status = 'pending'")
deleted_orders = cursor.rowcount

# Also delete orphaned payments and shipping records
cursor.execute("DELETE FROM payments WHERE order_id NOT IN (SELECT id FROM orders)")
deleted_payments = cursor.rowcount

cursor.execute("DELETE FROM shipping WHERE order_id NOT IN (SELECT id FROM orders)")
deleted_shipping = cursor.rowcount

conn.commit()

print(f'✅ Deleted {deleted_orders} pending orders')
print(f'✅ Deleted {deleted_payments} orphaned payments')
print(f'✅ Deleted {deleted_shipping} orphaned shipping records')

# Show remaining orders
cursor.execute('SELECT id, order_id, customer_id, item_id, status FROM orders ORDER BY id DESC')
rows = cursor.fetchall()

print(f'\n📦 Remaining Orders: {len(rows)}')
for r in rows:
    print(f'   ID:{r[0]} | OrderID:{r[1]} | CustID:{r[2]} | ItemID:{r[3]} | Status:{r[4]}')

conn.close()
