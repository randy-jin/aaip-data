#!/bin/bash
# Update Sitemap Last Modified Dates
# Run this after deploying content updates

cd "$(dirname "$0")/.." || exit

SITEMAP="frontend/public/sitemap.xml"
TODAY=$(date +%Y-%m-%d)

echo "Updating sitemap.xml with today's date: $TODAY"

# Update all lastmod dates to today
sed -i.bak "s|<lastmod>.*</lastmod>|<lastmod>$TODAY</lastmod>|g" "$SITEMAP"

# Show changes
echo ""
echo "Updated dates in sitemap.xml"
echo "Backup created: ${SITEMAP}.bak"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff $SITEMAP"
echo "2. Commit and push: git add $SITEMAP && git commit -m 'Update sitemap dates' && git push"
echo "3. After deployment, submit to Google Search Console"
