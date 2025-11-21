#!/bin/bash
# AAIP Data Collectors - Status Check Script
# Run this to quickly check the health of all data collection services

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=========================================="
echo "AAIP Data Collectors - Health Check"
echo -e "==========================================${NC}"
echo ""

# Check if we're on the server
if [ ! -d "/home/randy/deploy/aaip-data" ]; then
    echo -e "${RED}⚠ Warning: Not on deployment server${NC}"
    echo "This script is designed to run on: /home/randy/deploy/aaip-data"
    echo ""
fi

# Function to check service status
check_service() {
    local service=$1
    local name=$2
    
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✓${NC} $name: ${GREEN}Running${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} $name: ${RED}Stopped${NC}"
        return 1
    fi
}

# Function to check timer status
check_timer() {
    local timer=$1
    local name=$2
    
    if systemctl is-active --quiet "$timer"; then
        echo -e "${GREEN}✓${NC} $name: ${GREEN}Active${NC}"
        # Get next run time
        next_run=$(systemctl status "$timer" 2>/dev/null | grep "Trigger:" | awk '{print $2, $3, $4, $5}')
        if [ -n "$next_run" ]; then
            echo -e "  ${BLUE}→${NC} Next run: $next_run"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $name: ${RED}Inactive${NC}"
        return 1
    fi
}

echo -e "${YELLOW}━━━ Backend Service ━━━${NC}"
check_service "aaip-backend-test.service" "Backend API"
echo ""

echo -e "${YELLOW}━━━ Data Collection Timers ━━━${NC}"
check_timer "aaip-scraper.timer" "Hourly Collector"
check_timer "aaip-extended-collectors.timer" "Daily Collector"
echo ""

echo -e "${YELLOW}━━━ Last Collection Runs ━━━${NC}"

# Check last hourly collection
echo -e "${BLUE}Hourly Collector (aaip-scraper):${NC}"
last_hourly=$(systemctl status aaip-scraper.service 2>/dev/null | grep "Deactivated:" | head -1 | awk '{print $2, $3}')
if [ -n "$last_hourly" ]; then
    echo -e "  Last run: $last_hourly"
    
    # Check if it succeeded
    if journalctl -u aaip-scraper.service -n 1 --no-pager 2>/dev/null | grep -q "Failed"; then
        echo -e "  Status: ${RED}Failed${NC}"
    else
        echo -e "  Status: ${GREEN}Success${NC}"
    fi
else
    echo -e "  ${YELLOW}No recent runs found${NC}"
fi
echo ""

# Check last daily collection
echo -e "${BLUE}Daily Collector (aaip-extended-collectors):${NC}"
last_daily=$(systemctl status aaip-extended-collectors.service 2>/dev/null | grep "Deactivated:" | head -1 | awk '{print $2, $3}')
if [ -n "$last_daily" ]; then
    echo -e "  Last run: $last_daily"
    
    # Check if it succeeded
    if journalctl -u aaip-extended-collectors.service -n 1 --no-pager 2>/dev/null | grep -q "Failed"; then
        echo -e "  Status: ${RED}Failed${NC}"
    else
        echo -e "  Status: ${GREEN}Success${NC}"
    fi
else
    echo -e "  ${YELLOW}No recent runs found${NC}"
fi
echo ""

echo -e "${YELLOW}━━━ Database Status ━━━${NC}"
if command -v psql &> /dev/null; then
    # Try to connect to database
    if psql "postgresql://randy:1234QWER$@randy-vmware-virtual-platform.tail566241.ts.net:5432/aaip_data_trend_dev_db" -c "SELECT 1" &>/dev/null; then
        echo -e "${GREEN}✓${NC} Database: ${GREEN}Connected${NC}"
        
        # Get record counts
        draw_count=$(psql "postgresql://randy:1234QWER$@randy-vmware-virtual-platform.tail566241.ts.net:5432/aaip_data_trend_dev_db" -t -c "SELECT COUNT(*) FROM aaip_draws" 2>/dev/null | xargs)
        eoi_count=$(psql "postgresql://randy:1234QWER$@randy-vmware-virtual-platform.tail566241.ts.net:5432/aaip_data_trend_dev_db" -t -c "SELECT COUNT(*) FROM eoi_pool_data" 2>/dev/null | xargs)
        news_count=$(psql "postgresql://randy:1234QWER$@randy-vmware-virtual-platform.tail566241.ts.net:5432/aaip_data_trend_dev_db" -t -c "SELECT COUNT(*) FROM aaip_news" 2>/dev/null | xargs)
        
        echo -e "  ${BLUE}→${NC} Draw records: $draw_count"
        echo -e "  ${BLUE}→${NC} EOI pool records: $eoi_count"
        echo -e "  ${BLUE}→${NC} News articles: $news_count"
    else
        echo -e "${RED}✗${NC} Database: ${RED}Cannot connect${NC}"
    fi
else
    echo -e "${YELLOW}⚠${NC} psql not found - skipping database check"
fi
echo ""

echo -e "${YELLOW}━━━ Quick Actions ━━━${NC}"
echo "View logs:  sudo journalctl -u aaip-scraper.service -f"
echo "Manual run: sudo systemctl start aaip-scraper.service"
echo "Full guide: cat deployment/DATA_COLLECTORS_SETUP.md"
echo ""

echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}Health check complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
