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

print('\n===== FIXING CUSTOMER/ORDER MISMATCH =====\n')

# Step 1: Move all orders from customer_id=2 to customer_id=1
print('Step 1: Migrating orders from Customer 2 to Customer 1...')
cursor.execute('UPDATE orders SET customer_id = 1 WHERE customer_id = 2')
updated_orders = cursor.rowcount
print(f'✅ Migrated {updated_orders} orders')

# Step 2: Delete the duplicate customer record (ID=2)
print('\nStep 2: Deleting duplicate customer record...')
cursor.execute('DELETE FROM customers WHERE id = 2')
deleted_customers = cursor.rowcount
print(f'✅ Deleted {deleted_customers} duplicate customer record')

conn.commit()

# Verify
print('\n===== VERIFICATION =====\n')

print('CUSTOMERS:')
cursor.execute('SELECT id, customer_id, email, user_id FROM customers')
for r in cursor.fetchall():
    print(f'  ID:{r[0]} | CustomerID:{r[1]} | Email:{r[2]} | UserID:{r[3]}')

print('\nORDERS (showing customer_id):')
cursor.execute('SELECT id, order_id, customer_id, status FROM orders')
for r in cursor.fetchall():
    print(f'  ID:{r[0]} | OrderID:{r[1]} | CustomerID:{r[2]} | Status:{r[3]}')

print('\n✅ FIX COMPLETE!')
print('Now user matthew2 (Customer ID=1) will see all their orders!')

conn.close()
