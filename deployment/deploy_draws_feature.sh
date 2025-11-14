#!/bin/bash

###############################################################################
# AAIP Draw Records Feature - One-Click Deployment Script
# 
# This script automates the deployment of the draw records visualization
# feature to the AAIP Data Tracker system.
#
# Usage: ./deploy_draws_feature.sh
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/randy/deploy/aaip-data"
DB_NAME="aaip_data"
DB_USER="randy"
BACKEND_SERVICE="aaip-backend-test"
SCRAPER_SERVICE="aaip-scraper"
FRONTEND_DIR="/var/www/html/aaip-test"

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_deps=0
    
    # Check if running as correct user
    if [ "$USER" != "randy" ]; then
        print_warning "Not running as user 'randy'. Some commands may require sudo."
    fi
    
    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL client found"
    else
        print_error "PostgreSQL client not found"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_success "Python 3 found"
    else
        print_error "Python 3 not found"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Check Node.js
    if command -v npm &> /dev/null; then
        print_success "npm found"
    else
        print_error "npm not found"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Check systemd
    if command -v systemctl &> /dev/null; then
        print_success "systemd found"
    else
        print_error "systemd not found"
        missing_deps=$((missing_deps + 1))
    fi
    
    if [ $missing_deps -gt 0 ]; then
        print_error "Missing $missing_deps required dependencies. Please install them first."
        exit 1
    fi
    
    print_success "All prerequisites met"
    echo
}

backup_database() {
    print_header "Backing Up Database"
    
    local backup_file="aaip_data_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    print_info "Creating backup: $backup_file"
    
    if sudo -u postgres pg_dump $DB_NAME > "$PROJECT_DIR/backups/$backup_file" 2>/dev/null; then
        print_success "Database backed up successfully"
    else
        print_warning "Could not create database backup (continuing anyway)"
    fi
    
    echo
}

update_database_schema() {
    print_header "Updating Database Schema"
    
    print_info "Installing draws table and indexes..."
    
    if sudo -u postgres psql $DB_NAME < "$PROJECT_DIR/setup_db_draws.sql" 2>/dev/null; then
        print_success "Database schema updated"
    else
        print_error "Failed to update database schema"
        exit 1
    fi
    
    # Verify table creation
    local table_exists=$(sudo -u postgres psql -t $DB_NAME -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'aaip_draws');" | xargs)
    
    if [ "$table_exists" = "t" ]; then
        print_success "aaip_draws table verified"
    else
        print_error "aaip_draws table not found after creation"
        exit 1
    fi
    
    echo
}

update_scraper() {
    print_header "Updating Scraper"
    
    cd "$PROJECT_DIR/scraper"
    
    # Test scraper
    print_info "Testing new scraper..."
    if python3 scraper_draws.py; then
        print_success "Scraper test successful"
    else
        print_error "Scraper test failed"
        exit 1
    fi
    
    # Update systemd service
    print_info "Updating systemd service..."
    
    local service_file="/etc/systemd/system/${SCRAPER_SERVICE}.service"
    
    if [ -f "$service_file" ]; then
        # Backup original service file
        sudo cp "$service_file" "${service_file}.backup"
        
        # Update ExecStart line
        sudo sed -i "s|ExecStart=.*|ExecStart=/usr/bin/python3 $PROJECT_DIR/scraper/scraper_draws.py|" "$service_file"
        
        print_success "Service file updated"
    else
        print_warning "Service file not found at $service_file"
        print_info "You may need to manually update the service configuration"
    fi
    
    # Reload and restart
    print_info "Reloading systemd and restarting scraper..."
    sudo systemctl daemon-reload
    sudo systemctl restart ${SCRAPER_SERVICE}.service
    
    if sudo systemctl is-active --quiet ${SCRAPER_SERVICE}.timer; then
        print_success "Scraper timer is active"
    else
        print_warning "Scraper timer is not active. Starting it..."
        sudo systemctl start ${SCRAPER_SERVICE}.timer
    fi
    
    echo
}

update_backend() {
    print_header "Updating Backend"
    
    cd "$PROJECT_DIR/backend"
    
    # Backup current main.py
    if [ -f "main.py" ]; then
        cp main.py "main.py.backup.$(date +%Y%m%d_%H%M%S)"
        print_success "Backed up current main.py"
    fi
    
    # Copy new backend
    if [ -f "main_draws.py" ]; then
        cp main_draws.py main.py
        print_success "Updated main.py with draw endpoints"
    else
        print_error "main_draws.py not found"
        exit 1
    fi
    
    # Restart backend service
    print_info "Restarting backend service..."
    sudo systemctl restart ${BACKEND_SERVICE}.service
    
    # Wait for service to start
    sleep 3
    
    if sudo systemctl is-active --quiet ${BACKEND_SERVICE}.service; then
        print_success "Backend service is running"
    else
        print_error "Backend service failed to start"
        print_info "Check logs: sudo journalctl -u ${BACKEND_SERVICE}.service -n 50"
        exit 1
    fi
    
    # Test API
    print_info "Testing API endpoints..."
    if curl -s -f http://localhost:8000/api/stats > /dev/null; then
        print_success "API is responding"
    else
        print_warning "API test failed (may still be starting up)"
    fi
    
    echo
}

update_frontend() {
    print_header "Updating Frontend"
    
    cd "$PROJECT_DIR/frontend"
    
    # Backup current App.jsx
    if [ -f "src/App.jsx" ]; then
        cp src/App.jsx "src/App.jsx.backup.$(date +%Y%m%d_%H%M%S)"
        print_success "Backed up current App.jsx"
    fi
    
    # Copy new files
    if [ -f "src/App_with_draws.jsx" ]; then
        cp src/App_with_draws.jsx src/App.jsx
        print_success "Updated App.jsx"
    else
        print_error "App_with_draws.jsx not found"
        exit 1
    fi
    
    # Install dependencies if needed
    print_info "Checking npm dependencies..."
    if [ ! -d "node_modules" ]; then
        print_info "Installing dependencies..."
        npm install
    fi
    
    # Build frontend
    print_info "Building frontend..."
    if npm run build; then
        print_success "Frontend built successfully"
    else
        print_error "Frontend build failed"
        exit 1
    fi
    
    # Deploy to web server
    print_info "Deploying to web server..."
    if sudo cp -r dist/* "$FRONTEND_DIR/"; then
        print_success "Frontend deployed to $FRONTEND_DIR"
    else
        print_error "Failed to deploy frontend"
        exit 1
    fi
    
    echo
}

run_tests() {
    print_header "Running Tests"
    
    cd "$PROJECT_DIR"
    
    print_info "Running test suite..."
    
    if python3 test_draws_feature.py; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed. Check output above."
        print_info "System may still be functional, but review any errors."
    fi
    
    echo
}

print_summary() {
    print_header "Deployment Summary"
    
    echo -e "${GREEN}✓ Draw Records Feature Deployed Successfully!${NC}"
    echo
    echo "Components updated:"
    echo "  • Database schema with aaip_draws table"
    echo "  • Scraper with incremental draw collection"
    echo "  • Backend with draw visualization API"
    echo "  • Frontend with interactive charts"
    echo
    echo "Services status:"
    sudo systemctl is-active ${BACKEND_SERVICE}.service && echo -e "  ${GREEN}✓${NC} Backend: Running" || echo -e "  ${RED}✗${NC} Backend: Not running"
    sudo systemctl is-active ${SCRAPER_SERVICE}.timer && echo -e "  ${GREEN}✓${NC} Scraper timer: Active" || echo -e "  ${RED}✗${NC} Scraper timer: Inactive"
    echo
    echo "Database stats:"
    local draw_count=$(sudo -u postgres psql -t $DB_NAME -c "SELECT COUNT(*) FROM aaip_draws;" | xargs)
    echo "  • Draw records: $draw_count"
    echo
    echo "Next steps:"
    echo "  1. Visit https://aaip.randy.it.com"
    echo "  2. Click 'Draw History' tab"
    echo "  3. Explore the visualizations!"
    echo
    echo "Useful commands:"
    echo "  • Check scraper logs: sudo journalctl -u ${SCRAPER_SERVICE}.service -f"
    echo "  • Check backend logs: sudo journalctl -u ${BACKEND_SERVICE}.service -f"
    echo "  • Run tests: python3 test_draws_feature.py"
    echo "  • View draw data: sudo -u postgres psql $DB_NAME -c 'SELECT * FROM aaip_draws LIMIT 5;'"
    echo
}

main() {
    echo
    print_header "AAIP Draw Records Feature - Deployment Script"
    echo
    print_info "Starting deployment at $(date)"
    echo
    
    # Create backups directory if it doesn't exist
    mkdir -p "$PROJECT_DIR/backups"
    
    # Run deployment steps
    check_prerequisites
    backup_database
    update_database_schema
    update_scraper
    update_backend
    update_frontend
    run_tests
    
    echo
    print_summary
    
    print_success "Deployment completed at $(date)"
    echo
}

# Run main function
main "$@"
