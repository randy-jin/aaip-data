#!/bin/bash
# Deploy Scraper Updates
# This script updates the consolidated scraper on the production server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Configuration
DEPLOY_PATH="/home/$USER/deploy/aaip-data"

clear
echo "========================================"
echo "   Deploy Consolidated Scraper Update"
echo "========================================"
echo ""
print_info "This will update the scraper to the new consolidated version"
print_info "Deploy path: $DEPLOY_PATH"
echo ""

# Confirm
read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Deployment cancelled"
    exit 0
fi

# ============================================
# Step 1: Navigate to deployment directory
# ============================================
print_step "Step 1/7: Navigating to deployment directory"

if [ ! -d "$DEPLOY_PATH" ]; then
    print_error "Deployment directory not found: $DEPLOY_PATH"
    exit 1
fi

cd "$DEPLOY_PATH"
print_success "In directory: $(pwd)"

# ============================================
# Step 2: Check current branch
# ============================================
print_step "Step 2/7: Checking git status"

CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "Not on main branch, switching to main..."
    git checkout main
fi

# ============================================
# Step 3: Pull latest changes
# ============================================
print_step "Step 3/7: Pulling latest changes from repository"

print_info "Fetching updates..."
git fetch origin

print_info "Pulling changes..."
git pull origin main

print_success "Repository updated"

# ============================================
# Step 4: Check scraper file exists
# ============================================
print_step "Step 4/7: Verifying consolidated scraper"

if [ ! -f "scraper/scraper.py" ]; then
    print_error "Consolidated scraper not found: scraper/scraper.py"
    exit 1
fi

print_success "Consolidated scraper found"

# Show what was updated
echo ""
print_info "Recent commits:"
git log --oneline -3
echo ""

# ============================================
# Step 5: Update systemd service
# ============================================
print_step "Step 5/7: Updating systemd service"

print_info "Copying service file..."
sudo cp deployment/aaip-scraper.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/aaip-scraper.service

print_info "Reloading systemd daemon..."
sudo systemctl daemon-reload

print_success "Systemd service updated"

# ============================================
# Step 6: Restart timer
# ============================================
print_step "Step 6/7: Restarting scraper timer"

print_info "Restarting aaip-scraper.timer..."
sudo systemctl restart aaip-scraper.timer

sleep 2

# Verify timer is running
if sudo systemctl is-active --quiet aaip-scraper.timer; then
    print_success "Timer restarted successfully"
else
    print_error "Timer failed to start"
    exit 1
fi

# ============================================
# Step 7: Test the new scraper
# ============================================
print_step "Step 7/7: Testing consolidated scraper"

echo ""
read -p "Run a test scrape now? (Y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_info "Running test scrape..."
    echo ""
    echo "----------------------------------------"

    sudo systemctl start aaip-scraper.service

    # Wait for service to complete
    sleep 5

    print_info "Service status:"
    sudo systemctl status aaip-scraper.service --no-pager -l || true

    echo ""
    echo "----------------------------------------"
    print_info "Recent logs:"
    sudo journalctl -u aaip-scraper.service -n 30 --no-pager
    echo "----------------------------------------"
fi

# ============================================
# Deployment Complete
# ============================================
echo ""
echo "========================================"
print_success "Deployment Complete!"
echo "========================================"
echo ""

print_info "Scraper Status:"
sudo systemctl status aaip-scraper.timer --no-pager -l

echo ""
print_info "Next scheduled run:"
systemctl list-timers | grep aaip

echo ""
print_success "The consolidated scraper is now active!"
echo ""
print_info "What's new:"
echo "  ✓ Single scraper collects both nomination AND draw data"
echo "  ✓ Runs automatically every hour"
echo "  ✓ Smart saving: only saves changed data"
echo "  ✓ Incremental draw collection"
echo ""
print_info "Useful commands:"
echo "  View live logs:      sudo journalctl -u aaip-scraper.service -f"
echo "  Check timer status:  sudo systemctl status aaip-scraper.timer"
echo "  Manual trigger:      sudo systemctl start aaip-scraper.service"
echo "  View schedule:       systemctl list-timers | grep aaip"
echo ""
