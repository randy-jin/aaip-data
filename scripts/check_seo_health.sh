#!/bin/bash
# SEO Health Check Script
# Checks for common SEO issues in the AAIP Data Tracker

echo "======================================"
echo "  AAIP Data Tracker - SEO Health Check"
echo "======================================"
echo ""

cd "$(dirname "$0")/.." || exit

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Check 1: Required files exist
echo "📄 Checking required files..."
files=("frontend/public/sitemap.xml" "frontend/public/robots.txt" "frontend/public/manifest.json" "frontend/index.html")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $file missing"
        ((FAIL++))
    fi
done
echo ""

# Check 2: Required image assets
echo "🖼️  Checking image assets..."
images=("frontend/public/og-image.png" "frontend/public/twitter-card.png" "frontend/public/icon-192.png" "frontend/public/icon-512.png" "frontend/public/logo.png")
for img in "${images[@]}"; do
    if [ -f "$img" ]; then
        echo -e "${GREEN}✓${NC} $img exists"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠${NC} $img missing (recommended)"
        ((WARN++))
    fi
done
echo ""

# Check 3: Meta tags in index.html
echo "🏷️  Checking meta tags..."
required_meta=("og:title" "og:description" "og:image" "twitter:card" "description" "keywords" "robots")
for meta in "${required_meta[@]}"; do
    if grep -q "$meta" frontend/index.html; then
        echo -e "${GREEN}✓${NC} $meta found"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $meta missing"
        ((FAIL++))
    fi
done
echo ""

# Check 4: Structured data
echo "📊 Checking structured data..."
if grep -q "application/ld+json" frontend/index.html; then
    echo -e "${GREEN}✓${NC} JSON-LD structured data found"
    ((PASS++))
else
    echo -e "${RED}✗${NC} JSON-LD structured data missing"
    ((FAIL++))
fi
echo ""

# Check 5: Sitemap format
echo "🗺️  Checking sitemap format..."
if grep -q "<?xml version" frontend/public/sitemap.xml && grep -q "<urlset" frontend/public/sitemap.xml; then
    echo -e "${GREEN}✓${NC} Sitemap has valid XML format"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Sitemap format invalid"
    ((FAIL++))
fi
echo ""

# Check 6: Robots.txt configuration
echo "🤖 Checking robots.txt..."
if grep -q "Sitemap:" frontend/public/robots.txt; then
    echo -e "${GREEN}✓${NC} Sitemap URL in robots.txt"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Sitemap URL missing in robots.txt"
    ((FAIL++))
fi
echo ""

# Check 7: Build size (if dist exists)
echo "📦 Checking build size..."
if [ -d "frontend/dist" ]; then
    size=$(du -sh frontend/dist | cut -f1)
    echo -e "${GREEN}✓${NC} Build size: $size"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} No build found (run 'npm run build' first)"
    ((WARN++))
fi
echo ""

# Summary
echo "======================================"
echo "  Summary"
echo "======================================"
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${RED}Failed:${NC} $FAIL"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo ""

if [ $FAIL -eq 0 ]; then
    if [ $WARN -eq 0 ]; then
        echo -e "${GREEN}✓ SEO health check PASSED!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ SEO health check passed with warnings${NC}"
        echo "  Consider creating missing image assets"
        exit 0
    fi
else
    echo -e "${RED}✗ SEO health check FAILED${NC}"
    echo "  Please fix the failed checks above"
    exit 1
fi
