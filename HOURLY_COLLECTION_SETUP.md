# Hourly Data Collection Setup Guide

## Current Status
❌ **NOT RUNNING** - Manual collection only

⚠️ **Important**: The scraper now includes **change detection** - it will only save data when something actually changes on the AAIP website. This keeps your database clean and meaningful!

You need to choose and set up one of these options:

---

## Option 1: GitHub Actions (Recommended - Free)

### Requirements:
- Push code to GitHub
- Database accessible from internet OR use GitHub-hosted database

### Setup Steps:

1. **Push to GitHub:**
```bash
cd /Users/jinzhiqiang/workspaces/doit/aaip-data
git remote add origin https://github.com/YOUR_USERNAME/aaip-data.git
git push -u origin main
```

2. **Add Database Secret:**
   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `DATABASE_URL`
   - Value: `postgresql://randy:1234QWER$@100.77.247.113:5432/aaip_data_trend_dev_db`

3. **Enable Actions:**
   - Go to "Actions" tab
   - Enable workflows

4. **Done!** Will run every hour automatically at :00

### Manual Trigger:
- Go to Actions tab → AAIP Data Scraper → Run workflow

---

## Option 2: Cron Job (Server/Mac)

### For macOS/Linux Server:

1. **Create cron job:**
```bash
crontab -e
```

2. **Add this line:**
```bash
0 * * * * cd /Users/jinzhiqiang/workspaces/doit/aaip-data/scraper && /usr/local/bin/python3 scraper_enhanced.py >> /tmp/aaip_scraper.log 2>&1
```

3. **Verify:**
```bash
crontab -l
```

### For Windows (Task Scheduler):

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 1 hour
4. Action: Start program
   - Program: `python3`
   - Arguments: `scraper_enhanced.py`
   - Start in: `/path/to/aaip-data/scraper`

---

## Option 3: Docker Container with Cron

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY scraper/ /app/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y cron
COPY scraper-cron /etc/cron.d/scraper-cron
RUN chmod 0644 /etc/cron.d/scraper-cron
RUN crontab /etc/cron.d/scraper-cron
CMD ["cron", "-f"]
```

2. **Create scraper-cron:**
```
0 * * * * cd /app && python3 scraper_enhanced.py >> /var/log/scraper.log 2>&1
```

3. **Run:**
```bash
docker build -t aaip-scraper .
docker run -d --name aaip-scraper aaip-scraper
```

---

## Option 4: Cloud Scheduler (Production)

### Heroku Scheduler:
```bash
heroku addons:create scheduler:standard
heroku addons:open scheduler
# Add job: python3 scraper/scraper_enhanced.py
```

### AWS EventBridge + Lambda:
- Create Lambda function with scraper code
- Trigger: EventBridge rule (rate: 1 hour)

### Google Cloud Scheduler:
- Create Cloud Function with scraper
- Trigger: Cloud Scheduler (every hour)

---

## Testing Your Setup

### Test Manually:
```bash
cd /Users/jinzhiqiang/workspaces/doit/aaip-data/scraper
python3 scraper_enhanced.py
```

### Check Logs:
```bash
# Database logs
PGPASSWORD='1234QWER$' psql -h 100.77.247.113 -p 5432 -U randy -d aaip_data_trend_dev_db \
  -c "SELECT timestamp, status, streams_collected FROM scrape_log ORDER BY timestamp DESC LIMIT 10;"
```

### Verify Data:
```bash
# Check latest scrape
PGPASSWORD='1234QWER$' psql -h 100.77.247.113 -p 5432 -U randy -d aaip_data_trend_dev_db \
  -c "SELECT MAX(timestamp) as last_scrape, COUNT(*) as total_records FROM aaip_summary;"
```

---

## Monitoring

### Email Notifications (Optional):

Add to scraper_enhanced.py:
```python
import smtplib
from email.mime.text import MIMEText

def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = 'AAIP Scraper Alert'
    msg['From'] = 'scraper@example.com'
    msg['To'] = 'your@email.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user', 'pass')
        server.send_message(msg)

# In main() catch block:
except Exception as e:
    send_alert(f"Scraper failed: {e}")
```

---

## Recommended: Option 1 (GitHub Actions)

**Why:**
- ✅ Free (2,000 minutes/month on free plan)
- ✅ No server maintenance
- ✅ Built-in logs and monitoring
- ✅ Manual trigger available
- ✅ Version controlled

**Just need to:**
1. Push to GitHub
2. Add DATABASE_URL secret
3. Done!

---

## Current Schedule:

**Not running yet** - Choose option above

Once set up, scraper will run:
- Every hour at :00 minutes (00:00, 01:00, 02:00, etc.)
- Collects data from all 8 streams
- **Only saves when data changes** (smart detection)
- Takes ~10 seconds per run
- Logs all attempts (saved or skipped)

## How Change Detection Works:

The scraper compares current data with the last saved record:

1. **Fetches data** from AAIP website
2. **Compares** with last database record
3. **If identical**: Logs "no_change" and skips save
4. **If different**: Saves new data with timestamp

### Example Logs:
```
2025-11-07 14:00:00 | success   | Data changed and saved      | 8
2025-11-07 15:00:00 | no_change | Data unchanged, not saved   | 0
2025-11-07 16:00:00 | no_change | Data unchanged, not saved   | 0
2025-11-07 17:00:00 | success   | Data changed and saved      | 8
```

This means:
- ✅ Your database only contains meaningful changes
- ✅ Charts show actual trend changes, not noise
- ✅ Storage space is optimized
- ✅ You can see when AAIP actually updates their data
