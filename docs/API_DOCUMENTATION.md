# MarketMate API Documentation

## Base URL
```
http://127.0.0.1:8002
```

## Authentication

All endpoints (except signup/login) require a JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

---

## Auth Endpoints

### Register User
```http
POST /api/auth/signup
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

### Login (JSON)
```http
POST /api/auth/login/json
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}

Response:
{
  "id": 1,
  "username": "admin",
  "email": "admin@marketmate.com",
  "shop_name": "MarketMate Store",
  "created_at": "2026-01-22T10:00:00"
}
```

---

## Dashboard Endpoints

### Get Dashboard Stats
```http
GET /api/dashboard/stats
Authorization: Bearer {token}

Response:
{
  "total_orders": 150,
  "active_orders": 25,
  "to_ship": 10,
  "total_revenue": 125000.50,
  "total_customers": 75,
  "total_items": 30
}
```

### Get Top Selling Items
```http
GET /api/dashboard/top-items?limit=5
Authorization: Bearer {token}

Response:
[
  {"name": "iPhone 17 Pro Max", "count": 45},
  {"name": "Samsung Galaxy S25", "count": 32}
]
```

### Get Recent Reviews
```http
GET /api/dashboard/recent-reviews?limit=5
Authorization: Bearer {token}

Response:
[
  {
    "item_name": "iPhone 17 Pro Max",
    "customer_name": "John Doe",
    "rating": 4.9,
    "comment": "Excellent product!",
    "created_at": "2026-01-22T10:00:00"
  }
]
```

### Get Average Rating
```http
GET /api/dashboard/average-rating
Authorization: Bearer {token}

Response:
{
  "average_rating": 4.5,
  "review_count": 25
}
```

---

## Customer Endpoints

### List All Customers
```http
GET /api/customers/
Authorization: Bearer {token}
```

### Get Customer by ID
```http
GET /api/customers/{id}
Authorization: Bearer {token}
```

### Create Customer
```http
POST /api/customers/
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "CUST001",
  "name": "John Doe",
  "email": "john@example.com",
  "address": "123 Main St, City",
  "phone": "555-0100",
  "status": "active"
}
```

### Update Customer
```http
PUT /api/customers/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "John Updated",
  "status": "inactive"
}
```

### Delete Customer
```http
DELETE /api/customers/{id}
Authorization: Bearer {token}
```

---

## Order Endpoints

### List All Orders
```http
GET /api/orders/
Authorization: Bearer {token}
```

### Get Order by ID
```http
GET /api/orders/{id}
Authorization: Bearer {token}
```

### Create Order
```http
POST /api/orders/
Authorization: Bearer {token}
Content-Type: application/json

{
  "order_id": "ORD001",
  "customer_id": 1,
  "item_id": 1,
  "payment_method": "GCash",
  "status": "new"
}
```

### Update Order
```http
PUT /api/orders/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "preparing"
}
```

### Delete Order
```http
DELETE /api/orders/{id}
Authorization: Bearer {token}
```

---

## Item Endpoints

### List All Items
```http
GET /api/items/
Authorization: Bearer {token}
```

### Get Item by ID
```http
GET /api/items/{id}
Authorization: Bearer {token}
```

### Create Item
```http
POST /api/items/
Authorization: Bearer {token}
Content-Type: application/json

{
  "item_id": "ITM001",
  "name": "iPhone 17 Pro Max",
  "description": "Latest flagship phone",
  "price": 78000.00,
  "image_url": "../images/iphonee.jpg",
  "variants": ["Cosmic Black", "Cosmic White"]
}
```

### Update Item
```http
PUT /api/items/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "iPhone 17 Pro Max Updated",
  "price": 75000.00,
  "variants": ["Cosmic Black", "Cosmic White", "Cosmic Orange"]
}
```

### Delete Item
```http
DELETE /api/items/{id}
Authorization: Bearer {token}
```

---

## Shipping Endpoints

### List All Shipments
```http
GET /api/shipping/
Authorization: Bearer {token}
```

### Get Shipment by ID
```http
GET /api/shipping/{id}
Authorization: Bearer {token}
```

### Create Shipment
```http
POST /api/shipping/
Authorization: Bearer {token}
Content-Type: application/json

{
  "shipping_id": "SHP001",
  "order_id": 1,
  "courier": "LBC",
  "address": "123 Main St",
  "status": "preparing"
}
```

### Update Shipment
```http
PUT /api/shipping/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "shipped"
}
```

### Delete Shipment
```http
DELETE /api/shipping/{id}
Authorization: Bearer {token}
```

---

## Payment Endpoints

### List All Payments
```http
GET /api/payments/
Authorization: Bearer {token}
```

### Get Payment by ID
```http
GET /api/payments/{id}
Authorization: Bearer {token}
```

### Create Payment
```http
POST /api/payments/
Authorization: Bearer {token}
Content-Type: application/json

{
  "payment_id": "PAY001",
  "order_id": 1,
  "amount": 78000.00,
  "payment_method": "GCash",
  "status": "pending"
}
```

### Update Payment
```http
PUT /api/payments/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "paid"
}
```

### Delete Payment
```http
DELETE /api/payments/{id}
Authorization: Bearer {token}
```

---

## Review Endpoints

### List All Reviews
```http
GET /api/reviews/
Authorization: Bearer {token}
```

### Get Reviews by Item
```http
GET /api/reviews/item/{item_id}
Authorization: Bearer {token}
```

### Get Review by ID
```http
GET /api/reviews/{id}
Authorization: Bearer {token}
```

### Create Review
```http
POST /api/reviews/
Authorization: Bearer {token}
Content-Type: application/json

{
  "item_id": 1,
  "customer_name": "John Doe",
  "rating": 4.5,
  "comment": "Great product!"
}
```

### Delete Review
```http
DELETE /api/reviews/{id}
Authorization: Bearer {token}
```

---

## Reward Endpoints

### List All Rewards
```http
GET /api/rewards/
Authorization: Bearer {token}
```

### Get Reward by ID
```http
GET /api/rewards/{id}
Authorization: Bearer {token}
```

### Validate Reward Code
```http
GET /api/rewards/validate/{code}
Authorization: Bearer {token}
```

### Create Reward
```http
POST /api/rewards/
Authorization: Bearer {token}
Content-Type: application/json

{
  "reward_id": "RWD001",
  "type": "Voucher",
  "code": "SAVE20",
  "discount": 20.00,
  "validity_period": "2026-12-31",
  "status": "active"
}
```

### Update Reward
```http
PUT /api/rewards/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "inactive"
}
```

### Delete Reward
```http
DELETE /api/rewards/{id}
Authorization: Bearer {token}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Testing with PowerShell

```powershell
# Login
$body = '{"username":"admin","password":"admin123"}'
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8002/api/auth/login/json" -Method POST -Body $body -ContentType "application/json"
$token = $response.access_token

# Get Dashboard Stats
$headers = @{"Authorization"="Bearer $token"}
Invoke-RestMethod -Uri "http://127.0.0.1:8002/api/dashboard/stats" -Headers $headers

# Create Customer
$customer = '{"customer_id":"CUST001","name":"Test","email":"test@test.com","address":"123 St","phone":"555-0001"}'
Invoke-RestMethod -Uri "http://127.0.0.1:8002/api/customers/" -Method POST -Headers $headers -Body $customer -ContentType "application/json"
```

---

## Interactive Documentation

For interactive API testing, visit:
- **Swagger UI**: http://127.0.0.1:8002/api/docs
- **ReDoc**: http://127.0.0.1:8002/api/redoc
