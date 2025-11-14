# Quick Start: AAIP Draw Records Visualization

## 🚀 Quick Setup (5 minutes)

### Step 1: Update Database Schema
```bash
cd /home/randy/deploy/aaip-data
sudo -u postgres psql aaip_data < setup_db_draws.sql
```

### Step 2: Update Scraper
```bash
# Test new scraper
python3 scraper/scraper_draws.py

# Update systemd service
sudo nano /etc/systemd/system/aaip-scraper.service

# Change ExecStart line to:
# ExecStart=/usr/bin/python3 /home/randy/deploy/aaip-data/scraper/scraper_draws.py

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.service
```

### Step 3: Update Backend
```bash
# Replace main.py with new version
cp backend/main_draws.py backend/main.py

# Restart backend
sudo systemctl restart aaip-backend-test
```

### Step 4: Update Frontend
```bash
cd frontend

# Copy new files
cp src/App_with_draws.jsx src/App.jsx

# Build and deploy
npm run build
sudo cp -r dist/* /var/www/html/aaip-test/
```

### Step 5: Verify

1. **Check scraper collected data:**
```bash
sudo -u postgres psql aaip_data -c "SELECT COUNT(*) FROM aaip_draws;"
```

2. **Test API:**
```bash
curl https://aaip.randy.it.com/api/draws/streams | jq
```

3. **Check frontend:**
- Visit https://aaip.randy.it.com
- Click "Draw History" tab
- You should see charts and data!

## 📊 What's New

### New Features
- ✅ **Incremental Draw Data Collection** - Automatically collects new draws hourly
- ✅ **Interactive Charts** - Visualize min scores and invitation trends
- ✅ **Stream Filtering** - Filter by specific pathways and years
- ✅ **Statistics Dashboard** - View aggregated stats for each stream
- ✅ **Recent Draws Table** - See the latest 20 draws at a glance

### New Files Added
```
aaip-data/
├── setup_db_draws.sql          # Database schema
├── scraper/scraper_draws.py    # Enhanced scraper with draw collection
├── backend/main_draws.py       # API with draw endpoints
├── frontend/src/
│   ├── api_draws.js           # API client for draws
│   ├── App_with_draws.jsx     # Enhanced App component
│   └── components/
│       └── DrawsVisualization.jsx  # Draw visualization component
└── docs/DRAWS_VISUALIZATION.md # Complete documentation
```

## 🎯 Key API Endpoints

```bash
# Get all available streams
GET /api/draws/streams

# Get draw records (with filters)
GET /api/draws?stream_category=Alberta+Express+Entry+Stream&year=2025

# Get trend data for charts
GET /api/draws/trends?stream_category=Alberta+Express+Entry+Stream&year=2025

# Get aggregated statistics
GET /api/draws/stats
```

## 🔧 Quick Troubleshooting

### No data showing?
```bash
# Run scraper manually
python3 scraper/scraper_draws.py

# Check if data was inserted
sudo -u postgres psql aaip_data -c "SELECT * FROM aaip_draws ORDER BY draw_date DESC LIMIT 5;"
```

### API not working?
```bash
# Check backend status
sudo systemctl status aaip-backend-test

# Check logs
sudo journalctl -u aaip-backend-test -n 50
```

### Frontend not updating?
```bash
# Clear browser cache
# Or force refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

# Rebuild frontend
cd frontend && npm run build && sudo cp -r dist/* /var/www/html/aaip-test/
```

## 📈 How It Works

1. **Every hour**, the scraper:
   - Fetches the AAIP website
   - Parses the draw table
   - Saves new draws to database (skips duplicates)

2. **Frontend**:
   - User clicks "Draw History" tab
   - Loads data from API
   - Displays interactive charts and tables
   - User can filter by stream, pathway, and year

3. **Incremental Updates**:
   - Only new draws are added to database
   - Existing draws are updated if data changes
   - No duplicate records created

## 🎨 User Interface

### Draw History Tab Features
- **Filters**: Select stream category, detail, and year
- **Charts**:
  - Minimum Score Trend (line chart)
  - Invitations Issued Trend (bar + line chart)
  - Score vs Invitations (dual-axis chart)
- **Tables**:
  - Recent 20 draws
  - Stream statistics with aggregated data

### Example Use Cases
1. **Track specific pathway**: Select "Alberta Express Entry" → "Accelerated Tech Pathway"
2. **Compare years**: Switch between 2024 and 2025 to see trends
3. **View all data**: Keep "All Categories" selected to see overall trends

## 📝 Maintenance

### Check Scraper is Running
```bash
# View timer status
systemctl status aaip-scraper.timer

# View recent runs
sudo journalctl -u aaip-scraper.service -n 10
```

### Monitor Database Growth
```bash
sudo -u postgres psql aaip_data -c "
SELECT 
    COUNT(*) as total_draws,
    COUNT(DISTINCT stream_category) as streams,
    MIN(draw_date) as earliest,
    MAX(draw_date) as latest
FROM aaip_draws;
"
```

## 🎉 That's It!

You now have a fully functional draw records visualization system that:
- ✅ Automatically collects new draws
- ✅ Prevents duplicates
- ✅ Provides interactive visualizations
- ✅ Supports filtering and analysis

For detailed documentation, see [DRAWS_VISUALIZATION.md](./DRAWS_VISUALIZATION.md)

---

**Need help?** Check the logs:
```bash
# Scraper logs
sudo journalctl -u aaip-scraper.service -f

# Backend logs
sudo journalctl -u aaip-backend-test -f
```
