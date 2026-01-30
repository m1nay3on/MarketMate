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

print('\n===== PROBLEM ANALYSIS =====\n')

print('CUSTOMERS:')
cursor.execute('SELECT id, customer_id, email, user_id FROM customers')
for r in cursor.fetchall():
    print(f'  ID:{r[0]} | Email:{r[2]} | UserID:{r[3]}')

print('\nORDERS:')
cursor.execute('SELECT id, order_id, customer_id, status FROM orders')
for r in cursor.fetchall():
    print(f'  ID:{r[0]} | OrderID:{r[1]} | CustomerID:{r[2]} | Status:{r[3]}')

print('\n===== THE ISSUE =====')
print('User matthew2 (ID=3, Email=botemt@students.national-u.edu.ph) is logged in')
print('The query finds Customer ID=1 (Email=botemt@students.national-u.edu.ph)')
print('But all the pending orders belong to Customer ID=2')
print('So Customer ID=1 has 0 orders, while Customer ID=2 has all the orders!')

print('\n===== SOLUTION =====')
print('We need to either:')
print('1. Update all orders from customer_id=2 to customer_id=1, OR')
print('2. Delete the duplicate customer record')

print('\nWhich customer should we keep?')
cursor.execute('SELECT id, customer_id, email, name, user_id, created_at FROM customers ORDER BY id')
customers = cursor.fetchall()
for c in customers:
    print(f'  Customer {c[0]}: {c[1]} | {c[2]} | UserID={c[4]} | Created={c[5]}')

conn.close()
