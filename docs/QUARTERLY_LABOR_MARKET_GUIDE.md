# Quarterly Labor Market Data Collection

## Overview

This automated system collects Alberta labor market data quarterly from official sources and updates the "Labor Market Context" page on your website.

---

## How It Works

1. **Scrapes Job Bank Canada** for occupation outlooks (Good/Fair/Limited)
2. **Analyzes AAIP activity** from your database (nominations, draws, pool sizes)
3. **Calculates demand levels** for each stream (Strong/Moderate/Declining)
4. **Determines trends** (Up/Down/Stable)
5. **Saves to database** for the frontend to display
6. **Exports JSON file** for manual review

---

## When to Run

**Run this script quarterly:**
- **January** (for Q4 previous year data)
- **April** (for Q1 data)
- **July** (for Q2 data)
- **October** (for Q3 data)

---

## How to Run

### Manual Execution

```bash
cd /Users/jinzhiqiang/workspaces/doit/aaip-data/scraper
python3 quarterly_labor_market_collector.py
```

### Expected Output

```
======================================================================
Alberta Labor Market Quarterly Data Collection
Quarter: 2025-Q4 (November 2025)
======================================================================

📊 Analyzing Healthcare (DHCP)...
  NOC 31301: Good
  NOC 32101: Good
  NOC 33102: Fair
  → Demand: strong, Trend: up

📊 Analyzing Tourism & Hospitality...
  NOC 62020: Fair
  NOC 63200: Fair
  → Demand: moderate, Trend: stable

... (continues for all 6 streams)

✅ Saved 6 stream summaries to database
✅ Exported data to labor_market_data.json

======================================================================
✅ Quarterly data collection complete!
======================================================================

Quarter: 2025-Q4
Streams analyzed: 6

Next steps:
1. Review the generated labor_market_data.json file
2. Manually refine summaries and recommendations  
3. Frontend will automatically load from database
4. Update again next quarter (in 3 months)
```

---

## Automated Scheduling

### Option 1: Cron Job (Linux/Mac)

Add to crontab:
```bash
# Run quarterly labor market collection
# At 2 AM on the 1st day of Jan, Apr, Jul, Oct
0 2 1 1,4,7,10 * cd /path/to/aaip-data/scraper && python3 quarterly_labor_market_collector.py >> /var/log/labor_market_collector.log 2>&1
```

### Option 2: GitHub Actions (Recommended)

Create `.github/workflows/quarterly-labor-market.yml`:

```yaml
name: Quarterly Labor Market Data Collection

on:
  schedule:
    # Run on 1st of Jan, Apr, Jul, Oct at 2 AM UTC
    - cron: '0 2 1 1,4,7,10 *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  collect-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4 psycopg2-binary python-dotenv
      
      - name: Run collector
        env:
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_NAME: ${{ secrets.DB_NAME }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
        run: |
          cd scraper
          python3 quarterly_labor_market_collector.py
      
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add scraper/labor_market_data.json
          git commit -m "Update Q$(date +%m) labor market data" || echo "No changes"
          git push
```

---

## Data Sources

The collector uses:

1. **Job Bank Canada**
   - `https://www.jobbank.gc.ca/marketreport/outlook-occupation/{NOC}/48`
   - Scrapes occupation outlooks for Alberta (area code 48)

2. **Your AAIP Database**
   - Recent nominations by stream (past 90 days)
   - Draw frequency by stream
   - Current EOI pool sizes

3. **Combined Analysis**
   - Weighs Job Bank outlook + AAIP activity
   - Calculates demand and trend indicators

---

## Output Files

### 1. Database Table: `labor_market_quarterly`

```sql
CREATE TABLE labor_market_quarterly (
    id SERIAL PRIMARY KEY,
    quarter VARCHAR(10) NOT NULL,           -- '2025-Q4'
    update_date VARCHAR(50) NOT NULL,       -- 'November 2025'
    stream_name VARCHAR(255) NOT NULL,      -- 'Healthcare (DHCP)'
    demand_level VARCHAR(20) NOT NULL,      -- 'strong' / 'moderate' / 'declining'
    trend VARCHAR(20) NOT NULL,             -- 'up' / 'down' / 'stable'
    sectors TEXT,                           -- JSON array of occupations
    noc_codes TEXT,                         -- JSON array of NOC codes
    generated_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(quarter, stream_name)
);
```

### 2. JSON Export: `labor_market_data.json`

```json
{
  "quarter": "2025-Q4",
  "update_date": "November 2025",
  "generated_at": "2025-11-19T05:00:00",
  "streams": [
    {
      "name": "Healthcare (DHCP)",
      "demand": "strong",
      "trend": "up",
      "sectors": ["Registered Nurses", "LPNs", "Healthcare Aides"],
      "noc_codes": ["31301", "32101", "33102"]
    },
    ...
  ]
}
```

---

## Frontend Integration

The frontend automatically fetches from the API:

```
GET /api/labor-market/quarterly
```

If data exists, it displays:
- Demand badges (🟢 Strong / 🟡 Moderate / 🔴 Competitive)
- Trend arrows (↗️ Up / ↘️ Down / ➖ Stable)
- Key occupations for each stream

If no data exists, it falls back to placeholder content.

---

## Manual Refinement

After running the collector:

1. **Review** `labor_market_data.json`
2. **Check** if demand levels make sense
3. **Update database** manually if needed:

```sql
UPDATE labor_market_quarterly
SET 
    demand_level = 'strong',
    trend = 'up'
WHERE quarter = '2025-Q4' AND stream_name = 'Healthcare (DHCP)';
```

4. **Add summaries & recommendations** in the frontend component if needed

---

## Monitored Occupations

### Healthcare (DHCP)
- NOC 31301: Registered Nurses
- NOC 32101: Licensed Practical Nurses
- NOC 33102: Healthcare Aides

### Tourism & Hospitality
- NOC 62020: Food Service Supervisors
- NOC 63200: Cooks
- NOC 64300: Hotel Front Desk

### Technology
- NOC 21231: Software Engineers
- NOC 21232: Software Developers
- NOC 21233: Computer Programmers

### Construction & Trades
- NOC 72010-72013: Electricians, Plumbers, Carpenters

### Agriculture & Rural
- NOC 82030: Farm Supervisors
- NOC 84120: Specialized Livestock Workers
- NOC 94141: Meat Cutters

### General Business
- NOC 62010: Retail Supervisors
- NOC 73300: Transport Truck Drivers
- NOC 13110: Administrative Assistants

---

## Troubleshooting

### Problem: "No AAIP activity data"
**Solution**: Make sure main AAIP scraper has run recently with current data

### Problem: Job Bank scraping fails
**Solution**: 
- Check if Job Bank website structure changed
- Update CSS selectors in `scrape_job_bank_outlook()`
- May need to manually input data that quarter

### Problem: All demands show as "declining"
**Solution**: 
- Check if database has recent AAIP data
- Run main scraper first
- Manually review and adjust if needed

---

## Maintenance

- **Quarterly**: Run the collector (automated or manual)
- **Annually**: Review NOC codes (NOC system updates every few years)
- **As needed**: Update scraping logic if Job Bank changes

---

## Next Steps

1. **Test it now**:
   ```bash
   cd scraper
   python3 quarterly_labor_market_collector.py
   ```

2. **Review output**:
   - Check `labor_market_data.json`
   - Verify database entries
   - Test frontend display

3. **Schedule it**:
   - Set up cron job or GitHub Action
   - Mark calendar for manual review each quarter

4. **Refine as needed**:
   - Add more NOC codes
   - Adjust demand calculation logic
   - Customize summaries

---

**The system is now ready to provide real, quarterly-updated labor market data!** 🎉
