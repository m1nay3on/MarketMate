# 🛒 MarketMate

MarketMate is a full-stack **e-commerce management platform** that allows shop owners to manage their online business. The platform provides dashboards for tracking orders, customers, inventory, payments, shipping, reviews, and rewards - all with a modern, responsive user interface.

This project showcases full-stack web development with a clean separation between frontend (HTML/CSS/JavaScript) and backend (Python FastAPI + MySQL).

---

## 🚀 Features

### Frontend Features
- 📊 **Dashboard** - Real-time statistics and analytics
- 📦 **Order Management** - Track and update order statuses
- 👥 **Customer Management** - Manage customer information
- 📦 **Inventory** - Add, edit, and delete items with variants
- 🚚 **Shipping Tracker** - Monitor shipping status
- 💳 **Payment Processing** - Track payment statuses
- ⭐ **Review System** - View and manage customer reviews
- 🎁 **Rewards & Vouchers** - Create and manage discount codes
- 🔐 **Authentication** - Secure JWT-based login system

### Backend Features
- RESTful API with FastAPI
- JWT token authentication
- MySQL database with SQLAlchemy ORM
- CRUD operations for all entities
- Automatic API documentation (Swagger UI)
- CORS support for frontend integration
- Password hashing with bcrypt
- Input validation with Pydantic

---

## 🛠️ Tech Stack

**Frontend**
- HTML5  
- CSS3
- JavaScript (ES6+)
- Font Awesome Icons

**Backend**
- Python 3.13
- FastAPI
- SQLAlchemy ORM
- PyMySQL
- python-jose (JWT)
- passlib (Password Hashing)
- Pydantic (Validation)

**Database**
- MySQL 8.0+

---

## 📂 Project Structure

```
MarketMate/
├── backend/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # Database connection & session management
│   │   └── schema.sql              # Database schema with all tables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   └── schemas.py              # Pydantic schemas for validation
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── dashboard.py            # Dashboard statistics
│   │   ├── customers.py            # Customer CRUD
│   │   ├── orders.py               # Order CRUD
│   │   ├── items.py                # Item CRUD
│   │   ├── shipping.py             # Shipping CRUD
│   │   ├── payments.py             # Payment CRUD
│   │   ├── reviews.py              # Review CRUD
│   │   └── rewards.py              # Reward CRUD
│   ├── utils/
│   │   ├── __init__.py
│   │   └── auth_utils.py           # JWT & password utilities
│   ├── __init__.py
│   ├── config.py                   # Configuration settings
│   ├── main.py                     # FastAPI application entry point
│   └── .env.example                # Environment variables template
├── css/
│   ├── customer.css
│   ├── home.css
│   ├── items.css
│   ├── order.css
│   ├── payments.css
│   ├── reviews.css
│   ├── rewards.css
│   ├── shipping.css
│   ├── signin.css
│   └── SignUp.css
├── html/
│   ├── customer.html               # Customer management page
│   ├── home.html                   # Dashboard
│   ├── items.html                  # Inventory management
│   ├── order.html                  # Order tracking
│   ├── payments.html               # Payment management
│   ├── reviews.html                # Customer reviews
│   ├── rewards.html                # Rewards & vouchers
│   ├── shipping.html               # Shipping tracker
│   ├── Sign-In.html                # Login page
│   └── Sign-Up.html                # Registration page
├── js/
│   ├── api.js                      # API client & token management
│   ├── customers.js                # Customer page logic
│   ├── items.js                    # Items page logic (edit, variants)
│   ├── shipping.js                 # Shipping page logic
│   ├── payments.js                 # Payments page logic (dynamic)
│   ├── reviews.js                  # Reviews page logic (dynamic)
│   └── rewards.js                  # Rewards page logic
├── images/                         # Static images
├── static/                         # Backend static files
│   └── uploads/                    # Uploaded images
├── docs/                           # Documentation
│   ├── QUICKSTART.md
│   ├── FOLDER_STRUCTURE.md
│   ├── IMPLEMENTATION_COMPLETE.md
│   └── API_DOCUMENTATION.md
├── .venv/                          # Python virtual environment
├── start.py                        # ✅ Start all servers
├── stop.py                         # ✅ Stop all servers
├── requirements.txt                # Python dependencies
├── seed_database.py                # Database seeding
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Start All Servers (One Command!)
```bash
# Activate virtual environment first
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Mac/Linux

# Start everything
python start.py
```

This starts:
- **Backend API** on http://127.0.0.1:8002
- **Frontend** on http://127.0.0.1:8080
- **API Docs** at http://127.0.0.1:8002/api/docs

### Stop All Servers
```bash
python stop.py
```

### Login
- **URL**: http://127.0.0.1:8080/html/Sign-In.html
- **Username**: `admin`
- **Password**: `admin123`

---

## 🔧 First-Time Setup

### Prerequisites
- Python 3.9 or higher
- MySQL 8.0 or higher
- Modern web browser

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/MarketMate.git
cd MarketMate
```

### 2. Set Up MySQL Database
```bash
mysql -u root -p
```
```sql
CREATE DATABASE marketmate_db;
USE marketmate_db;
SOURCE backend/database/schema.sql;
exit;
```

### 3. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Edit backend/.env with your database credentials
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=marketmate_db
```

### 5. Start the Servers
```bash
python start.py
```

This will start:
- **Backend API**: http://127.0.0.1:8002
- **API Docs (Swagger)**: http://127.0.0.1:8002/api/docs
- **Frontend**: http://127.0.0.1:8080

### 6. Stop the Servers
```bash
python stop.py
```

---

## 🎯 Usage

### Default Admin Account
After running the database schema, a default admin account is created:
- **Username**: `admin`
- **Password**: `admin123`

### Key URLs
| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:8080/html/home.html |
| Backend API | http://127.0.0.1:8002 |
| API Docs | http://127.0.0.1:8002/api/docs |

### API Endpoints

#### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login/json` - Login (JSON)
- `GET /api/auth/me` - Get current user

#### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/top-items` - Get top selling items
- `GET /api/dashboard/recent-reviews` - Get recent reviews
- `GET /api/dashboard/average-rating` - Get average rating

#### Customers
- `GET /api/customers/` - List all customers
- `POST /api/customers/` - Create customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

#### Orders
- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order

#### Items
- `GET /api/items/` - List all items
- `POST /api/items/` - Create item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item

#### (Similar patterns for shipping, payments, reviews, rewards)

Full API documentation available at `/api/docs` when server is running.

---

## 🔐 Security Features

- JWT token-based authentication
- Bcrypt password hashing
- CORS configuration for frontend
- SQL injection protection via SQLAlchemy ORM
- Input validation with Pydantic
- HTTP-only authentication (can be configured)

---

## 🚧 Future Enhancements

- [ ] Image upload functionality for items
- [ ] Email notifications
- [ ] Advanced analytics and reports
- [ ] Export data to CSV/PDF
- [ ] Multi-shop support
- [ ] Real-time notifications with WebSockets
- [ ] Payment gateway integration
- [ ] Mobile responsive improvements
- [ ] Dark mode

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License.

---

## 👨‍💻 Developer

Developed as a full-stack e-commerce management solution showcasing modern web development practices.

---

## 📧 Support

For issues or questions, please open an issue on GitHub.

