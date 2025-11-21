#!/bin/bash
###############################################################################
# Quick Integration Script - Activates the Draw Visualization Feature
# Run this on the server to activate the new functionality
###############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Activating AAIP Draw Visualization Feature${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Change to project directory
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)

echo -e "${GREEN}[1/5]${NC} Updating database..."
sudo -u randy psql aaip_data_trend_dev_db < setup_db_draws.sql
echo -e "${GREEN}✓${NC} Database updated"
echo

echo -e "${GREEN}[2/5]${NC} Updating backend..."
cd backend
cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)
cp main_draws.py main.py
echo -e "${GREEN}✓${NC} Backend files updated"
sudo systemctl restart aaip-backend-test
echo -e "${GREEN}✓${NC} Backend restarted"
echo

echo -e "${GREEN}[3/5]${NC} Updating frontend..."
cd ../frontend
cp src/App.jsx src/App.jsx.backup.$(date +%Y%m%d_%H%M%S)
cp src/App_with_draws.jsx src/App.jsx
echo -e "${GREEN}✓${NC} Frontend files updated"
echo "Building frontend..."
npm run build
echo -e "${GREEN}✓${NC} Frontend built"
sudo cp -r dist/* /var/www/html/aaip-test/
echo -e "${GREEN}✓${NC} Frontend deployed"
echo

echo -e "${GREEN}[4/5]${NC} Updating scraper..."
cd ../scraper
python3 scraper_draws.py
echo -e "${GREEN}✓${NC} Scraper tested and data collected"
echo

echo -e "${GREEN}[5/5]${NC} Verification..."
sleep 2
if curl -sf http://localhost:8000/api/draws/streams > /dev/null; then
    echo -e "${GREEN}✓${NC} API is working"
else
    echo -e "${YELLOW}⚠${NC} API not responding yet (may need a moment)"
fi
echo

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Feature Activated!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo "Next steps:"
echo "  1. Visit https://aaip.randy.it.com"
echo "  2. Click 'Draw History' tab"
echo "  3. View the new visualizations!"
echo
echo "Backups created:"
echo "  • backend/main.py.backup.*"
echo "  • frontend/src/App.jsx.backup.*"
echo
