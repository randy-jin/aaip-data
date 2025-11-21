# AAIP Data Collection Automation Setup

## Overview

The AAIP data collection system automatically collects data from multiple sources every hour:

1. **AAIP Processing Info & Draw Records** - https://www.alberta.ca/aaip-processing-information
2. **AAIP News Updates** - https://www.alberta.ca/aaip-updates
3. **Express Entry Comparison Data** - Federal EE draws
4. **Alberta Economy Indicators** - Provincial economic data
5. **Labor Market Data** - Employment and wage statistics
6. **Job Bank Postings** - Job posting trends
7. **Trend Analysis Engine** - Historical pattern analysis

## Orchestrator Script

The main orchestrator script `collect_all_data.py` runs all data collectors in sequence and provides:

- ✅ Automatic execution of all collectors
- ⏱️ Timeout protection (5 minutes per collector)
- 📊 Detailed logging and progress reporting
- 🛡️ Critical failure handling (stops if main scraper fails)
- 📈 Summary statistics after each run

## Setup Methods

### Method 1: Systemd Timer (Recommended for Linux Servers)

**1. Copy service files to systemd directory:**

```bash
sudo cp deployment/aaip-scraper.service /etc/systemd/system/
sudo cp deployment/aaip-scraper.timer /etc/systemd/system/
```

**2. Update the service file with correct paths:**

Edit `/etc/systemd/system/aaip-scraper.service` and update:
- `User=` and `Group=` (your username)
- `WorkingDirectory=` (path to scraper directory)
- `Environment="PATH=..."` (path to your Python venv)
- `Environment="DATABASE_URL=..."` (your database connection)

**3. Enable and start the timer:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable timer (starts automatically on boot)
sudo systemctl enable aaip-scraper.timer

# Start timer immediately
sudo systemctl start aaip-scraper.timer

# Check timer status
sudo systemctl status aaip-scraper.timer
sudo systemctl list-timers | grep aaip
```

**4. Manual trigger (for testing):**

```bash
# Run scraper immediately
sudo systemctl start aaip-scraper.service

# Check logs
sudo journalctl -u aaip-scraper.service -f
```

### Method 2: Cron (Alternative for Systems Without Systemd)

**1. Create a cron wrapper script:**

```bash
cd scraper
cat > run_collector_cron.sh << 'EOF'
#!/bin/bash
# AAIP Data Collection Cron Wrapper

# Change to scraper directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set database connection
export DATABASE_URL="postgresql://user:password@host:port/dbname"

# Run the orchestrator
python3 collect_all_data.py >> /var/log/aaip-collector.log 2>&1
EOF

chmod +x run_collector_cron.sh
```

**2. Add to crontab:**

```bash
# Edit crontab
crontab -e

# Add this line to run every hour at :00
0 * * * * /path/to/aaip-data/scraper/run_collector_cron.sh

# Or run every hour at :05 past the hour
5 * * * * /path/to/aaip-data/scraper/run_collector_cron.sh
```

**3. View cron logs:**

```bash
tail -f /var/log/aaip-collector.log
```

### Method 3: Manual Execution (Development/Testing)

```bash
cd scraper

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Set database connection
export DATABASE_URL="postgresql://user:password@host:port/dbname"

# Run all collectors
python3 collect_all_data.py
```

## Individual Collector Scripts

You can also run individual collectors manually:

```bash
cd scraper
source venv/bin/activate

# Main AAIP scraper (processing info + draws)
python3 scraper.py

# News scraper
python3 aaip_news_scraper.py

# Express Entry comparison
python3 express_entry_collector.py

# Alberta economy data
python3 alberta_economy_collector.py

# Labor market data
python3 quarterly_labor_market_collector.py

# Job Bank data
python3 job_bank_scraper.py

# Trend analysis
python3 trend_analysis_engine.py
```

## Monitoring

### Check Systemd Timer Status

```bash
# View timer schedule
sudo systemctl list-timers aaip-scraper.timer

# Check service status
sudo systemctl status aaip-scraper.service

# View recent logs
sudo journalctl -u aaip-scraper.service -n 50

# Follow logs in real-time
sudo journalctl -u aaip-scraper.service -f
```

### Check Database for Recent Data

```bash
# Connect to database
psql -h host -U user -d aaip_data_trend_dev_db

# Check recent scrapes
SELECT * FROM scrape_log ORDER BY timestamp DESC LIMIT 10;

# Check recent AAIP data
SELECT * FROM aaip_summary ORDER BY timestamp DESC LIMIT 5;

# Check recent draw records
SELECT * FROM aaip_draws ORDER BY draw_date DESC LIMIT 10;

# Check recent news
SELECT published_date, title_en FROM aaip_news ORDER BY published_date DESC LIMIT 10;
```

## Troubleshooting

### Collectors Failing

1. **Check database connection:**
   ```bash
   # Test connection
   psql -h host -U user -d dbname -c "SELECT 1;"
   ```

2. **Check Python dependencies:**
   ```bash
   cd scraper
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Check permissions:**
   ```bash
   # Ensure user can write to log files
   ls -la /var/log/aaip-*.log
   ```

4. **Run manually to see errors:**
   ```bash
   cd scraper
   python3 collect_all_data.py
   ```

### Timer Not Running

```bash
# Check if timer is enabled
sudo systemctl is-enabled aaip-scraper.timer

# Check if timer is active
sudo systemctl is-active aaip-scraper.timer

# Restart timer
sudo systemctl restart aaip-scraper.timer
```

### Missing Dependencies

```bash
cd scraper
pip install -r requirements.txt

# Key dependencies:
pip install requests beautifulsoup4 psycopg2-binary python-dotenv deep-translator
```

## Configuration

### Environment Variables

Create `.env` file in `scraper/` directory:

```env
# Database connection (required)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Or individual parameters:
DB_HOST=host
DB_PORT=5432
DB_NAME=aaip_data_trend_dev_db
DB_USER=username
DB_PASSWORD=password
```

### Collector Schedule

Default: **Every hour at :00 minutes**

To change frequency, edit `deployment/aaip-scraper.timer`:

```ini
[Timer]
# Run every hour
OnCalendar=hourly

# Run every 2 hours
# OnCalendar=*-*-* 0/2:00:00

# Run every 30 minutes
# OnCalendar=*:0/30

# Run daily at 2 AM
# OnCalendar=daily
# OnCalendar=*-*-* 02:00:00
```

After changes, reload systemd:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.timer
```

## Deployment Workflow

When deploying to server (via GitHub Actions):

```bash
# 1. Pull latest code
cd /home/randy/deploy/aaip-data
git pull origin test

# 2. Update dependencies
cd scraper
source venv/bin/activate
pip install -r requirements.txt

# 3. Restart systemd service (if needed)
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.timer

# 4. Verify timer is running
sudo systemctl status aaip-scraper.timer
```

## Data Collection Schedule Summary

| Collector | Frequency | Critical | Timeout |
|-----------|-----------|----------|---------|
| AAIP Processing & Draws | Hourly | ✅ Yes | 5 min |
| News Updates | Hourly | ❌ No | 5 min |
| Express Entry | Hourly | ❌ No | 5 min |
| Alberta Economy | Hourly | ❌ No | 5 min |
| Labor Market | Hourly | ❌ No | 5 min |
| Job Bank | Hourly | ❌ No | 5 min |
| Trend Analysis | Hourly | ❌ No | 5 min |

**Total maximum time per run:** ~35 minutes (7 collectors × 5 min timeout)
**Expected typical time:** ~2-5 minutes

## Benefits of Automated Collection

✅ **Real-time updates** - Data refreshed every hour
✅ **No manual intervention** - Runs automatically
✅ **Historical tracking** - Builds comprehensive time-series data
✅ **Trend detection** - Analysis engine identifies patterns
✅ **Multi-source integration** - Combines AAIP, federal, and economic data
✅ **Fault tolerance** - Non-critical failures don't stop execution
✅ **Comprehensive logging** - Full audit trail of all collections
