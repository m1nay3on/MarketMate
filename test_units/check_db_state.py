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

print("\n===== CURRENT DATABASE STATE =====\n")

# Check customers
cursor.execute("SELECT id, customer_id, name, email, user_id FROM customers")
customers = cursor.fetchall()
print(f"CUSTOMERS ({len(customers)}):")
for c in customers:
    print(f"  ID:{c[0]} | CustID:{c[1]} | Name:{c[2]} | Email:{c[3]} | UserID:{c[4]}")

# Check items
cursor.execute("SELECT id, item_id, name, price, user_id FROM items LIMIT 5")
items = cursor.fetchall()
print(f"\nITEMS ({len(items)}):")
for i in items:
    print(f"  ID:{i[0]} | ItemID:{i[1]} | Name:{i[2]} | Price:{i[3]} | UserID:{i[4]}")

# Check orders
cursor.execute("SELECT id, order_id, customer_id, item_id, status, user_id FROM orders")
orders = cursor.fetchall()
print(f"\nORDERS ({len(orders)}):")
for o in orders:
    print(f"  ID:{o[0]} | OrderID:{o[1]} | CustID:{o[2]} | ItemID:{o[3]} | Status:{o[4]} | UserID:{o[5]}")

# Check payments
cursor.execute("SELECT id, payment_id, order_id, amount, status FROM payments")
payments = cursor.fetchall()
print(f"\nPAYMENTS ({len(payments)}):")
for p in payments:
    print(f"  ID:{p[0]} | PayID:{p[1]} | OrderID:{p[2]} | Amount:{p[3]} | Status:{p[4]}")

# Check shipping
cursor.execute("SELECT id, shipping_id, order_id, status FROM shipping")
shipping = cursor.fetchall()
print(f"\nSHIPPING ({len(shipping)}):")
for s in shipping:
    print(f"  ID:{s[0]} | ShipID:{s[1]} | OrderID:{s[2]} | Status:{s[3]}")

# Check users
cursor.execute("SELECT id, username, email, role FROM users")
users = cursor.fetchall()
print(f"\nUSERS ({len(users)}):")
for u in users:
    print(f"  ID:{u[0]} | Username:{u[1]} | Email:{u[2]} | Role:{u[3]}")

print("\n" + "="*50)

conn.close()
