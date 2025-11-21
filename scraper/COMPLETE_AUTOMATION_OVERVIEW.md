# Automated Data Collection - Complete Overview

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      AAIP Data Collection System                         │
│                     Fully Automated with Systemd                         │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────┐          ┌───────────────────────────────┐
│    MAIN PIPELINE           │          │   EXTENDED PIPELINE           │
│    (Hourly - Critical)     │          │   (Daily - Supplementary)     │
├────────────────────────────┤          ├───────────────────────────────┤
│ ✅ AAIP Processing Info    │          │ ✅ Express Entry (Federal)    │
│ ✅ AAIP Draw Records       │          │ ✅ Alberta Economy            │
│ ✅ AAIP News & Updates     │          │ ✅ Labor Market Data          │
│ ✅ Trend Analysis          │          │ ✅ Job Bank Postings          │
├────────────────────────────┤          ├───────────────────────────────┤
│ Timer: aaip-scraper.timer  │          │ Timer: aaip-extended-        │
│ Frequency: Every hour      │          │        collectors.timer       │
│ Run at: :00 past hour      │          │ Frequency: Once daily         │
│ Orchestrator:              │          │ Run at: 3:00 AM               │
│   collect_all_data.py      │          │ Orchestrator:                 │
│                            │          │   collect_extended_data.py    │
└────────────────────────────┘          └───────────────────────────────┘
              │                                        │
              └────────────┬───────────────────────────┘
                           ▼
                  ┌─────────────────────┐
                  │   PostgreSQL DB     │
                  │  aaip_data_trend    │
                  │     _dev_db         │
                  └─────────────────────┘
```

## 🎯 Data Sources & Collection Frequency

### Main Pipeline (Hourly)

| Data Source | URL | Frequency | Purpose | Critical? |
|-------------|-----|-----------|---------|-----------|
| **AAIP Processing Info** | https://www.alberta.ca/aaip-processing-information | Hourly | Allocation, applications, remaining quotas | ✅ YES |
| **AAIP Draw Records** | Same as above | Hourly | Historical draws, scores, invitations | ✅ YES |
| **AAIP News & Updates** | https://www.alberta.ca/aaip-updates | Hourly | Program updates with Chinese translation | ⚠️ Important |
| **Trend Analysis** | N/A (internal) | Hourly | Pattern detection and insights | ⚠️ Important |

### Extended Pipeline (Daily at 3 AM)

| Data Source | URL | Frequency | Purpose | Critical? |
|-------------|-----|-----------|---------|-----------|
| **Express Entry** | https://www.canada.ca/en/immigration-refugees-citizenship/corporate/mandate/policies-operational-instructions-agreements/ministerial-instructions/express-entry-rounds.html | Daily | Federal vs. AAIP comparison | ❌ No |
| **Alberta Economy** | Statistics Canada APIs | Daily | GDP, unemployment, population | ❌ No |
| **Labor Market** | Alberta LMI sources | Daily* | Employment, wages, vacancies | ❌ No |
| **Job Bank** | https://www.jobbank.gc.ca | Daily | Job posting trends by NOC | ❌ No |

*Labor market collector checks internally if it's a new quarter before collecting

## 🚀 Quick Start Guide

### For Local Development/Testing

```bash
cd /Users/jinzhiqiang/workspaces/doit/aaip-data/scraper

# Test main pipeline (critical data)
python3 collect_all_data.py --verbose

# Test extended pipeline (supplementary data)
python3 collect_extended_data.py --verbose

# Test specific extended collector
python3 collect_extended_data.py --collector express_entry -v
python3 collect_extended_data.py --collector alberta_economy -v
python3 collect_extended_data.py --collector labor_market -v
python3 collect_extended_data.py --collector job_bank -v

# Test individual scrapers directly
python3 scraper.py                           # Main AAIP scraper
python3 aaip_news_scraper.py                 # News scraper
python3 express_entry_collector.py           # Express Entry
```

### For Production Server

#### 1. Main Pipeline (Already Deployed)

```bash
# Check status
sudo systemctl status aaip-scraper.timer
sudo systemctl list-timers | grep aaip-scraper

# View logs
sudo journalctl -u aaip-scraper.service --since today
sudo journalctl -u aaip-scraper.service -f  # follow

# Manual trigger (for testing)
sudo systemctl start aaip-scraper.service
```

#### 2. Extended Pipeline (New - Needs Deployment)

```bash
# Pull latest code
cd /home/randy/deploy/aaip-data
git pull origin test

# Copy systemd files
sudo cp deployment/aaip-extended-collectors.service /etc/systemd/system/
sudo cp deployment/aaip-extended-collectors.timer /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable aaip-extended-collectors.timer
sudo systemctl start aaip-extended-collectors.timer

# Verify it's active
sudo systemctl status aaip-extended-collectors.timer
sudo systemctl list-timers | grep extended

# Test manual run
sudo systemctl start aaip-extended-collectors.service
sudo journalctl -u aaip-extended-collectors.service -f
```

## 📁 File Structure

```
aaip-data/
├── scraper/
│   ├── collect_all_data.py              # Main pipeline orchestrator (hourly)
│   ├── collect_extended_data.py         # Extended pipeline orchestrator (daily) ⭐ NEW
│   ├── scraper.py                       # AAIP processing + draws
│   ├── aaip_news_scraper.py             # News + Chinese translation
│   ├── express_entry_collector.py       # Federal EE data
│   ├── alberta_economy_collector.py     # Economic indicators
│   ├── quarterly_labor_market_collector.py  # Labor market
│   ├── job_bank_scraper.py              # Job postings
│   ├── trend_analysis_engine.py         # Trend detection
│   ├── AUTOMATION_SETUP.md              # Main automation guide
│   ├── AUTOMATION_SUMMARY.md            # Main automation summary
│   ├── EXTENDED_COLLECTORS_README.md    # Extended collectors guide ⭐ NEW
│   └── COMPLETE_AUTOMATION_OVERVIEW.md  # This file ⭐ NEW
│
└── deployment/
    ├── aaip-scraper.service             # Main service
    ├── aaip-scraper.timer               # Main timer (hourly)
    ├── aaip-extended-collectors.service # Extended service ⭐ NEW
    └── aaip-extended-collectors.timer   # Extended timer (daily) ⭐ NEW
```

## 📊 Database Tables Updated

### Main Pipeline Updates (Hourly)

| Table | Description | Update Frequency |
|-------|-------------|------------------|
| `aaip_summary` | Overall program statistics | Every hour |
| `stream_data` | Per-stream tracking | Every hour |
| `aaip_draws` | Historical draw records | When new draws occur |
| `aaip_news` | News articles (EN + ZH) | When new articles published |
| `scrape_log` | Scraping activity log | Every hour |

### Extended Pipeline Updates (Daily)

| Table | Description | Update Frequency |
|-------|-------------|------------------|
| `express_entry_draws` | Federal EE draws | When new draws occur (check daily) |
| `alberta_economy` | Economic indicators | Daily |
| `labor_market_data` | Employment stats | Quarterly (check daily) |
| `job_postings` | Job market trends | Daily |

## 🔍 Monitoring & Verification

### Check Timer Status

```bash
# List all AAIP timers
sudo systemctl list-timers | grep aaip

# Check specific timer status
sudo systemctl status aaip-scraper.timer
sudo systemctl status aaip-extended-collectors.timer

# See when they'll run next
systemd-analyze calendar "hourly"             # Main pipeline
systemd-analyze calendar "*-*-* 03:00:00"     # Extended pipeline
```

### View Logs

```bash
# Main pipeline logs
sudo journalctl -u aaip-scraper.service -n 50           # Last 50 lines
sudo journalctl -u aaip-scraper.service --since today  # Today's logs
sudo journalctl -u aaip-scraper.service -f             # Follow live

# Extended pipeline logs
sudo journalctl -u aaip-extended-collectors.service -n 50
sudo journalctl -u aaip-extended-collectors.service --since today
sudo journalctl -u aaip-extended-collectors.service -f
```

### Verify Data Collection

```bash
# Connect to database
psql -h randy-vmware-virtual-platform.tail566241.ts.net \
     -U randy -d aaip_data_trend_dev_db

# Check scrape logs
SELECT 
  timestamp, 
  scraper_name, 
  status, 
  records_updated 
FROM scrape_log 
ORDER BY timestamp DESC 
LIMIT 20;

# Check main data (hourly updates)
SELECT draw_date, stream_category, lowest_score, invitations_issued 
FROM aaip_draws 
ORDER BY draw_date DESC 
LIMIT 10;

SELECT published_date, title_en 
FROM aaip_news 
ORDER BY published_date DESC 
LIMIT 10;

# Check extended data (daily updates)
SELECT draw_date, program, crs_cutoff, invitations_issued 
FROM express_entry_draws 
ORDER BY draw_date DESC 
LIMIT 10;

SELECT recorded_date, indicator_name, value 
FROM alberta_economy 
ORDER BY recorded_date DESC 
LIMIT 10;

SELECT quarter, year, unemployment_rate, job_vacancies 
FROM labor_market_data 
ORDER BY year DESC, quarter DESC 
LIMIT 5;

SELECT occupation_title, outlook, scrape_date 
FROM job_postings 
ORDER BY scrape_date DESC 
LIMIT 10;
```

## ⚙️ Configuration Options

### Change Main Pipeline Frequency

Edit `/etc/systemd/system/aaip-scraper.timer`:

```ini
[Timer]
OnCalendar=hourly                # Default: every hour at :00
# OnCalendar=*:0/30              # Every 30 minutes
# OnCalendar=*-*-* 0/2:00:00     # Every 2 hours
```

### Change Extended Pipeline Frequency

Edit `/etc/systemd/system/aaip-extended-collectors.timer`:

```ini
[Timer]
OnCalendar=*-*-* 03:00:00        # Default: daily at 3 AM
# OnCalendar=*-*-* 00,12:00:00   # Twice daily: midnight and noon
# OnCalendar=*-*-* */6:00:00     # Every 6 hours
```

After changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer
```

## 🔧 Troubleshooting

### Main Pipeline Not Running

```bash
# Check if timer is enabled
sudo systemctl is-enabled aaip-scraper.timer

# Enable if needed
sudo systemctl enable aaip-scraper.timer
sudo systemctl start aaip-scraper.timer

# Check for errors
systemctl status aaip-scraper.timer
sudo journalctl -u aaip-scraper.service --since today
```

### Extended Pipeline Not Running

```bash
# Check if timer is enabled
sudo systemctl is-enabled aaip-extended-collectors.timer

# Enable if needed
sudo systemctl enable aaip-extended-collectors.timer
sudo systemctl start aaip-extended-collectors.timer

# Check for errors
systemctl status aaip-extended-collectors.timer
sudo journalctl -u aaip-extended-collectors.service --since today
```

### Specific Collector Failing

```bash
# Run manually to see errors
cd /home/randy/deploy/aaip-data/scraper
source venv/bin/activate

# Test main collectors
python3 scraper.py
python3 aaip_news_scraper.py

# Test extended collectors
python3 express_entry_collector.py
python3 alberta_economy_collector.py
python3 quarterly_labor_market_collector.py
python3 job_bank_scraper.py

# Check dependencies
pip install -r requirements.txt
```

### Database Connection Issues

```bash
# Check .env file exists
cat /home/randy/deploy/aaip-data/scraper/.env

# Test database connection
psql -h randy-vmware-virtual-platform.tail566241.ts.net \
     -U randy -d aaip_data_trend_dev_db -c "SELECT 1;"

# Verify environment variables
cd /home/randy/deploy/aaip-data/scraper
source venv/bin/activate
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DB_HOST'))"
```

## 📈 Expected Behavior

### Typical Execution Times

**Main Pipeline (Hourly)**:
- Total: 3-5 minutes
- AAIP Scraper: 1-2 minutes
- News Scraper: 1-2 minutes
- Trend Analysis: <1 minute

**Extended Pipeline (Daily)**:
- Total: 5-10 minutes
- Express Entry: 1-2 minutes
- Alberta Economy: 1-2 minutes
- Labor Market: 1-2 minutes
- Job Bank: 3-5 minutes

### Success Indicators

✅ Both timers show "active (waiting)" status
✅ `scrape_log` table has recent entries
✅ Main data tables have hourly updates
✅ Extended data tables have daily updates
✅ No error messages in journalctl logs

## 📝 Summary

### What's Automated

✅ **Main Pipeline (Hourly)**:
1. AAIP Processing Info & Draw Records
2. AAIP News & Updates (with Chinese translation)
3. Trend Analysis

✅ **Extended Pipeline (Daily at 3 AM)**:
1. Express Entry Comparison Data
2. Alberta Economy Indicators
3. Labor Market Data
4. Job Bank Postings

### What You Need to Do

1. **One-Time Setup** (Extended Pipeline):
   ```bash
   cd /home/randy/deploy/aaip-data
   git pull origin test
   sudo cp deployment/aaip-extended-collectors.* /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now aaip-extended-collectors.timer
   ```

2. **Monitoring** (Optional but recommended):
   - Check timer status weekly: `sudo systemctl list-timers | grep aaip`
   - Review logs if issues occur: `sudo journalctl -u aaip-<service>`
   - Verify data in database occasionally

3. **No Manual Intervention Required** ✨
   - Both pipelines run automatically
   - Logs are saved to systemd journal
   - Database tracks all scraping activity

---

**🎉 All data collection is now fully automated! 🎉**

For detailed documentation, see:
- `scraper/AUTOMATION_SETUP.md` - Main pipeline setup
- `scraper/AUTOMATION_SUMMARY.md` - Main pipeline summary
- `scraper/EXTENDED_COLLECTORS_README.md` - Extended pipeline guide
