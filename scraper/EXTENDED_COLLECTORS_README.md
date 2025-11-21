# Extended Data Collectors - Automated Setup

## Overview

This setup handles **additional data sources** beyond the main AAIP processing and draw data:

| Collector | Data Source | Frequency | Purpose |
|-----------|-------------|-----------|---------|
| **Express Entry** | IRCC EE Rounds | Daily | Federal vs. AAIP comparison |
| **Alberta Economy** | Statistics Canada | Daily | Economic indicators |
| **Labor Market** | Alberta LMI | Daily* | Employment statistics |
| **Job Bank** | Job Bank Canada | Daily | Job posting trends |

*Note: Labor Market collector internally checks if it's a new quarter before collecting*

## Why Separate from Main Scraper?

1. **Different Update Frequencies**: Main scraper runs hourly, these run daily
2. **Independent Failures**: If external sources fail, main AAIP data still works
3. **Longer Execution Time**: Some of these scrape multiple pages
4. **Less Critical**: App can function without these, but not without main data

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Automated Data Collection              │
└─────────────────────────────────────────────────────────┘

┌────────────────────┐                  ┌──────────────────────┐
│  HOURLY (Main)     │                  │  DAILY (Extended)    │
│  aaip-scraper      │                  │  aaip-extended       │
│  .timer/.service   │                  │  -collectors         │
└────────────────────┘                  │  .timer/.service     │
         │                              └──────────────────────┘
         │                                        │
         ▼                                        ▼
┌────────────────────┐                  ┌──────────────────────┐
│ collect_all_data.py│                  │collect_extended_     │
│                    │                  │data.py               │
│ ├─ scraper.py      │                  │                      │
│ ├─ aaip_news       │                  │ ├─ express_entry    │
│ └─ trend_analysis  │                  │ ├─ alberta_economy  │
└────────────────────┘                  │ ├─ labor_market     │
         │                              │ └─ job_bank          │
         │                              └──────────────────────┘
         │                                        │
         └────────────────┬───────────────────────┘
                          ▼
                 ┌─────────────────┐
                 │   PostgreSQL    │
                 │   Database      │
                 └─────────────────┘
```

## Quick Setup

### 1. Test Locally First

```bash
cd /Users/jinzhiqiang/workspaces/doit/aaip-data/scraper

# Test all extended collectors
python3 collect_extended_data.py --verbose

# Test specific collector
python3 collect_extended_data.py --collector express_entry -v
python3 collect_extended_data.py --collector alberta_economy -v
python3 collect_extended_data.py --collector labor_market -v
python3 collect_extended_data.py --collector job_bank -v
```

### 2. Deploy to Server

```bash
# On your server
cd /home/randy/deploy/aaip-data
git pull origin test

# Copy systemd files
sudo cp deployment/aaip-extended-collectors.service /etc/systemd/system/
sudo cp deployment/aaip-extended-collectors.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable aaip-extended-collectors.timer
sudo systemctl start aaip-extended-collectors.timer

# Verify
sudo systemctl status aaip-extended-collectors.timer
sudo systemctl list-timers | grep extended
```

### 3. Test Manual Run

```bash
# Trigger one-time collection
sudo systemctl start aaip-extended-collectors.service

# Watch logs in real-time
sudo journalctl -u aaip-extended-collectors.service -f
```

## Configuration

### Collection Time

By default, extended collectors run **daily at 3:00 AM** (quieter time).

To change, edit `deployment/aaip-extended-collectors.timer`:

```ini
[Timer]
OnCalendar=*-*-* 03:00:00     # Daily at 3 AM (default)
# OnCalendar=*-*-* */6:00:00  # Every 6 hours
# OnCalendar=*-*-* 00,12:00:00  # Twice daily (midnight and noon)
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aaip-extended-collectors.timer
```

### Timeout Settings

Individual collector timeouts (in `collect_extended_data.py`):

- Express Entry: 5 minutes
- Alberta Economy: 5 minutes  
- Labor Market: 5 minutes
- Job Bank: 10 minutes (more data to scrape)

Service-level timeout (in `.service` file): 15 minutes total

## Monitoring

### Check Timer Status
```bash
# When will it run next?
sudo systemctl list-timers aaip-extended-collectors.timer

# Is it enabled?
sudo systemctl is-enabled aaip-extended-collectors.timer

# Detailed status
sudo systemctl status aaip-extended-collectors.timer
```

### View Logs
```bash
# Last 50 lines
sudo journalctl -u aaip-extended-collectors.service -n 50

# Today's runs
sudo journalctl -u aaip-extended-collectors.service --since today

# Follow in real-time
sudo journalctl -u aaip-extended-collectors.service -f

# Specific date range
sudo journalctl -u aaip-extended-collectors.service \
  --since "2025-01-20" --until "2025-01-21"
```

### Check Database Results

```bash
# Express Entry draws
psql -d aaip_data_trend_dev_db -c \
  "SELECT draw_date, program, crs_cutoff, invitations_issued 
   FROM express_entry_draws 
   ORDER BY draw_date DESC LIMIT 10;"

# Alberta economy indicators
psql -d aaip_data_trend_dev_db -c \
  "SELECT recorded_date, indicator_name, value 
   FROM alberta_economy 
   ORDER BY recorded_date DESC LIMIT 10;"

# Labor market data
psql -d aaip_data_trend_dev_db -c \
  "SELECT quarter, year, unemployment_rate, job_vacancies 
   FROM labor_market_data 
   ORDER BY year DESC, quarter DESC LIMIT 10;"

# Job postings
psql -d aaip_data_trend_dev_db -c \
  "SELECT occupation_title, outlook, scrape_date 
   FROM job_postings 
   ORDER BY scrape_date DESC LIMIT 10;"
```

## Troubleshooting

### Collector Fails to Run

```bash
# Check service status
sudo systemctl status aaip-extended-collectors.service

# Run manually with verbose output
cd /home/randy/deploy/aaip-data/scraper
source venv/bin/activate
python3 collect_extended_data.py --verbose
```

### Specific Collector Failing

```bash
# Test individual collectors
cd /home/randy/deploy/aaip-data/scraper
source venv/bin/activate

python3 express_entry_collector.py
python3 alberta_economy_collector.py
python3 quarterly_labor_market_collector.py
python3 job_bank_scraper.py
```

### Timer Not Starting

```bash
# Check if timer is active
sudo systemctl is-active aaip-extended-collectors.timer

# If not, enable and start
sudo systemctl enable aaip-extended-collectors.timer
sudo systemctl start aaip-extended-collectors.timer

# Check for errors
systemctl status aaip-extended-collectors.timer
```

### No Data Being Collected

1. Check database connection in `.env`:
   ```bash
   cat /home/randy/deploy/aaip-data/scraper/.env
   ```

2. Test database connection:
   ```bash
   psql -h randy-vmware-virtual-platform.tail566241.ts.net \
        -U randy -d aaip_data_trend_dev_db -c "SELECT 1;"
   ```

3. Check if tables exist:
   ```bash
   psql -d aaip_data_trend_dev_db -c "\dt" | grep -E "(express_entry|alberta_economy|labor_market|job_postings)"
   ```

## Expected Results

### After First Run

You should see entries in:
- `express_entry_draws` table
- `alberta_economy` table
- `labor_market_data` table (if new quarter)
- `job_postings` table

### Typical Execution Time

- **Total**: 5-10 minutes for all 4 collectors
- **Express Entry**: 1-2 minutes
- **Alberta Economy**: 1-2 minutes
- **Labor Market**: 1-2 minutes
- **Job Bank**: 3-5 minutes

## Manual Testing

### Test All Collectors
```bash
cd scraper
python3 collect_extended_data.py --verbose
```

### Test Specific Collector
```bash
python3 collect_extended_data.py --collector express_entry
python3 collect_extended_data.py --collector alberta_economy
python3 collect_extended_data.py --collector labor_market
python3 collect_extended_data.py --collector job_bank
```

## Integration with Main Scraper

Both timers run independently:

```
Timeline (24 hours)
├── 00:00 ─ Main scraper runs
├── 01:00 ─ Main scraper runs
├── 02:00 ─ Main scraper runs
├── 03:00 ─ Main + Extended collectors run ★
├── 04:00 ─ Main scraper runs
...
├── 23:00 ─ Main scraper runs
└── (repeat)
```

## Summary

✅ **Main Scraper** (`aaip-scraper.timer`):
- Runs **hourly**
- Collects: AAIP processing info, draw records, news, trends
- Critical for app functionality

✅ **Extended Collectors** (`aaip-extended-collectors.timer`):
- Runs **daily at 3 AM**
- Collects: Express Entry, economy, labor market, job postings
- Enhances app with comparative and contextual data

Both are fully automated and log to systemd journal! 🎉
