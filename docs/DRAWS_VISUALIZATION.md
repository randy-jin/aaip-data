# AAIP Draw Records Visualization - Complete Implementation Guide

## 📋 Overview

This document describes the complete implementation of the AAIP draw records collection and visualization feature. The system incrementally collects historical draw data and provides interactive visualizations showing trends across different streams and pathways.

## 🏗️ System Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                         │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │   App.jsx    │  │ DrawsVisualization│  │ Tab Navigation│   │
│  │  (Main UI)   │──│    Component      │──│   & Filters   │   │
│  └──────────────┘  └─────────────────┘  └───────────────┘   │
│         │                  │                                  │
│         └──────────────────┴──────────────────────────────┐  │
└────────────────────────────────────────────────────────────┼──┘
                                                              │
                                                              ▼
┌────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                      │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ /api/draws   │  │/api/draws/  │  │/api/draws/       │  │
│  │              │  │  streams    │  │  trends          │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┴────────┐   │
└─────────────────────────────────────────────────────────┼───┘
                                                           │
                                                           ▼
┌──────────────────────────────────────────────────────────┐
│              PostgreSQL Database                          │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐│
│  │ aaip_draws   │  │ aaip_summary│  │  scrape_log      ││
│  │ (draw records)│  │ (nominations│  │  (tracking)      ││
│  └──────────────┘  └─────────────┘  └──────────────────┘│
└──────────────────────────────────────────────────────────┘
                           ▲
                           │
┌──────────────────────────┴────────────────────────────────┐
│            Scraper (Python - Cron Job)                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  scraper_draws.py - Incremental Data Collection      │ │
│  │  • Fetches draw table from alberta.ca                │ │
│  │  • Parses and categorizes streams                    │ │
│  │  • Deduplicates and saves to database                │ │
│  └──────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

## 📊 Database Schema

### New Table: `aaip_draws`

```sql
CREATE TABLE aaip_draws (
    id SERIAL PRIMARY KEY,
    draw_date DATE NOT NULL,
    draw_number VARCHAR(50),
    stream_category TEXT NOT NULL,
    stream_detail TEXT,
    min_score INTEGER,
    invitations_issued INTEGER,
    applications_received INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(draw_date, stream_category, stream_detail)
);
```

**Key Features:**
- `UNIQUE` constraint prevents duplicate draws
- `updated_at` tracks when records are modified
- Indexed on `draw_date` and `stream_category` for fast queries

## 🔄 Incremental Data Collection

### How It Works

1. **Scraper runs hourly** (via cron/systemd timer)
2. **Fetches draw table** from alberta.ca
3. **Parses each row** and categorizes streams
4. **Uses `INSERT ... ON CONFLICT`** to handle duplicates:
   - New draws → inserted
   - Existing draws → updated if data changed
5. **Logs results** including count of new draws added

### Stream Categorization Logic

The scraper automatically categorizes streams into:

- **Main Categories:**
  - Alberta Opportunity Stream
  - Alberta Express Entry Stream
  - Dedicated Health Care Pathway
  - Tourism and Hospitality Stream
  - Rural Renewal Stream

- **Details/Pathways:**
  - Accelerated Tech Pathway
  - Law Enforcement Pathway
  - Priority Sectors (Construction, Agriculture, Aviation, Health Care)
  - Specific sectors for Alberta Opportunity Stream

### Example Data Flow

```
AAIP Website Draw Table:
┌──────────────┬──────────────────────────────┬──────────┬──────────┐
│   Draw Date  │       Stream Description     │ Min Score│ Invites  │
├──────────────┼──────────────────────────────┼──────────┼──────────┤
│ Oct 29, 2025 │ Alberta Express Entry - Tech │    60    │    89    │
└──────────────┴──────────────────────────────┴──────────┴──────────┘
                            ↓
                      Scraper Parses
                            ↓
┌────────────────────────────────────────────────────────────────────┐
│ stream_category: "Alberta Express Entry Stream"                    │
│ stream_detail: "Accelerated Tech Pathway"                          │
│ draw_date: 2025-10-29                                              │
│ min_score: 60                                                      │
│ invitations_issued: 89                                             │
└────────────────────────────────────────────────────────────────────┘
                            ↓
                   Check if exists in DB
                            ↓
            ┌───────────────┴────────────────┐
            │                                │
         New Draw                      Existing Draw
            │                                │
         INSERT                         UPDATE (if changed)
            │                                │
            └────────────────┬───────────────┘
                            ↓
                    Database Updated
```

## 🎨 Frontend Visualization

### Features

1. **Interactive Filters:**
   - Stream category selector
   - Pathway/sector detail selector
   - Year selector

2. **Multiple Chart Types:**
   - **Line Chart**: Minimum score trends over time
   - **Bar + Line Chart**: Invitation counts with trend line
   - **Dual-Axis Chart**: Score vs invitations comparison

3. **Data Tables:**
   - Recent draws table (20 most recent)
   - Stream statistics table (aggregated data)

4. **Statistics Cards:**
   - Total draws
   - Total invitations
   - Average minimum score
   - Score range

### User Flow

```
User lands on page
       ↓
Sees two tabs: "Nomination Summary" | "Draw History"
       ↓
Clicks "Draw History" tab
       ↓
System loads draw data from API
       ↓
User sees:
  • Statistics cards
  • Filter dropdowns (Category, Detail, Year)
  • Three interactive charts
  • Recent draws table
  • Stream statistics table
       ↓
User selects specific stream (e.g., "Alberta Express Entry")
       ↓
Dropdown updates to show available pathways
       ↓
User selects "Accelerated Tech Pathway"
       ↓
Charts update to show filtered data
       ↓
User hovers over data points → sees detailed tooltip
```

## 🚀 Deployment Instructions

### 1. Database Setup

```bash
# Connect to PostgreSQL
sudo -u postgres psql aaip_data

# Run the draws schema
\i /path/to/aaip-data/setup_db_draws.sql
```

### 2. Backend Setup

```bash
cd /path/to/aaip-data/backend

# Update main file (or use main_draws.py)
# The new API endpoints are backward compatible

# Restart backend service
sudo systemctl restart aaip-backend-test
```

### 3. Scraper Setup

```bash
cd /path/to/aaip-data/scraper

# Test the new scraper
python3 scraper_draws.py

# Update systemd service to use new scraper
sudo systemctl edit aaip-scraper.service

# Update ExecStart line:
# ExecStart=/usr/bin/python3 /home/randy/deploy/aaip-data/scraper/scraper_draws.py

# Restart scraper
sudo systemctl restart aaip-scraper.service
```

### 4. Frontend Setup

```bash
cd /path/to/aaip-data/frontend

# Copy new files
cp src/App_with_draws.jsx src/App.jsx
cp src/api_draws.js src/api_draws.js

# Build
npm run build

# Deploy
sudo cp -r dist/* /var/www/html/aaip-test/
```

## 📡 API Endpoints

### Draw Data Endpoints

#### `GET /api/draws`
Get draw records with optional filtering

**Query Parameters:**
- `limit` (int): Maximum records to return (default: 100)
- `offset` (int): Pagination offset (default: 0)
- `stream_category` (string): Filter by category
- `stream_detail` (string): Filter by detail/pathway
- `start_date` (string): Filter draws after date (YYYY-MM-DD)
- `end_date` (string): Filter draws before date (YYYY-MM-DD)

**Example:**
```bash
curl "https://aaip.randy.it.com/api/draws?stream_category=Alberta%20Express%20Entry%20Stream&limit=50"
```

#### `GET /api/draws/streams`
Get list of all available streams and categories

**Response:**
```json
{
  "categories": [
    "Alberta Opportunity Stream",
    "Alberta Express Entry Stream",
    ...
  ],
  "streams": [
    {
      "category": "Alberta Express Entry Stream",
      "detail": "Accelerated Tech Pathway"
    },
    ...
  ]
}
```

#### `GET /api/draws/trends`
Get draw trend data for visualization

**Query Parameters:**
- `stream_category` (string): Filter by category
- `stream_detail` (string): Filter by detail
- `year` (int): Filter by year (e.g., 2025)
- `limit` (int): Maximum records (default: 365)

**Response:**
```json
[
  {
    "date": "2025-10-29",
    "min_score": 60,
    "invitations": 89,
    "stream_category": "Alberta Express Entry Stream",
    "stream_detail": "Accelerated Tech Pathway"
  },
  ...
]
```

#### `GET /api/draws/stats`
Get aggregated statistics for each stream

**Query Parameters:**
- `stream_category` (string, optional): Filter by category

**Response:**
```json
[
  {
    "stream_category": "Alberta Express Entry Stream",
    "stream_detail": "Accelerated Tech Pathway",
    "total_draws": 25,
    "total_invitations": 2500,
    "avg_score": 62.4,
    "min_score": 52,
    "max_score": 73,
    "latest_draw_date": "2025-10-29",
    "earliest_draw_date": "2025-01-15"
  },
  ...
]
```

## 🧪 Testing

### Manual Testing Checklist

#### Database Tests
```bash
# 1. Check if draws table exists
psql -U randy -d aaip_data -c "SELECT COUNT(*) FROM aaip_draws;"

# 2. Check latest draws
psql -U randy -d aaip_data -c "SELECT * FROM aaip_draws ORDER BY draw_date DESC LIMIT 5;"

# 3. Check stream categories
psql -U randy -d aaip_data -c "SELECT DISTINCT stream_category FROM aaip_draws;"
```

#### Scraper Tests
```bash
# 1. Run scraper manually
cd /path/to/aaip-data/scraper
python3 scraper_draws.py

# Expected output:
# ✓ Summary data saved
# ✓ Scraped X draw records
# ✓ Processed X records, Y new records added

# 2. Verify duplicate handling
python3 scraper_draws.py  # Run again
# Should show: "Processed X records, 0 new records added"
```

#### API Tests
```bash
# 1. Test stats endpoint
curl https://aaip.randy.it.com/api/stats | jq

# 2. Test draws endpoint
curl https://aaip.randy.it.com/api/draws?limit=5 | jq

# 3. Test streams endpoint
curl https://aaip.randy.it.com/api/draws/streams | jq

# 4. Test trends endpoint
curl "https://aaip.randy.it.com/api/draws/trends?year=2025&limit=10" | jq
```

#### Frontend Tests
1. Navigate to https://aaip.randy.it.com
2. Click "Draw History" tab
3. Verify statistics cards display correctly
4. Select different stream categories
5. Verify charts update correctly
6. Check table data displays properly
7. Test year selector
8. Verify tooltips show on chart hover

### Automated Testing

```python
# Test draw categorization
def test_categorize_stream():
    from scraper_draws import categorize_stream
    
    tests = [
        ("Alberta Express Entry Stream – Accelerated Tech Pathway", 
         "Alberta Express Entry Stream", "Accelerated Tech Pathway"),
        ("Alberta Opportunity Stream – Construction",
         "Alberta Opportunity Stream", "Construction"),
    ]
    
    for input_text, expected_category, expected_detail in tests:
        category, detail = categorize_stream(input_text)
        assert category == expected_category
        assert detail == expected_detail
```

## 🔧 Troubleshooting

### Common Issues

#### 1. No draw data showing in frontend

**Check:**
```bash
# 1. Verify data in database
psql -U randy -d aaip_data -c "SELECT COUNT(*) FROM aaip_draws;"

# 2. Check API response
curl https://aaip.randy.it.com/api/draws | jq

# 3. Check browser console for errors
# Open browser DevTools → Console tab
```

**Solution:** Run scraper manually to populate data

#### 2. Scraper fails to parse draws

**Check logs:**
```bash
sudo journalctl -u aaip-scraper.service -n 50
```

**Common causes:**
- Website structure changed
- Network timeout
- Database connection issues

**Solution:** Check error message and adjust parsing logic in `scraper_draws.py`

#### 3. Duplicate draws being created

**Check uniqueness constraint:**
```bash
psql -U randy -d aaip_data -c "
SELECT draw_date, stream_category, stream_detail, COUNT(*) 
FROM aaip_draws 
GROUP BY draw_date, stream_category, stream_detail 
HAVING COUNT(*) > 1;
"
```

**Solution:** Recreate unique constraint if missing

#### 4. Charts not displaying

**Check:**
1. Browser console for JavaScript errors
2. API responses contain data
3. Date format is correct (ISO 8601)

**Solution:** Clear browser cache and rebuild frontend

## 📈 Performance Optimization

### Database Indexes

Already created by schema:
- `idx_draws_date` - Fast date range queries
- `idx_draws_category` - Fast category filtering
- `idx_draws_category_date` - Combined queries

### API Caching

Consider adding caching for frequently accessed data:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_cached_trends(stream_category, year):
    # Cache for 1 hour
    return get_draw_trends(stream_category=stream_category, year=year)
```

### Frontend Optimization

- Data fetched once per tab switch
- Charts rendered only when data changes
- Pagination for large datasets

## 🔐 Security Considerations

1. **SQL Injection Prevention:** All queries use parameterized statements
2. **Input Validation:** API validates all query parameters
3. **Rate Limiting:** Consider adding rate limiting for API endpoints
4. **CORS:** Configure specific origins in production

## 📝 Maintenance

### Regular Tasks

1. **Weekly:** Check scraper logs for errors
2. **Monthly:** Review database size and performance
3. **Quarterly:** Update stream categorization if AAIP adds new programs

### Monitoring

```bash
# Check scraper status
systemctl status aaip-scraper.timer
systemctl list-timers | grep aaip

# Check last successful run
sudo journalctl -u aaip-scraper.service -n 1 --output=cat | grep "completed successfully"

# Check database growth
psql -U randy -d aaip_data -c "
SELECT 
    COUNT(*) as total_draws,
    MIN(draw_date) as earliest,
    MAX(draw_date) as latest,
    COUNT(DISTINCT stream_category) as categories
FROM aaip_draws;
"
```

## 📚 Additional Resources

- [Alberta AAIP Official Site](https://www.alberta.ca/aaip-processing-information)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Recharts Documentation](https://recharts.org/)
- [PostgreSQL UPSERT Documentation](https://www.postgresql.org/docs/current/sql-insert.html)

## 🎯 Future Enhancements

### Potential Features

1. **Email Notifications**
   - Alert users when new draws are published
   - Notify when score drops below threshold

2. **Predictive Analytics**
   - Forecast future draw scores using ML
   - Predict invitation volumes

3. **Comparison Tools**
   - Compare multiple streams side-by-side
   - Year-over-year comparisons

4. **Export Functionality**
   - Export charts as images
   - Download data as CSV/Excel

5. **Advanced Filtering**
   - Filter by score range
   - Filter by invitation count range
   - Date range picker

6. **Mobile App**
   - Native iOS/Android apps
   - Push notifications for new draws

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review logs: `sudo journalctl -u aaip-backend-test -u aaip-scraper.service`
3. Check GitHub Issues (if applicable)
4. Contact system administrator

---

**Version:** 2.0.0  
**Last Updated:** November 14, 2025  
**Author:** AAIP Data Tracker Team
