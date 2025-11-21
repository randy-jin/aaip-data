# AAIP Data Collection Summary

## Overview
This project collects and tracks Alberta Advantage Immigration Program (AAIP) data through scheduled hourly scraping of official government sources.

## Data Sources & Collection Schedule

### 1. **AAIP Processing Information** ⏰ Hourly
**Source**: https://www.alberta.ca/aaip-processing-information  
**Scraper**: `scraper/scraper.py`  
**Data Collected**:
- **2025 Summary Table**: Overall program statistics
  - Nomination allocation
  - Nominations issued
  - Nomination spaces remaining
  - Applications to process
- **Draw Records Table**: Historical draw data
  - Draw date and number
  - Stream category (Alberta Opportunity, Express Entry, etc.)
  - Stream detail (subcategories)
  - Minimum score
  - Invitations issued
  - Selection parameters

**Database Tables**:
- `aaip_summary` - Overall program statistics
- `stream_data` - Individual stream tracking
- `aaip_draws` - Historical draw records
- `scrape_log` - Scraping activity logs

---

### 2. **AAIP News & Updates** ⏰ Hourly
**Source**: https://www.alberta.ca/aaip-updates  
**Scraper**: `scraper/aaip_news_scraper.py`  
**Data Collected**:
- News article title (English + Chinese translation)
- Content (English + Chinese translation)
- Published date
- Source URL

**Database Table**: `aaip_news`

**Features**:
- Automatic translation to Simplified Chinese using Google Translate
- Handles long text by splitting into chunks (4500 char limit per chunk)
- UPSERT logic to avoid duplicates (based on published_date + title_en)

---

### 3. **Federal Express Entry Draws** ⏰ Periodic
**Source**: IRCC Express Entry draw data  
**Scraper**: `scraper/express_entry_collector.py`  
**Data Collected**:
- Federal EE draw dates
- CRS cutoff scores
- Number of invitations issued
- Draw type/program

**Database Table**: `express_entry_draws`

**Purpose**: Compare federal vs. provincial pathways

---

### 4. **Alberta Economic Indicators** ⏰ Periodic
**Source**: Economic data sources  
**Scraper**: `scraper/alberta_economy_collector.py`  
**Data Collected**:
- GDP
- Unemployment rate
- Employment statistics
- Other economic indicators

**Database Table**: `alberta_economy`

---

### 5. **Labor Market Data** ⏰ Quarterly
**Source**: Labor market statistics  
**Scraper**: `scraper/quarterly_labor_market_collector.py`  
**Data Collected**:
- Employment by sector
- Wage levels
- Job openings

**Database Table**: `labor_market_data`

---

### 6. **Job Bank Data** ⏰ Periodic
**Source**: Job Bank postings  
**Scraper**: `scraper/job_bank_scraper.py`  
**Data Collected**:
- Job postings trends
- In-demand occupations
- Regional distribution

**Database Table**: `job_postings`

---

### 7. **EOI Pool Data** ⏰ Hourly (via main scraper)
**Source**: Embedded in https://www.alberta.ca/aaip-processing-information  
**Scraper**: `scraper/scraper.py` (same as #1)  
**Data Collected**:
- Expression of Interest pool statistics by stream
- Score distribution

**Database Table**: `eoi_pool_data`

---

## API Endpoints (Backend)

### News Endpoints (main_enhanced.py)
- `GET /api/news` - Get AAIP news articles
  - Parameters: `limit`, `offset`, `lang` (en/zh)
  - Returns: Paginated news with both English and Chinese content

### Draw Endpoints
- `GET /api/draws` - Historical draw records
- `GET /api/draws/latest` - Most recent draws
- `GET /api/draws/stats` - Statistics by stream
- `GET /api/draws/streams` - Available stream categories

### Summary Endpoints
- `GET /api/summary` - Historical summary data
- `GET /api/summary/latest` - Most recent summary
- `GET /api/stats` - Overall statistics

### Extended Features
- `GET /api/express-entry/comparison` - Federal vs. provincial comparison
- `GET /api/labor-market` - Labor market indicators
- `GET /api/insights/weekly` - Smart insights and trend analysis

---

## Scraping Schedule

**Systemd Timer**: `aaip-scraper.timer`  
**Frequency**: Every hour  
**Scrapers Run**:
1. `scraper/scraper.py` (main: processing info + draws + EOI pool)
2. `scraper/aaip_news_scraper.py` (news & updates)

**Manual Execution**:
```bash
# Start scraper immediately
sudo systemctl start aaip-scraper.service

# Check status
sudo systemctl status aaip-scraper.service

# View logs
sudo journalctl -u aaip-scraper.service -f
```

---

## Data Storage

**Database**: PostgreSQL  
**Location**: `aaip_data_trend_dev_db` (development) / `aaip_data` (production)

**Main Tables**:
- `aaip_summary` - Overall program stats
- `stream_data` - Stream-specific data
- `aaip_draws` - Draw records (2024-2025+)
- `aaip_news` - News articles (bilingual)
- `express_entry_draws` - Federal EE comparison
- `eoi_pool_data` - EOI pool statistics
- `alberta_economy` - Economic indicators
- `labor_market_data` - Labor market stats
- `job_postings` - Job Bank data
- `scrape_log` - Scraping activity logs

---

## Key Features

### 1. Bilingual Support
- All news content is automatically translated to Simplified Chinese
- API returns both English and Chinese versions

### 2. Data Integrity
- UNIQUE constraints prevent duplicates
- UPSERT operations for updates
- Logging of all scraping activities

### 3. Historical Data
- **2024 Data**: Imported from official PDF (September 30 - December 31, 2024)
- **2025+ Data**: Live scraping from official website
- All data preserved and accessible via API

### 4. Smart Categorization
- Automatic stream categorization (main + subcategories)
- Normalization of stream names
- Consistent data structure

---

## Frontend Integration

**Components**:
- `DrawsVisualization.jsx` - Draw history charts
- `EOIPoolVisualization.jsx` - EOI pool tracking
- `NewsUpdates.jsx` - News articles (bilingual)
- `ExpressEntryComparison.jsx` - Federal vs. provincial
- `LaborMarketInsights.jsx` - Job market data

**API Client**: `src/api.js` (uses `VITE_API_BASE_URL`)

---

## Maintenance

### Check Data Freshness
```bash
# Connect to database
sudo -u postgres psql aaip_data_trend_dev_db

# Check latest scrape
SELECT * FROM scrape_log ORDER BY timestamp DESC LIMIT 10;

# Check latest news
SELECT published_date, title_en FROM aaip_news ORDER BY published_date DESC LIMIT 5;

# Check latest draws
SELECT draw_date, stream_category, min_score FROM aaip_draws ORDER BY draw_date DESC LIMIT 5;
```

### Re-run Scraper
```bash
cd /Users/jinzhiqiang/workspaces/doit/aaip-data/scraper

# Main scraper
python3 scraper.py

# News scraper
python3 aaip_news_scraper.py

# Other collectors
python3 express_entry_collector.py
python3 alberta_economy_collector.py
python3 quarterly_labor_market_collector.py
python3 job_bank_scraper.py
```

---

## Important Notes

1. **Data Collection Frequency**: Hourly scraping ensures near real-time data updates
2. **Translation Service**: Uses Google Translate API (free tier has limits)
3. **Historical Data**: 2024 draws imported from PDF; 2025+ from live scraping
4. **Duplicate Prevention**: All scrapers use ON CONFLICT clauses to prevent duplicates
5. **Error Handling**: All errors logged to `scrape_log` table

---

## Related Documentation

- `CLAUDE.md` - Development guidelines and project overview
- `PROJECT_STRUCTURE.md` - Repository structure
- `scraper/IMPORT_2024_SUMMARY.md` - 2024 data import summary
- `API_TESTING_README.md` - API testing documentation

---

**Last Updated**: 2025-11-21  
**Maintained By**: Randy Jin
