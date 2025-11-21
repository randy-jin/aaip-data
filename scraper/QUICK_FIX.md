# Quick Fix for Server Errors

## Run This On Your Test Server

```bash
# 1. Go to scraper directory
cd ~/deploy/aaip-data/scraper

# 2. Download and run the fix script
chmod +x fix_server_dependencies.sh
./fix_server_dependencies.sh

# 3. Configure database (if .env was created)
nano .env
# Update with:
# DB_HOST=randy-vmware-virtual-platform.tail566241.ts.net
# DB_PORT=5432
# DB_NAME=aaip_data_trend_dev_db
# DB_USER=randy
# DB_PASSWORD=1234QWER$

# 4. Test the fix
source venv/bin/activate
python3 test_collectors.py
```

## What This Fixes

✅ **ModuleNotFoundError: No module named 'bs4'**
- Reinstalls beautifulsoup4 in virtual environment

✅ **Database connection errors**
- Creates/checks `.env` configuration file
- Verifies database credentials

## If Issues Persist

See detailed guide: `SERVER_SETUP.md`

## Quick Tests

```bash
# Test individual scrapers
cd ~/deploy/aaip-data/scraper
source venv/bin/activate

python3 express_entry_collector.py
python3 job_bank_scraper.py
python3 alberta_economy_collector.py
python3 quarterly_labor_market_collector.py
```

## Update Systemd Services

After fixing, update your systemd service to use the venv:

```bash
sudo nano /etc/systemd/system/aaip-scraper.service
```

Make sure it has:
```ini
Environment="PATH=/home/randy/deploy/aaip-data/scraper/venv/bin:/usr/bin"
ExecStart=/home/randy/deploy/aaip-data/scraper/venv/bin/python3 scraper.py
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.service
```
