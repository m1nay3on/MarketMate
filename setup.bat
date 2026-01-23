@echo off
REM MarketMate Backend Setup Script for Windows

echo =========================================
echo   MarketMate Backend Setup
echo =========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please activate the virtual environment first:
    echo   .venv\Scripts\activate
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo =========================================
echo   Setup Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Set up MySQL database:
echo    mysql -u root -p ^< backend/database/schema.sql
echo.
echo 2. Configure environment:
echo    Copy backend/.env.example to backend/.env
echo    Edit backend/.env with your database credentials
echo.
echo 3. Start the backend:
echo    uvicorn backend.main:app --reload
echo.
echo 4. Open frontend:
echo    html/Sign-In.html
echo.
echo Default login: admin / admin123
echo.
pause
