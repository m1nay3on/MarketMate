@echo off
echo Importing MarketMate database schema...
echo.
echo Please enter your MySQL root password when prompted.
echo.

"C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysql.exe" -u root -p < backend\database\schema.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Database schema imported successfully!
    echo ✓ Database 'marketmate' created
    echo ✓ Default admin user created (username: admin, password: admin123)
) else (
    echo.
    echo ✗ Error importing database schema
    echo Please check your MySQL password and try again
)

echo.
pause
