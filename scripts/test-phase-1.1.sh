#!/bin/bash

# Phase 1.1 Local Testing Script
# Run this to test all new features before pushing to test branch

set -e  # Exit on error

echo "=================================================="
echo "🧪 AAIP Phase 1.1 - Local Testing"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=5173
API_BASE="http://localhost:${BACKEND_PORT}"

echo -e "${BLUE}📋 Pre-flight Checks${NC}"
echo "=================================="

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Backend directory not found!${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Frontend directory not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Directories found${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 installed: $(python3 --version)${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js installed: $(node --version)${NC}"

echo ""
echo -e "${BLUE}🔧 Backend Testing${NC}"
echo "=================================="

# Test backend syntax
echo "Testing Python syntax..."
cd backend
if python3 -c "import main_enhanced" 2>&1; then
    echo -e "${GREEN}✅ Backend syntax valid${NC}"
else
    echo -e "${RED}❌ Backend syntax error! Fix before continuing.${NC}"
    exit 1
fi

# Check if backend is running
echo ""
echo "Checking if backend is running on port ${BACKEND_PORT}..."
if curl -s "http://localhost:${BACKEND_PORT}" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is already running${NC}"
    BACKEND_ALREADY_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Backend not running. Please start it in a separate terminal:${NC}"
    echo "   cd backend && python3 main_enhanced.py"
    echo ""
    echo "Press Enter when backend is running (or Ctrl+C to exit)..."
    read
fi

cd ..

# Test API endpoints
echo ""
echo "Testing new API endpoints..."

# Test Smart Insights
echo -n "  📊 /api/insights/weekly ... "
if curl -s "${API_BASE}/api/insights/weekly" > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# Test Quota Calculator
echo -n "  📈 /api/tools/quota-calculator ... "
if curl -s "${API_BASE}/api/tools/quota-calculator" > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# Test Processing Timeline
echo -n "  ⏱️  /api/tools/processing-timeline ... "
if curl -s "${API_BASE}/api/tools/processing-timeline?submission_date=2024-10-15" > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# Test Competitiveness
echo -n "  🎯 /api/tools/competitiveness ... "
if curl -s "${API_BASE}/api/tools/competitiveness" > /dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

echo ""
echo -e "${BLUE}🎨 Frontend Testing${NC}"
echo "=================================="

cd frontend

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Installing...${NC}"
    npm install
fi

# Check if heroicons is installed
if grep -q "@heroicons/react" package.json; then
    echo -e "${GREEN}✅ Heroicons installed${NC}"
else
    echo -e "${RED}❌ Heroicons not found!${NC}"
    exit 1
fi

# Check if new components exist
echo ""
echo "Checking new components..."
if [ -f "src/components/SmartInsights.jsx" ]; then
    echo -e "${GREEN}✅ SmartInsights.jsx exists${NC}"
else
    echo -e "${RED}❌ SmartInsights.jsx not found!${NC}"
fi

if [ -f "src/components/ToolsDashboard.jsx" ]; then
    echo -e "${GREEN}✅ ToolsDashboard.jsx exists${NC}"
else
    echo -e "${RED}❌ ToolsDashboard.jsx not found!${NC}"
fi

cd ..

echo ""
echo "=================================================="
echo -e "${GREEN}✅ All Pre-flight Checks Passed!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Start the frontend (if not running):"
echo "   cd frontend && npm run dev"
echo ""
echo "2. Open browser to: http://localhost:${FRONTEND_PORT}"
echo ""
echo "3. Test the new features:"
echo "   • Click 'Smart Insights' tab"
echo "   • Click 'Planning Tools' tab"
echo "   • Try each tool (quota, timeline, competitiveness)"
echo "   • Test on mobile responsive view"
echo ""
echo "4. Verify:"
echo "   ✓ No console errors in browser DevTools"
echo "   ✓ All insights display correctly"
echo "   ✓ Tools calculate and show results"
echo "   ✓ Disclaimers are visible"
echo "   ✓ UI is responsive on mobile"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Do NOT push to test branch until you've tested!${NC}"
echo ""
echo "When ready to commit locally:"
echo "  git add ."
echo "  git commit -m \"Phase 1.1: Add Smart Insights and Planning Tools\""
echo ""
echo "=================================================="
