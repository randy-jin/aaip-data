# Server Fix Summary - AAIP Data Scraper Issues

## Problems Identified

### 1. Missing Python Package: beautifulsoup4
```
ModuleNotFoundError: No module named 'bs4'
```

**Affected scrapers:**
- express_entry_collector.py
- job_bank_scraper.py (indirectly)
- alberta_economy_collector.py
- quarterly_labor_market_collector.py

### 2. Database Connection Issues
```
Traceback in job_bank_scraper.py at line 173: get_db_connection()
```

**Potential causes:**
- Missing `.env` file
- Incorrect database credentials
- Database not accessible from server

## Solutions Provided

### Fix Script: `scraper/fix_server_dependencies.sh`
Automated script that:
1. Creates Python virtual environment
2. Installs all required packages
3. Verifies package installation
4. Checks `.env` configuration

### Documentation Files Created:
1. **QUICK_FIX.md** - Fast troubleshooting guide
2. **SERVER_SETUP.md** - Comprehensive setup guide
3. **fix_server_dependencies.sh** - Automated fix script

## How to Fix on Test Server

Run these commands on `randy@test-server`:

```bash
cd ~/deploy/aaip-data/scraper
chmod +x fix_server_dependencies.sh
./fix_server_dependencies.sh
```

Then configure `.env`:
```bash
nano .env
```

Add:
```
DB_HOST=randy-vmware-virtual-platform.tail566241.ts.net
DB_PORT=5432
DB_NAME=aaip_data_trend_dev_db
DB_USER=randy
DB_PASSWORD=1234QWER$
```

Test:
```bash
source venv/bin/activate
python3 test_collectors.py
```

## Systemd Service Update Needed

Update `/etc/systemd/system/aaip-scraper.service` to use venv:

```ini
[Service]
Environment="PATH=/home/randy/deploy/aaip-data/scraper/venv/bin:/usr/bin"
ExecStart=/home/randy/deploy/aaip-data/scraper/venv/bin/python3 scraper.py
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.service
sudo systemctl status aaip-scraper.service
```

## Files to Transfer to Server

Copy these files to your test server:

```bash
scp scraper/fix_server_dependencies.sh randy@server:~/deploy/aaip-data/scraper/
scp scraper/QUICK_FIX.md randy@server:~/deploy/aaip-data/scraper/
scp scraper/SERVER_SETUP.md randy@server:~/deploy/aaip-data/scraper/
```

Or let GitHub Actions deployment handle it (push to test branch).

## Prevention for Future

✅ Always use virtual environment on server
✅ Keep `.env` file with correct credentials
✅ Run `pip install -r requirements.txt` after code updates
✅ Test scrapers manually before enabling systemd timers
