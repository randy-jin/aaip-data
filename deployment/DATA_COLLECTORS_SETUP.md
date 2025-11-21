# AAIP Data Collectors - Complete Setup Guide

## Overview

We have **2 automated data collection services** running on the server:

1. **Main Data Collector** (`aaip-scraper`) - Runs **hourly**
2. **Extended Data Collector** (`aaip-extended-collectors`) - Runs **daily at 3 AM**

---

## Data Collection Services

### 1. Main Data Collector (Hourly)

**Service**: `aaip-scraper.service` + `aaip-scraper.timer`  
**Schedule**: Every hour (via `collect_all_data.py`)  
**Collects**:
- ✅ AAIP Processing Information (Summary data)
- ✅ AAIP Draw History Records
- ✅ EOI Pool Data (with deduplication - only saves if data changed)
- ✅ AAIP News & Updates

**Scripts run**:
```bash
1. scraper.py                    # Processing info + Draw records
2. aaip_news_scraper.py          # News & Updates
3. (EOI dedup built into scraper.py)
```

**Timer Schedule**: `OnCalendar=hourly` (runs at :00 of every hour)

---

### 2. Extended Data Collector (Daily)

**Service**: `aaip-extended-collectors.service` + `aaip-extended-collectors.timer`  
**Schedule**: Daily at 3:00 AM (via `collect_extended_data.py`)  
**Collects**:
- ✅ Express Entry Comparison Data (Federal draws)
- ✅ Alberta Economy Indicators
- ✅ Quarterly Labor Market Data
- ✅ Job Bank Posting Trends

**Scripts run**:
```bash
1. express_entry_collector.py           # Federal EE draws
2. alberta_economy_collector.py         # Economic data
3. quarterly_labor_market_collector.py  # Labor statistics
4. job_bank_scraper.py                  # Job postings
```

**Timer Schedule**: `OnCalendar=*-*-* 03:00:00` (every day at 3 AM)

---

## Server Deployment Commands

### Initial Setup (One-time)

```bash
# 1. Copy service files to systemd
sudo cp /home/randy/deploy/aaip-data/deployment/aaip-scraper.service /etc/systemd/system/
sudo cp /home/randy/deploy/aaip-data/deployment/aaip-scraper.timer /etc/systemd/system/
sudo cp /home/randy/deploy/aaip-data/deployment/aaip-extended-collectors.service /etc/systemd/system/
sudo cp /home/randy/deploy/aaip-data/deployment/aaip-extended-collectors.timer /etc/systemd/system/

# 2. Reload systemd
sudo systemctl daemon-reload

# 3. Enable timers (start on boot)
sudo systemctl enable aaip-scraper.timer
sudo systemctl enable aaip-extended-collectors.timer

# 4. Start timers
sudo systemctl start aaip-scraper.timer
sudo systemctl start aaip-extended-collectors.timer
```

---

## Service Management Commands

### Check Status

```bash
# Check timer status
sudo systemctl status aaip-scraper.timer
sudo systemctl status aaip-extended-collectors.timer

# List all timers and next run time
sudo systemctl list-timers | grep aaip

# Check service logs
sudo journalctl -u aaip-scraper.service -f
sudo journalctl -u aaip-extended-collectors.service -f
```

### Manual Trigger (for testing)

```bash
# Run main collector manually (hourly data)
sudo systemctl start aaip-scraper.service

# Run extended collector manually (daily data)
sudo systemctl start aaip-extended-collectors.service

# Or run scripts directly
cd /home/randy/deploy/aaip-data/scraper
source venv/bin/activate
python3 collect_all_data.py          # Hourly collection
python3 collect_extended_data.py     # Daily collection
```

### Restart Services

```bash
# Restart timers
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer

# Stop timers
sudo systemctl stop aaip-scraper.timer
sudo systemctl stop aaip-extended-collectors.timer
```

---

## Data Collection Schedule Summary

| Data Source | Frequency | Service | Script |
|------------|-----------|---------|--------|
| AAIP Processing Info | Hourly | aaip-scraper | scraper.py |
| Draw History | Hourly | aaip-scraper | scraper.py |
| EOI Pool Data | Hourly (dedup) | aaip-scraper | scraper.py |
| News & Updates | Hourly | aaip-scraper | aaip_news_scraper.py |
| Express Entry | Daily 3 AM | extended-collectors | express_entry_collector.py |
| Alberta Economy | Daily 3 AM | extended-collectors | alberta_economy_collector.py |
| Labor Market | Daily 3 AM | extended-collectors | quarterly_labor_market_collector.py |
| Job Bank Data | Daily 3 AM | extended-collectors | job_bank_scraper.py |

---

## Important Notes

### EOI Pool Deduplication
- EOI Pool data is collected **hourly** but only saved if values changed
- Deduplication logic built into `scraper.py`
- Reduces database bloat from unchanged data

### Environment Variables
All services use:
```bash
DATABASE_URL=dbname=aaip_data_trend_dev_db
PATH=/home/randy/deploy/aaip-data/scraper/venv/bin
WorkingDirectory=/home/randy/deploy/aaip-data/scraper
```

### Timeouts
- Main collector: 15 minutes (900s)
- Extended collector: 15 minutes (900s)

### Logging
All logs are sent to systemd journal:
```bash
# View logs
sudo journalctl -u aaip-scraper.service -n 100
sudo journalctl -u aaip-extended-collectors.service -n 100

# Follow logs in real-time
sudo journalctl -u aaip-scraper.service -f
```

---

## Troubleshooting

### Check next scheduled run
```bash
sudo systemctl list-timers | grep aaip
```

### Check if timers are enabled
```bash
sudo systemctl is-enabled aaip-scraper.timer
sudo systemctl is-enabled aaip-extended-collectors.timer
```

### View failed runs
```bash
sudo journalctl -u aaip-scraper.service --since today | grep -i error
sudo journalctl -u aaip-extended-collectors.service --since today | grep -i error
```

### Manual test run
```bash
cd /home/randy/deploy/aaip-data/scraper
source venv/bin/activate

# Test hourly collection
python3 collect_all_data.py

# Test daily collection
python3 collect_extended_data.py

# Test individual scripts
python3 scraper.py
python3 aaip_news_scraper.py
python3 express_entry_collector.py
# etc.
```

---

## After Code Updates

When you push code to the `test` branch, the GitHub Actions deployment will:
1. ✅ Pull latest code
2. ✅ Update virtual environment dependencies
3. ✅ Restart backend service
4. ✅ Build and deploy frontend

**But you need to manually restart the timers if you update collector code:**

```bash
# SSH to server
ssh ssh.randy.it.com

# Restart timers to pick up new code
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer

# Or just trigger one manual run to verify
sudo systemctl start aaip-scraper.service
sudo systemctl start aaip-extended-collectors.service
```

---

## Quick Reference

```bash
# Status check
systemctl list-timers | grep aaip

# Start all
sudo systemctl start aaip-scraper.timer
sudo systemctl start aaip-extended-collectors.timer

# Stop all
sudo systemctl stop aaip-scraper.timer
sudo systemctl stop aaip-extended-collectors.timer

# View logs
sudo journalctl -u aaip-scraper.service -f
sudo journalctl -u aaip-extended-collectors.service -f
```

---

**Last Updated**: November 21, 2024  
**Total Collectors**: 2 services, 7 data sources
