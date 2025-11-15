# AAIP Draw Records Visualization Feature

## 📊 Overview

This feature extends the AAIP Data Tracker with **incremental draw records collection** and **interactive data visualization**. The system automatically collects historical AAIP draw information and provides comprehensive trend analysis across different streams and pathways.

## ✨ Key Features

### 1. Incremental Data Collection
- ✅ **Automatic hourly scraping** of draw records from alberta.ca
- ✅ **Smart deduplication** - only new draws are added to database
- ✅ **Update detection** - existing draws are updated if data changes
- ✅ **Reliable logging** - tracks collection status and new records added

### 2. Interactive Data Visualization
- ✅ **Multiple chart types** for trend analysis
- ✅ **Stream filtering** - view specific pathways and sectors
- ✅ **Year-based filtering** - compare historical trends
- ✅ **Detailed statistics** - aggregated data for each stream
- ✅ **Recent draws table** - quick view of latest 20 draws

### 3. Comprehensive API
- ✅ **RESTful endpoints** for draw data access
- ✅ **Flexible filtering** by stream, date, year
- ✅ **Aggregated statistics** for analysis
- ✅ **Stream discovery** - list all available streams

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│  • Nomination Summary Tab (existing)                         │
│  • Draw History Tab (NEW)                                   │
│    - Stream filters                                          │
│    - Year selector                                           │
│    - Interactive charts                                      │
│    - Data tables                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/JSON
┌──────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend                          │
│  • /api/draws - Get draw records                            │
│  • /api/draws/streams - List streams                        │
│  • /api/draws/trends - Trend data                           │
│  • /api/draws/stats - Statistics                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ PostgreSQL
┌──────────────────────▼──────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  • aaip_draws - Historical draw records                     │
│  • Unique constraint prevents duplicates                    │
│  • Indexes for fast queries                                 │
└──────────────────────▲──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   Scraper (Cron Job)                         │
│  • Runs every hour via systemd timer                        │
│  • Parses alberta.ca draw table                             │
│  • Categorizes streams automatically                        │
│  • Inserts/updates database                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📁 New Files

```
aaip-data/
├── setup_db_draws.sql                  # Database schema for draws
├── scraper/
│   └── scraper_draws.py               # Enhanced scraper with draw collection
├── backend/
│   └── main_draws.py                  # API with draw endpoints
├── frontend/src/
│   ├── api_draws.js                   # Draw data API client
│   ├── App_with_draws.jsx             # Enhanced App with tabs
│   └── components/
│       └── DrawsVisualization.jsx     # Draw visualization component
├── test_draws_feature.py              # Comprehensive test suite
└── docs/
    ├── DRAWS_VISUALIZATION.md         # Complete documentation
    └── DRAWS_QUICKSTART.md           # Quick setup guide
```

## 🚀 Quick Start

### Prerequisites
- Existing AAIP Data Tracker installation
- PostgreSQL database
- Python 3.7+
- Node.js 16+

### Installation (5 minutes)

```bash
# 1. Navigate to project directory
cd /path/to/aaip-data

# 2. Update database schema
sudo -u postgres psql aaip_data < setup_db_draws.sql

# 3. Install Python dependencies (if needed)
cd scraper
pip install -r requirements.txt

# 4. Test scraper
python3 scraper_draws.py

# 5. Update systemd service
sudo nano /etc/systemd/system/aaip-scraper.service
# Change ExecStart to: /usr/bin/python3 /path/to/scraper_draws.py

# 6. Reload and restart services
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.service
sudo systemctl restart aaip-backend-test

# 7. Build and deploy frontend
cd frontend
npm run build
sudo cp -r dist/* /var/www/html/aaip-test/
```

### Verification

```bash
# Run test suite
python3 test_draws_feature.py

# Check API
curl https://aaip.randy.it.com/api/draws/streams | jq

# Visit frontend
open https://aaip.randy.it.com
# Click "Draw History" tab
```

## 📊 Data Model

### Draw Record Schema

```sql
CREATE TABLE aaip_draws (
    id SERIAL PRIMARY KEY,
    draw_date DATE NOT NULL,
    draw_number VARCHAR(50),
    stream_category TEXT NOT NULL,      -- e.g., "Alberta Express Entry Stream"
    stream_detail TEXT,                 -- e.g., "Accelerated Tech Pathway"
    min_score INTEGER,
    invitations_issued INTEGER,
    applications_received INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(draw_date, stream_category, stream_detail)
);
```

### Stream Categories

The system automatically categorizes draws into:

**Main Categories:**
- Alberta Opportunity Stream
- Alberta Express Entry Stream
- Dedicated Health Care Pathway
- Tourism and Hospitality Stream
- Rural Renewal Stream

**Pathways/Details:**
- Accelerated Tech Pathway
- Law Enforcement Pathway
- Construction
- Agriculture
- Aviation
- Health Care
- And more...

## 📡 API Documentation

### Core Endpoints

#### GET `/api/stats`
Get overall statistics including draw counts
```json
{
  "total_records": 1234,
  "total_draws": 567,
  "latest_draw_date": "2025-10-29"
}
```

#### GET `/api/draws`
Get draw records with optional filters
```bash
# All draws
GET /api/draws?limit=100

# Filter by stream
GET /api/draws?stream_category=Alberta+Express+Entry+Stream

# Filter by date range
GET /api/draws?start_date=2025-01-01&end_date=2025-12-31
```

#### GET `/api/draws/streams`
List all available streams
```json
{
  "categories": ["Alberta Opportunity Stream", ...],
  "streams": [
    {"category": "Alberta Express Entry Stream", "detail": "Accelerated Tech Pathway"},
    ...
  ]
}
```

#### GET `/api/draws/trends`
Get trend data for charts
```bash
GET /api/draws/trends?stream_category=Alberta+Express+Entry+Stream&year=2025
```

#### GET `/api/draws/stats`
Get aggregated statistics
```json
[
  {
    "stream_category": "Alberta Express Entry Stream",
    "stream_detail": "Accelerated Tech Pathway",
    "total_draws": 25,
    "total_invitations": 2500,
    "avg_score": 62.4,
    "min_score": 52,
    "max_score": 73
  },
  ...
]
```

## 🎨 User Interface

### Draw History Tab

**Features:**
1. **Filter Panel**
   - Stream category dropdown
   - Pathway/sector dropdown
   - Year selector

2. **Statistics Cards**
   - Total draws
   - Total invitations
   - Average minimum score
   - Score range

3. **Interactive Charts**
   - **Minimum Score Trend** - Line chart showing score changes over time
   - **Invitations Trend** - Bar + line chart showing invitation volumes
   - **Combined View** - Dual-axis chart comparing scores vs invitations

4. **Data Tables**
   - **Recent Draws** - Latest 20 draws with details
   - **Stream Statistics** - Aggregated data for all streams

### Example Workflows

**Track Specific Stream:**
1. Select "Alberta Express Entry Stream" from category dropdown
2. Select "Accelerated Tech Pathway" from detail dropdown
3. View historical trends for that specific pathway

**Compare Years:**
1. Select a stream
2. Switch between 2024 and 2025 in year selector
3. Observe score and invitation trends

**View All Data:**
1. Keep "All Categories" selected
2. See overall AAIP draw trends

## 🔄 Data Flow

### Incremental Collection Process

```
┌────────────────────────────────────────────────────────┐
│                  Hourly Trigger                         │
│              (systemd timer)                            │
└──────────────────┬─────────────────────────────────────┘
                   ▼
┌────────────────────────────────────────────────────────┐
│              Scraper Execution                          │
│  1. Fetch alberta.ca draw table                        │
│  2. Parse HTML and extract draw records                │
│  3. Categorize streams (main + detail)                 │
└──────────────────┬─────────────────────────────────────┘
                   ▼
┌────────────────────────────────────────────────────────┐
│          Check Against Database                         │
│  • Calculate unique key (date + category + detail)     │
│  • Query existing records                              │
└──────────────────┬─────────────────────────────────────┘
                   ▼
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────┐    ┌──────────────┐
│  New Draw    │    │Existing Draw │
└──────┬───────┘    └──────┬───────┘
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ INSERT       │    │ UPDATE       │
│ New record   │    │ (if changed) │
└──────┬───────┘    └──────┬───────┘
       └─────────┬──────────┘
                 ▼
┌────────────────────────────────────────────────────────┐
│               Database Updated                          │
│  • Log result (new draws added)                        │
│  • Update scrape_log table                             │
└────────────────────────────────────────────────────────┘
```

## 🧪 Testing

### Automated Test Suite

```bash
# Run comprehensive tests
python3 test_draws_feature.py
```

**Tests:**
- ✅ Database schema validation
- ✅ Data integrity checks
- ✅ API endpoint functionality
- ✅ Scraper file existence
- ✅ Service status verification

### Manual Testing

```bash
# Test scraper
python3 scraper/scraper_draws.py

# Test API endpoints
curl https://aaip.randy.it.com/api/draws | jq
curl https://aaip.randy.it.com/api/draws/streams | jq

# Check database
sudo -u postgres psql aaip_data -c "SELECT COUNT(*) FROM aaip_draws;"

# View recent draws
sudo -u postgres psql aaip_data -c "
SELECT draw_date, stream_category, stream_detail, min_score, invitations_issued 
FROM aaip_draws 
ORDER BY draw_date DESC 
LIMIT 10;
"
```

## 📈 Monitoring

### Check System Health

```bash
# Scraper status
systemctl status aaip-scraper.timer
systemctl list-timers | grep aaip

# Recent scraper runs
sudo journalctl -u aaip-scraper.service -n 20

# Backend status
systemctl status aaip-backend-test

# Database stats
sudo -u postgres psql aaip_data -c "
SELECT 
    COUNT(*) as total_draws,
    COUNT(DISTINCT stream_category) as categories,
    MIN(draw_date) as earliest,
    MAX(draw_date) as latest
FROM aaip_draws;
"
```

## 🔧 Troubleshooting

### No data showing?
```bash
# Run scraper manually
python3 scraper/scraper_draws.py

# Check if data exists
sudo -u postgres psql aaip_data -c "SELECT COUNT(*) FROM aaip_draws;"
```

### API errors?
```bash
# Check backend logs
sudo journalctl -u aaip-backend-test -n 50

# Restart backend
sudo systemctl restart aaip-backend-test
```

### Charts not loading?
1. Clear browser cache (Ctrl+Shift+R)
2. Check browser console for errors
3. Verify API is responding: `curl https://aaip.randy.it.com/api/draws/streams`

## 📚 Documentation

- **[DRAWS_VISUALIZATION.md](./docs/DRAWS_VISUALIZATION.md)** - Complete technical documentation
- **[DRAWS_QUICKSTART.md](./docs/DRAWS_QUICKSTART.md)** - 5-minute setup guide
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - General deployment guide
- **[CLAUDE.md](./docs/CLAUDE.md)** - Development notes

## 🎯 Future Enhancements

### Planned Features
- [ ] Email notifications for new draws
- [ ] Predictive analytics using machine learning
- [ ] Multi-stream comparison view
- [ ] Export charts as images/PDF
- [ ] Mobile app with push notifications
- [ ] Advanced filtering (score range, date picker)
- [ ] Historical data import from PDFs

### Contribution Ideas
- Add more chart types (scatter, area)
- Implement real-time updates (WebSocket)
- Add data export functionality
- Create public API documentation
- Build mobile-responsive layouts

## 📞 Support

**Issues:**
1. Check this documentation
2. Run test suite: `python3 test_draws_feature.py`
3. Check logs: `sudo journalctl -u aaip-backend-test -u aaip-scraper.service`
4. Review [DRAWS_VISUALIZATION.md](./docs/DRAWS_VISUALIZATION.md)

**Common Issues:**
- No data → Run scraper manually
- API errors → Check backend logs and restart service
- Charts not loading → Clear cache and check API responses

## 📝 License

This project is part of the AAIP Data Tracker system.
MIT License - See main README for details.

## 👥 Credits

- **Original System**: AAIP Data Tracker Team
- **Draw Visualization Feature**: Implemented November 2025
- **Data Source**: [Alberta.ca AAIP Processing Information](https://www.alberta.ca/aaip-processing-information)

---

**Version:** 2.0.0  
**Last Updated:** November 14, 2025  
**Status:** Production Ready ✅
