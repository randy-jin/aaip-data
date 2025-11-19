#!/bin/bash

echo "======================================================================"
echo "Phase 3 Implementation - Quick Test Script"
echo "======================================================================"
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    exit 1
fi

echo "📋 Checking Phase 3 Files..."
echo ""

# Check backend files
echo "Backend Files:"
if [ -f "backend/main_enhanced.py" ]; then
    echo "  ✅ main_enhanced.py exists"
    
    # Check for API endpoints
    if grep -q "success-stories" backend/main_enhanced.py; then
        echo "  ✅ Success stories APIs found"
    else
        echo "  ⚠️  Success stories APIs not found"
    fi
    
    if grep -q "trends/prediction" backend/main_enhanced.py; then
        echo "  ✅ Prediction APIs found"
    else
        echo "  ⚠️  Prediction APIs not found"
    fi
else
    echo "  ❌ main_enhanced.py not found"
fi

if [ -f "backend/run_migrations.py" ]; then
    echo "  ✅ run_migrations.py exists"
else
    echo "  ⚠️  run_migrations.py not found"
fi

if [ -f "backend/db/migrations/007_create_success_stories.sql" ]; then
    echo "  ✅ Migration file exists"
else
    echo "  ⚠️  Migration file not found"
fi

echo ""
echo "Frontend Files:"
if [ -f "frontend/src/components/SuccessStories.jsx" ]; then
    echo "  ✅ SuccessStories.jsx exists"
else
    echo "  ❌ SuccessStories.jsx not found"
fi

if [ -f "frontend/src/pages/Predictions.jsx" ]; then
    echo "  ✅ Predictions.jsx exists"
else
    echo "  ❌ Predictions.jsx not found"
fi

if [ -f "frontend/src/components/WhatIfCalculator.jsx" ]; then
    echo "  ✅ WhatIfCalculator.jsx exists"
else
    echo "  ⚠️  WhatIfCalculator.jsx not found"
fi

echo ""
echo "Translations:"
if grep -q '"community"' frontend/src/locales/en.json; then
    echo "  ✅ English translation for community tab"
else
    echo "  ⚠️  English translation missing"
fi

if grep -q '"community"' frontend/src/locales/zh.json; then
    echo "  ✅ Chinese translation for community tab"
else
    echo "  ⚠️  Chinese translation missing"
fi

if grep -q '"predictions"' frontend/src/locales/en.json; then
    echo "  ✅ English translation for predictions tab"
else
    echo "  ⚠️  English translation missing"
fi

echo ""
echo "App Integration:"
if grep -q "activeTab === 'community'" frontend/src/App.jsx; then
    echo "  ✅ Community tab integrated in App.jsx"
else
    echo "  ⚠️  Community tab not found in App.jsx"
fi

if grep -q "activeTab === 'predictions'" frontend/src/App.jsx; then
    echo "  ✅ Predictions tab integrated in App.jsx"
else
    echo "  ⚠️  Predictions tab not found in App.jsx"
fi

if grep -q "import SuccessStories" frontend/src/App.jsx; then
    echo "  ✅ SuccessStories component imported"
else
    echo "  ⚠️  SuccessStories import not found"
fi

if grep -q "import Predictions" frontend/src/App.jsx; then
    echo "  ✅ Predictions component imported"
else
    echo "  ⚠️  Predictions import not found"
fi

echo ""
echo "======================================================================"
echo "✅ Phase 3 Implementation Check Complete"
echo "======================================================================"
echo ""
echo "Next Steps:"
echo "1. Run database migration: cd backend && python3 run_migrations.py"
echo "2. Start backend: cd backend && python3 main_enhanced.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Test both new tabs: 'Trend Predictions' and 'Success Stories'"
echo ""
echo "For detailed information, see: PHASE3_COMPLETE.md"
echo "======================================================================"
