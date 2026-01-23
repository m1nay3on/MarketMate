# MarketMate Quick Start Guide

## 🚀 Quick Start (One Command!)

### Prerequisites
- Python 3.9+ with virtual environment set up
- MySQL running with `marketmate_db` database created
- Dependencies installed (`pip install -r requirements.txt`)

### Start Everything
```bash
# Activate virtual environment first
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Mac/Linux

# Start both backend and frontend servers
python start.py
```

This will:
- ✅ Check database connection
- ✅ Start Backend API on http://127.0.0.1:8002
- ✅ Start Frontend on http://127.0.0.1:8080
- ✅ Open API docs at http://127.0.0.1:8002/api/docs

### Stop Everything
```bash
python stop.py
```

### Login
- **URL**: http://127.0.0.1:8080/html/Sign-In.html
- **Username**: `admin`
- **Password**: `admin123`

---

## 📋 First-Time Setup (5 minutes)

### Step 1: Database Setup
```bash
# Start MySQL and create database
mysql -u root -p
```
```sql
CREATE DATABASE marketmate_db;
USE marketmate_db;
SOURCE backend/database/schema.sql;
exit;
```

### Step 2: Configure Environment
```bash
# Edit backend/.env with your MySQL credentials
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=marketmate_db
```

### Step 3: Python Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Start Servers
```bash
python start.py
```

### Step 5: Login
Open http://127.0.0.1:8080/html/Sign-In.html
- Username: `admin`
- Password: `admin123`

---

## 📋 Common Commands

| Command | Description |
|---------|-------------|
| `python start.py` | Start all servers (backend + frontend) |
| `python stop.py` | Stop all running servers |

### View API Documentation
Open browser: http://127.0.0.1:8002/api/docs

### Test API with PowerShell
```powershell
# Login and get token
$body = '{"username":"admin","password":"admin123"}'
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8002/api/auth/login/json" -Method POST -Body $body -ContentType "application/json"
$token = $response.access_token

# Get dashboard stats
$headers = @{"Authorization"="Bearer $token"}
Invoke-RestMethod -Uri "http://127.0.0.1:8002/api/dashboard/stats" -Headers $headers
```

---

## 🔧 Troubleshooting

### MySQL Connection Error
- Check MySQL is running
- Verify credentials in `backend/.env`
- Ensure database exists: `SHOW DATABASES;`

### Port Already in Use
```bash
# Stop any running servers
python stop.py
```

### Module Not Found Error
- Activate virtual environment: `.venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

### CORS Error in Browser
- Ensure backend is running on port 8002
- Use http://127.0.0.1:8080 for frontend (not localhost)
- Clear browser cache

### Token Expired
- Login again to get new token
- Tokens expire after 24 hours

---

## 🎯 Key URLs

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:8080/html/home.html |
| Backend API | http://127.0.0.1:8002 |
| API Docs (Swagger) | http://127.0.0.1:8002/api/docs |
| ReDoc | http://127.0.0.1:8002/api/redoc |

---

**Need Help?** Check the main README.md or open an issue on GitHub.
