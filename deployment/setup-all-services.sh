#!/bin/bash

# AAIP Data Tracker - Complete Service Setup Script
# This script sets up all systemd services and timers for automated data collection

set -e

DEPLOY_DIR="/home/randy/deploy/aaip-data"
SCRAPER_DIR="${DEPLOY_DIR}/scraper"
DEPLOYMENT_DIR="${DEPLOY_DIR}/deployment"

echo "=================================================="
echo "AAIP Data Tracker - Service Setup"
echo "=================================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run with sudo"
    echo "Usage: sudo ./setup-all-services.sh"
    exit 1
fi

echo "✅ Running with sudo privileges"
echo ""

# Function to copy and enable service
setup_service() {
    local service_file=$1
    local timer_file=$2
    
    echo "Setting up ${service_file}..."
    
    # Copy service file
    cp "${DEPLOYMENT_DIR}/${service_file}" /etc/systemd/system/
    chmod 644 "/etc/systemd/system/${service_file}"
    
    # Copy timer if provided
    if [ -n "${timer_file}" ]; then
        echo "Setting up ${timer_file}..."
        cp "${DEPLOYMENT_DIR}/${timer_file}" /etc/systemd/system/
        chmod 644 "/etc/systemd/system/${timer_file}"
    fi
    
    echo "✅ Copied to /etc/systemd/system/"
}

# 1. Backend Service (continuous)
echo "1️⃣  Backend Service"
echo "   - Service: aaip-backend-test.service"
echo "   - Type: Continuous (runs FastAPI server)"
echo ""
setup_service "aaip-backend-test.service"
echo ""

# 2. Main Data Scraper (hourly)
echo "2️⃣  Main Data Scraper"
echo "   - Service: aaip-scraper.service"
echo "   - Timer: aaip-scraper.timer (runs hourly)"
echo "   - Collects: Processing times, draw records, EOI pool data"
echo ""
setup_service "aaip-scraper.service" "aaip-scraper.timer"
echo ""

# 3. Extended Data Collectors (daily)
echo "3️⃣  Extended Data Collectors"
echo "   - Service: aaip-extended-collectors.service"
echo "   - Timer: aaip-extended-collectors.timer (runs daily at 3 AM)"
echo "   - Collects: Express Entry, Economy, Labor Market, Job Bank"
echo ""
setup_service "aaip-extended-collectors.service" "aaip-extended-collectors.timer"
echo ""

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload
echo "✅ Systemd daemon reloaded"
echo ""

# Enable and start services
echo "=================================================="
echo "Enabling and Starting Services"
echo "=================================================="
echo ""

# Backend (start immediately, enable on boot)
echo "1️⃣  Starting Backend Service..."
systemctl enable aaip-backend-test.service
systemctl restart aaip-backend-test.service
systemctl status aaip-backend-test.service --no-pager -l
echo ""

# Main Scraper Timer (enable, will run hourly)
echo "2️⃣  Starting Main Scraper Timer..."
systemctl enable aaip-scraper.timer
systemctl restart aaip-scraper.timer
systemctl status aaip-scraper.timer --no-pager -l
echo ""

# Extended Collectors Timer (enable, will run daily)
echo "3️⃣  Starting Extended Collectors Timer..."
systemctl enable aaip-extended-collectors.timer
systemctl restart aaip-extended-collectors.timer
systemctl status aaip-extended-collectors.timer --no-pager -l
echo ""

# Run scrapers once immediately
echo "=================================================="
echo "Running Initial Data Collection"
echo "=================================================="
echo ""

echo "🔄 Running main scraper once..."
systemctl start aaip-scraper.service
sleep 5
systemctl status aaip-scraper.service --no-pager -l
echo ""

echo "🔄 Running extended collectors once..."
systemctl start aaip-extended-collectors.service
sleep 5
systemctl status aaip-extended-collectors.service --no-pager -l
echo ""

# Show timer schedules
echo "=================================================="
echo "Service Schedule Summary"
echo "=================================================="
echo ""
systemctl list-timers aaip-* --no-pager
echo ""

# Show service status
echo "=================================================="
echo "Service Status Summary"
echo "=================================================="
echo ""
echo "Backend Service:"
systemctl is-active aaip-backend-test.service && echo "✅ Running" || echo "❌ Not Running"
echo ""
echo "Main Scraper Timer:"
systemctl is-active aaip-scraper.timer && echo "✅ Active" || echo "❌ Inactive"
echo ""
echo "Extended Collectors Timer:"
systemctl is-active aaip-extended-collectors.timer && echo "✅ Active" || echo "❌ Inactive"
echo ""

echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📋 Total Services:"
echo "   - 1 Backend Service (continuous)"
echo "   - 2 Data Collector Services (scheduled)"
echo ""
echo "📅 Collection Schedule:"
echo "   - Main Scraper: Every hour"
echo "   - Extended Collectors: Daily at 3 AM"
echo ""
echo "🔍 Useful Commands:"
echo "   View logs:"
echo "     sudo journalctl -u aaip-backend-test -f"
echo "     sudo journalctl -u aaip-scraper -f"
echo "     sudo journalctl -u aaip-extended-collectors -f"
echo ""
echo "   Manual runs:"
echo "     sudo systemctl start aaip-scraper.service"
echo "     sudo systemctl start aaip-extended-collectors.service"
echo ""
echo "   Check timers:"
echo "     sudo systemctl list-timers aaip-*"
echo ""
echo "   Service status:"
echo "     sudo systemctl status aaip-backend-test"
echo "     sudo systemctl status aaip-scraper.timer"
echo "     sudo systemctl status aaip-extended-collectors.timer"
echo ""
