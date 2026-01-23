#!/bin/bash
# MarketMate Backend Setup Script for Mac/Linux

echo "========================================="
echo "  MarketMate Backend Setup"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please activate the virtual environment first:"
    echo "  source .venv/bin/activate"
    exit 1
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Set up MySQL database:"
echo "   mysql -u root -p < backend/database/schema.sql"
echo ""
echo "2. Configure environment:"
echo "   cp backend/.env.example backend/.env"
echo "   Edit backend/.env with your database credentials"
echo ""
echo "3. Start the backend:"
echo "   uvicorn backend.main:app --reload"
echo ""
echo "4. Open frontend:"
echo "   html/Sign-In.html"
echo ""
echo "Default login: admin / admin123"
echo ""
