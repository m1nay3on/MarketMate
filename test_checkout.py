import requests
import json

# Test the checkout endpoint
API_URL = "http://127.0.0.1:8003"

# First, login to get token
print("1. Logging in...")
login_response = requests.post(
    f"{API_URL}/api/auth/login/json",
    json={"username": "matthew2", "password": "matthew"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Token obtained: {token[:20]}...")

# Get current user
print("\n2. Getting current user...")
user_response = requests.get(
    f"{API_URL}/api/auth/me",
    headers={"Authorization": f"Bearer {token}"}
)
user = user_response.json()
print(f"✅ Logged in as: {user['username']} ({user['email']})")

# Try checkout
print("\n3. Testing checkout...")
checkout_data = {
    "item_id": 6,
    "quantity": 1,
    "payment_method": "COD",
    "shipping_method": "J&T Express"
}

checkout_response = requests.post(
    f"{API_URL}/api/orders/checkout",
    json=checkout_data,
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status Code: {checkout_response.status_code}")
if checkout_response.status_code == 201:
    order = checkout_response.json()
    print(f"✅ Order created: {order['order_id']}")
    print(f"   Order ID: {order['id']}")
    print(f"   Status: {order['status']}")
else:
    print(f"❌ Checkout failed:")
    print(checkout_response.text)

# Get my orders
print("\n4. Getting my orders...")
orders_response = requests.get(
    f"{API_URL}/api/orders/my-orders",
    headers={"Authorization": f"Bearer {token}"}
)

if orders_response.status_code == 200:
    orders = orders_response.json()
    print(f"✅ Found {len(orders)} orders:")
    for order in orders:
        print(f"   - {order['order_id']}: {order['item_name']} (Status: {order['status']})")
else:
    print(f"❌ Failed to get orders: {orders_response.status_code}")
    print(orders_response.text)
