# Server Setup Guide for AAIP Data Scrapers

## Issue Diagnosis

If you see these errors on your test server:

```
ModuleNotFoundError: No module named 'bs4'
```

or

```
psycopg2.OperationalError: connection failed
```

Follow this guide to fix them.

## Quick Fix

Run the automated fix script:

```bash
cd ~/deploy/aaip-data/scraper
chmod +x fix_server_dependencies.sh
./fix_server_dependencies.sh
```

This script will:
1. Create/activate virtual environment
2. Install all Python dependencies
3. Verify package installation
4. Check `.env` configuration

## Manual Setup

If the automated script doesn't work, follow these steps:

### 1. Create Virtual Environment

```bash
cd ~/deploy/aaip-data/scraper
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python3 -c "import bs4; print('✓ BeautifulSoup4 OK')"
python3 -c "import psycopg2; print('✓ psycopg2 OK')"
python3 -c "import requests; print('✓ requests OK')"
python3 -c "import pdfplumber; print('✓ pdfplumber OK')"
```

### 4. Configure Database Connection

Create `.env` file with your database credentials:

```bash
cd ~/deploy/aaip-data/scraper
nano .env
```

Add these lines (update with your actual values):

```bash
# Database Configuration
DB_HOST=randy-vmware-virtual-platform.tail566241.ts.net
DB_PORT=5432
DB_NAME=aaip_data_trend_dev_db
DB_USER=randy
DB_PASSWORD=1234QWER$

# Alternative: Use DATABASE_URL (choose one method)
# DATABASE_URL=postgresql://randy:1234QWER$@randy-vmware-virtual-platform.tail566241.ts.net:5432/aaip_data_trend_dev_db
```

### 5. Test Database Connection

```bash
python3 << 'EOF'
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print("✓ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Database connection failed: {e}")
EOF
```

### 6. Test Scrapers

```bash
# Test all scrapers
python3 test_collectors.py

# Or test individual scrapers
python3 express_entry_collector.py
python3 job_bank_scraper.py
python3 alberta_economy_collector.py
python3 quarterly_labor_market_collector.py
```

## Systemd Service Configuration

If using systemd for automation, ensure the service file uses the virtual environment:

```ini
[Unit]
Description=AAIP Data Scraper
After=network.target postgresql.service

[Service]
Type=oneshot
User=randy
WorkingDirectory=/home/randy/deploy/aaip-data/scraper
Environment="PATH=/home/randy/deploy/aaip-data/scraper/venv/bin:/usr/bin"
ExecStart=/home/randy/deploy/aaip-data/scraper/venv/bin/python3 scraper.py

[Install]
WantedBy=multi-user.target
```

### Update Systemd Service

If you need to update the service file:

```bash
sudo nano /etc/systemd/system/aaip-scraper.service
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.service
sudo systemctl status aaip-scraper.service
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'bs4'"

**Solution:**
```bash
cd ~/deploy/aaip-data/scraper
source venv/bin/activate
pip install beautifulsoup4 lxml
```

### Issue: "psycopg2.OperationalError: connection to server failed"

**Causes:**
1. Database server not running
2. Wrong credentials in `.env`
3. Network/firewall issues

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if host is reachable
ping randy-vmware-virtual-platform.tail566241.ts.net

# Test connection with psql
psql -h randy-vmware-virtual-platform.tail566241.ts.net -p 5432 -U randy -d aaip_data_trend_dev_db

# Verify .env file
cat ~/deploy/aaip-data/scraper/.env
```

### Issue: systemd service fails to start

**Solution:**
```bash
# Check service logs
sudo journalctl -u aaip-scraper.service -n 50

# Check if venv exists
ls -la ~/deploy/aaip-data/scraper/venv/

# Manually run the scraper to see error
cd ~/deploy/aaip-data/scraper
source venv/bin/activate
python3 scraper.py
```

## Deployment Checklist

Before deploying to production, verify:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list | grep beautifulsoup4`)
- [ ] `.env` file configured with correct database credentials
- [ ] Database connection test successful
- [ ] Manual scraper test successful
- [ ] Systemd service file updated with venv path
- [ ] Systemd service started and enabled
- [ ] Systemd timer configured (if using scheduled scraping)
- [ ] Logs directory writable
- [ ] Firewall allows outbound HTTPS (for scraping)
- [ ] Firewall allows PostgreSQL connection

## Additional Resources

- **Requirements file**: `requirements.txt`
- **Test script**: `test_collectors.py`
- **Automation setup**: `AUTOMATION_SUMMARY.md`
- **Collector documentation**: `EXTENDED_COLLECTORS_README.md`

## Getting Help

If issues persist:

1. Check the scraper logs: `sudo journalctl -u aaip-scraper.service -f`
2. Run test_collectors.py for diagnostic info
3. Verify Python version: `python3 --version` (should be 3.11+)
4. Check disk space: `df -h`
5. Check memory: `free -h`
