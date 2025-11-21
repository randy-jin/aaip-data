#!/bin/bash

# Fix Server Dependencies for AAIP Data Scrapers
# Run this on the test server to fix missing dependencies

echo "======================================"
echo "Fixing AAIP Scraper Dependencies"
echo "======================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
echo ""
echo "Python version:"
python3 --version

# Check if venv exists, if not create one
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install all requirements
echo ""
echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt

# Verify critical packages
echo ""
echo "======================================"
echo "Verifying Critical Packages"
echo "======================================"

packages=("beautifulsoup4" "requests" "psycopg2-binary" "python-dotenv" "lxml" "pdfplumber")

for package in "${packages[@]}"; do
    if python3 -c "import ${package//-/_}" 2>/dev/null; then
        echo "✓ $package - OK"
    else
        echo "✗ $package - MISSING"
    fi
done

# Check for bs4 specifically
if python3 -c "import bs4" 2>/dev/null; then
    echo "✓ bs4 (BeautifulSoup) - OK"
else
    echo "✗ bs4 (BeautifulSoup) - MISSING"
fi

# Check .env file
echo ""
echo "======================================"
echo "Checking Environment Configuration"
echo "======================================"

if [ -f ".env" ]; then
    echo "✓ .env file exists"
    echo ""
    echo "Database configuration:"
    grep -E "^(DATABASE_URL|DB_HOST|DB_PORT|DB_NAME|DB_USER)=" .env | sed 's/DB_PASSWORD=.*/DB_PASSWORD=***HIDDEN***/'
else
    echo "✗ .env file NOT found"
    echo ""
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠ Please edit .env file with your database credentials"
    else
        echo "Creating default .env file..."
        cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname
# OR use individual parameters:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aaip_data
DB_USER=your_user
DB_PASSWORD=your_password
EOF
        echo "⚠ Please edit .env file with your database credentials"
    fi
fi

echo ""
echo "======================================"
echo "Setup Complete"
echo "======================================"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source $SCRIPT_DIR/venv/bin/activate"
echo ""
echo "To test the scrapers, run:"
echo "  python3 test_collectors.py"
echo ""
