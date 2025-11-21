#!/bin/bash

# AAIP Data Collectors - One-Click Setup Script
# Run this on the server to set up all data collection services

set -e

echo "=========================================="
echo "AAIP Data Collectors Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on server
if [ ! -d "/home/randy/deploy/aaip-data" ]; then
    echo -e "${RED}Error: This script must be run on the deployment server${NC}"
    echo "Expected directory: /home/randy/deploy/aaip-data"
    exit 1
fi

cd /home/randy/deploy/aaip-data

echo -e "${YELLOW}Step 1: Copying service files to systemd...${NC}"
sudo cp deployment/aaip-scraper.service /etc/systemd/system/
sudo cp deployment/aaip-scraper.timer /etc/systemd/system/
sudo cp deployment/aaip-extended-collectors.service /etc/systemd/system/
sudo cp deployment/aaip-extended-collectors.timer /etc/systemd/system/
echo -e "${GREEN}✓ Service files copied${NC}"
echo ""

echo -e "${YELLOW}Step 2: Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Systemd reloaded${NC}"
echo ""

echo -e "${YELLOW}Step 3: Stopping any running timers...${NC}"
sudo systemctl stop aaip-scraper.timer 2>/dev/null || true
sudo systemctl stop aaip-extended-collectors.timer 2>/dev/null || true
echo -e "${GREEN}✓ Timers stopped${NC}"
echo ""

echo -e "${YELLOW}Step 4: Enabling timers (auto-start on boot)...${NC}"
sudo systemctl enable aaip-scraper.timer
sudo systemctl enable aaip-extended-collectors.timer
echo -e "${GREEN}✓ Timers enabled${NC}"
echo ""

echo -e "${YELLOW}Step 5: Starting timers...${NC}"
sudo systemctl start aaip-scraper.timer
sudo systemctl start aaip-extended-collectors.timer
echo -e "${GREEN}✓ Timers started${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Service Status:"
echo "----------------------------------------"
sudo systemctl status aaip-scraper.timer --no-pager | head -n 5
echo ""
sudo systemctl status aaip-extended-collectors.timer --no-pager | head -n 5
echo ""

echo "Next Scheduled Runs:"
echo "----------------------------------------"
sudo systemctl list-timers | grep aaip
echo ""

echo "Useful Commands:"
echo "----------------------------------------"
echo "  Check status:  systemctl list-timers | grep aaip"
echo "  View logs:     sudo journalctl -u aaip-scraper.service -f"
echo "  Manual run:    sudo systemctl start aaip-scraper.service"
echo ""
echo -e "${GREEN}All data collectors are now running automatically!${NC}"
