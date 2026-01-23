# 📁 MarketMate Folder Structure

```
MarketMate/
│
├── 📂 backend/                          # Python FastAPI Backend
│   ├── 📂 database/
│   │   ├── __init__.py
│   │   ├── connection.py                # DB connection & session
│   │   └── schema.sql                   # MySQL database schema
│   │
│   ├── 📂 models/
│   │   ├── __init__.py
│   │   ├── models.py                    # SQLAlchemy ORM models
│   │   └── schemas.py                   # Pydantic validation schemas
│   │
│   ├── 📂 routes/                       # API Endpoints
│   │   ├── __init__.py
│   │   ├── auth.py                      # POST /api/auth/signup, /login
│   │   ├── dashboard.py                 # GET /api/dashboard/stats
│   │   ├── customers.py                 # CRUD /api/customers/
│   │   ├── orders.py                    # CRUD /api/orders/
│   │   ├── items.py                     # CRUD /api/items/
│   │   ├── shipping.py                  # CRUD /api/shipping/
│   │   ├── payments.py                  # CRUD /api/payments/
│   │   ├── reviews.py                   # CRUD /api/reviews/
│   │   └── rewards.py                   # CRUD /api/rewards/
│   │
│   ├── 📂 utils/
│   │   ├── __init__.py
│   │   └── auth_utils.py                # JWT & password hashing
│   │
│   ├── __init__.py
│   ├── config.py                        # Settings & configuration
│   └── main.py                          # FastAPI application
│
├── 📂 html/                             # Frontend HTML Pages
│   ├── Sign-In.html                     # Login page
│   ├── Sign-Up.html                     # Registration
│   ├── home.html                        # Dashboard (dynamic)
│   ├── customer.html                    # Customers
│   ├── order.html                       # Orders
│   ├── items.html                       # Items (with edit & variants)
│   ├── shipping.html                    # Shipping
│   ├── payments.html                    # Payments (dynamic)
│   ├── reviews.html                     # Reviews (dynamic)
│   └── rewards.html                     # Rewards
│
├── 📂 css/                              # Stylesheets
│   ├── home.css
│   ├── customer.css
│   ├── order.css
│   ├── items.css
│   ├── shipping.css
│   ├── payments.css
│   ├── reviews.css
│   ├── rewards.css
│   ├── signin.css
│   └── SignUp.css
│
├── 📂 js/                               # JavaScript Modules
│   ├── api.js                           # API client & JWT token mgmt
│   ├── customers.js                     # Customer page logic
│   ├── items.js                         # Items (edit, delete, variants)
│   ├── shipping.js                      # Shipping tracker
│   ├── payments.js                      # Payment tracking (dynamic)
│   ├── reviews.js                       # Review display (dynamic)
│   └── rewards.js                       # Rewards management
│
├── 📂 images/                           # Static images
│   ├── MarketMate.png                   # Logo
│   ├── ppft.png                         # Profile picture
│   └── iphonee.jpg                      # Product image
│
├── 📂 static/                           # Backend static files
│   └── 📂 uploads/                      # Uploaded images
│
├── 📂 docs/                             # Documentation
│   ├── QUICKSTART.md                    # Quick start guide
│   ├── FOLDER_STRUCTURE.md              # This file
│   ├── IMPLEMENTATION_COMPLETE.md       # Implementation summary
│   └── API_DOCUMENTATION.md             # API reference
│
├── 📂 .venv/                            # Python virtual environment
│
├── 📄 start.py                          # ✅ Start all servers
├── 📄 stop.py                           # ✅ Stop all servers
├── 📄 requirements.txt                  # Python dependencies
├── 📄 seed_database.py                  # Database seeding script
├── 📄 import_database.py                # Database import script
├── 📄 import_database.bat               # Windows batch import
├── 📄 setup.bat                         # Windows setup script
├── 📄 setup.sh                          # Mac/Linux setup script
├── 📄 .gitignore                        # Git ignore rules
└── 📄 README.md                         # Main documentation
```

## 📊 Statistics

### Backend
- **Python Files**: 15+
- **API Routes**: 9 route files
- **Models**: 9 database models
- **Endpoints**: 45+ API endpoints

### Frontend
- **HTML Pages**: 10 pages
- **CSS Files**: 10 stylesheets
- **JS Modules**: 7 JavaScript files

### Scripts
- **start.py** - Unified server startup
- **stop.py** - Stop all servers
- **seed_database.py** - Sample data

## 🔑 Key Files

### Server Management
| File | Purpose |
|------|---------|
| `start.py` | Start backend (8002) + frontend (8080) |
| `stop.py` | Kill all server processes |

### Configuration
| File | Purpose |
|------|---------|
| `backend/.env` | Database credentials |
| `backend/config.py` | App settings |
| `js/api.js` | API base URL (8002) |

### Entry Points
| Entry Point | URL |
|-------------|-----|
| Frontend | http://127.0.0.1:8080/html/Sign-In.html |
| Backend API | http://127.0.0.1:8002 |
| API Docs | http://127.0.0.1:8002/api/docs |

## 🎯 File Purposes

### Backend Files
- `main.py` - FastAPI application entry
- `config.py` - Settings, database URL, JWT secret
- `connection.py` - SQLAlchemy database setup
- `models.py` - ORM models (9 tables)
- `schemas.py` - Pydantic validation
- `auth_utils.py` - JWT & password utilities
- Route files - CRUD operations per entity

### Frontend Files
- `api.js` - Centralized API client (all pages use this)
- Page-specific JS files - CRUD logic
- Each HTML page - Complete dashboard view
- Each CSS file - Page styling

## 🚀 Quick Commands

```bash
# Start everything
python start.py

# Stop everything  
python stop.py

# View API docs
# http://127.0.0.1:8002/api/docs
```
