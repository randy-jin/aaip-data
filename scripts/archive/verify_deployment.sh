#!/bin/bash
###############################################################################
# AAIP Draw Records Feature - Post-Deployment Verification Script
# 
# Run this script after deployment to verify everything is working correctly
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AAIP Draw Records Feature - Deployment Verification${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo

# Configuration
API_URL="${API_URL:-https://aaip.randy.it.com/api}"
FRONTEND_URL="${FRONTEND_URL:-https://aaip.randy.it.com}"

pass_count=0
fail_count=0
warn_count=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    pass_count=$((pass_count + 1))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    fail_count=$((fail_count + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    warn_count=$((warn_count + 1))
}

echo -e "${BLUE}[1/6] Checking Database...${NC}"
if command -v psql &> /dev/null; then
    # Check if aaip_draws table exists
    if sudo -u postgres psql aaip_data -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'aaip_draws');" 2>/dev/null | grep -q "t"; then
        check_pass "Database table 'aaip_draws' exists"
        
        # Check record count
        count=$(sudo -u postgres psql aaip_data -t -c "SELECT COUNT(*) FROM aaip_draws;" 2>/dev/null | xargs)
        if [ "$count" -gt 0 ]; then
            check_pass "Database has $count draw records"
        else
            check_warn "Database has no draw records yet (run scraper)"
        fi
    else
        check_fail "Database table 'aaip_draws' not found"
    fi
else
    check_warn "Cannot verify database (psql not available)"
fi
echo

echo -e "${BLUE}[2/6] Checking Scraper Service...${NC}"
if systemctl is-active --quiet aaip-scraper.timer; then
    check_pass "Scraper timer is active"
else
    check_fail "Scraper timer is not active"
fi

if systemctl is-enabled --quiet aaip-scraper.timer; then
    check_pass "Scraper timer is enabled"
else
    check_warn "Scraper timer is not enabled for auto-start"
fi

# Check last scraper run
last_run=$(sudo journalctl -u aaip-scraper.service -n 1 --output=short-iso 2>/dev/null | head -1 || echo "Never")
echo -e "   Last scraper run: $last_run"
echo

echo -e "${BLUE}[3/6] Checking Backend Service...${NC}"
if systemctl is-active --quiet aaip-backend-test; then
    check_pass "Backend service is running"
else
    check_fail "Backend service is not running"
fi

# Check if backend is responding
if curl -sf "$API_URL/stats" > /dev/null 2>&1; then
    check_pass "Backend API is responding"
else
    check_fail "Backend API is not responding"
fi
echo

echo -e "${BLUE}[4/6] Checking API Endpoints...${NC}"

# Test /api/draws/streams
if curl -sf "$API_URL/draws/streams" | grep -q "categories"; then
    check_pass "API endpoint /api/draws/streams is working"
else
    check_fail "API endpoint /api/draws/streams failed"
fi

# Test /api/draws
if curl -sf "$API_URL/draws?limit=1" | grep -q "draw_date"; then
    check_pass "API endpoint /api/draws is working"
else
    check_warn "API endpoint /api/draws has no data (run scraper)"
fi

# Test /api/draws/stats
if curl -sf "$API_URL/draws/stats" > /dev/null 2>&1; then
    check_pass "API endpoint /api/draws/stats is working"
else
    check_warn "API endpoint /api/draws/stats failed (may have no data)"
fi
echo

echo -e "${BLUE}[5/6] Checking Frontend...${NC}"

# Check if frontend is accessible
if curl -sf "$FRONTEND_URL" > /dev/null 2>&1; then
    check_pass "Frontend is accessible at $FRONTEND_URL"
else
    check_fail "Frontend is not accessible at $FRONTEND_URL"
fi

# Check if JavaScript bundle exists
if curl -sf "$FRONTEND_URL" | grep -q "DrawsVisualization"; then
    check_pass "Frontend includes draw visualization code"
else
    check_warn "Frontend may not include latest draw visualization"
fi
echo

echo -e "${BLUE}[6/6] Checking File Integrity...${NC}"

files_to_check=(
    "setup_db_draws.sql"
    "scraper/scraper_draws.py"
    "backend/main_draws.py"
    "frontend/src/api_draws.js"
    "frontend/src/components/DrawsVisualization.jsx"
    "test_draws_feature.py"
    "deployment/deploy_draws_feature.sh"
    "docs/DRAWS_VISUALIZATION.md"
    "docs/DRAWS_QUICKSTART.md"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        check_pass "File exists: $file"
    else
        check_fail "File missing: $file"
    fi
done
echo

# Summary
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo
echo -e "  ${GREEN}✓ Passed${NC}: $pass_count"
echo -e "  ${YELLOW}⚠ Warnings${NC}: $warn_count"
echo -e "  ${RED}✗ Failed${NC}: $fail_count"
echo

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo
    echo "Next steps:"
    echo "  1. Visit $FRONTEND_URL"
    echo "  2. Click 'Draw History' tab"
    echo "  3. Verify charts are displaying correctly"
    echo
    if [ $warn_count -gt 0 ]; then
        echo "Notes:"
        echo "  • Some warnings may be normal if scraper hasn't run yet"
        echo "  • Wait 1 hour for first data collection, or run manually:"
        echo "    python3 scraper/scraper_draws.py"
    fi
else
    echo -e "${RED}✗ Some checks failed. Please review the errors above.${NC}"
    echo
    echo "Troubleshooting:"
    echo "  • Check logs: sudo journalctl -u aaip-backend-test -n 50"
    echo "  • Run tests: python3 test_draws_feature.py"
    echo "  • Review documentation: docs/DRAWS_VISUALIZATION.md"
fi

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo

exit $fail_count
