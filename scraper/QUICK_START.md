# Quick Start - Automated Data Collection

## 🚀 What's Been Set Up

All 7 data sources now collect automatically **every hour**:

1. ✅ AAIP Processing & Draws (alberta.ca/aaip-processing-information)
2. ✅ AAIP News Updates (alberta.ca/aaip-updates) + Chinese translation
3. ✅ Express Entry Comparison
4. ✅ Alberta Economy Indicators
5. ✅ Labor Market Data
6. ✅ Job Bank Postings
7. ✅ Trend Analysis Engine

## 📝 New Files Created

```
scraper/
├── collect_all_data.py      ← Master orchestrator script
├── setup_automation.sh       ← Interactive setup helper
├── test_collectors.py        ← Test suite
├── AUTOMATION_SETUP.md       ← Complete documentation
├── AUTOMATION_SUMMARY.md     ← This summary
└── QUICK_START.md            ← Quick reference

deployment/
└── aaip-scraper.service      ← Updated to use orchestrator
```

## ⚡ Quick Commands

### Test Everything
```bash
cd scraper
python3 test_collectors.py     # Test imports
python3 collect_all_data.py    # Run all collectors
```

### Setup Automation
```bash
cd scraper
./setup_automation.sh          # Interactive setup
```

### On Production Server
```bash
# Deploy
cd /home/randy/deploy/aaip-data
git pull origin test
sudo cp deployment/aaip-scraper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.timer

# Monitor
sudo systemctl status aaip-scraper.timer
sudo journalctl -u aaip-scraper.service -f

# Manual trigger
sudo systemctl start aaip-scraper.service
```

### Check Data
```bash
psql -d aaip_data_trend_dev_db -c \
  "SELECT * FROM scrape_log ORDER BY timestamp DESC LIMIT 10;"

psql -d aaip_data_trend_dev_db -c \
  "SELECT draw_date, stream_category, lowest_score 
   FROM aaip_draws ORDER BY draw_date DESC LIMIT 10;"

psql -d aaip_data_trend_dev_db -c \
  "SELECT published_date, title_en 
   FROM aaip_news ORDER BY published_date DESC LIMIT 10;"
```

## 📖 Documentation

- **AUTOMATION_SETUP.md** - Complete setup guide (systemd + cron)
- **AUTOMATION_SUMMARY.md** - Full feature summary
- **CLAUDE.md** - Project documentation (updated)

## ✨ Key Features

- ⏰ Runs every hour automatically
- 🛡️ Critical failure handling
- 📊 Detailed logging
- ⏱️ 5-minute timeout per collector
- 🌐 Bilingual support (EN + ZH)
- 📈 Comprehensive data coverage

---

**Everything is ready! Data collection will run automatically every hour.** 🎉
