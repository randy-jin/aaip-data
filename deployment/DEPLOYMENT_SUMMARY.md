# AAIP Data Tracker - Complete Deployment Summary

## 📋 System Overview

**Status**: ✅ Production Ready  
**Environment**: Test Server (Cloudflare Tunnel: ssh.randy.it.com)  
**Last Updated**: November 21, 2024

---

## 🏗️ Architecture Components

### 1. Backend Service
- **Service**: `aaip-backend-test.service`
- **Technology**: FastAPI (Python 3.11+)
- **Port**: 8000
- **Script**: `main_enhanced.py`
- **Database**: PostgreSQL (`aaip_data_trend_dev_db`)
- **Status**: ✅ Running automatically on boot

### 2. Frontend Application
- **Location**: `/var/www/aaip-test/`
- **Technology**: React 18 + Vite + TailwindCSS
- **Build**: Automated via GitHub Actions
- **Dev Port**: 3002 (local development)
- **Status**: ✅ Deployed and serving

### 3. Data Collectors
- **Hourly Collector**: `aaip-scraper.service` (+ timer)
- **Daily Collector**: `aaip-extended-collectors.service` (+ timer)
- **Orchestrators**: `collect_all_data.py`, `collect_extended_data.py`
- **Status**: ✅ Automated via systemd timers

---

## 🔄 Automated Data Collection

### Hourly Collection (Every :00)
| Data Source | Script | Database Table |
|------------|--------|----------------|
| AAIP Processing Info | scraper.py | aaip_summary, stream_data |
| Draw History Records | scraper.py | aaip_draws |
| EOI Pool Data | scraper.py | eoi_pool_data |
| News & Updates | aaip_news_scraper.py | aaip_news |

**Next Run**: Check with `systemctl list-timers | grep aaip-scraper`

### Daily Collection (3:00 AM)
| Data Source | Script | Database Table |
|------------|--------|----------------|
| Express Entry Draws | express_entry_collector.py | express_entry_draws |
| Alberta Economy | alberta_economy_collector.py | alberta_economy |
| Labor Market Data | quarterly_labor_market_collector.py | labor_market_data |
| Job Bank Postings | job_bank_scraper.py | job_postings |

**Next Run**: Check with `systemctl list-timers | grep aaip-extended`

---

## 📚 Key Documentation Files

1. **DATA_COLLECTORS_SETUP.md** - Complete collector setup and management
2. **QUICK_COMMANDS.md** - Quick reference for common operations
3. **CLAUDE.md** - AI assistant coding guidelines
4. **README.md** - Project overview and getting started

---

## 🚀 Deployment Workflow

### Development → Production Flow

```
1. Develop on `main` branch
   ↓
2. Test locally (localhost:8000 backend, localhost:3002 frontend)
   ↓
3. Merge main → test branch
   ↓
4. Push to GitHub (triggers GitHub Actions)
   ↓
5. Automated deployment to server:
   - Pull code
   - Update dependencies
   - Restart backend
   - Build & deploy frontend
   ↓
6. Manual step: Restart data collectors
   sudo systemctl restart aaip-scraper.timer
   sudo systemctl restart aaip-extended-collectors.timer
```

### GitHub Actions Workflow
- **File**: `.github/workflows/test-deploy.yml`
- **Trigger**: Push to `test` branch
- **Steps**:
  1. ✅ Python import validation
  2. ✅ Frontend build test
  3. ✅ SSH to server via Cloudflare Tunnel
  4. ✅ Pull latest code
  5. ✅ Update Python dependencies
  6. ✅ Restart backend service
  7. ✅ Build and deploy frontend
  8. ✅ Update scraper dependencies

---

## 🛠️ Server Setup (One-Time)

All services are already set up, but if you need to reinstall:

```bash
ssh ssh.randy.it.com
cd /home/randy/deploy/aaip-data

# Setup all data collectors
./deployment/setup_collectors.sh

# Or manually copy service files
sudo cp deployment/*.service /etc/systemd/system/
sudo cp deployment/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now aaip-scraper.timer
sudo systemctl enable --now aaip-extended-collectors.timer
```

---

## 📊 Monitoring & Maintenance

### Daily Checks
```bash
# Check all services are running
ssh ssh.randy.it.com
sudo systemctl list-timers | grep aaip
sudo systemctl status aaip-backend-test
```

### View Logs
```bash
# Backend logs
sudo journalctl -u aaip-backend-test -f

# Data collector logs
sudo journalctl -u aaip-scraper.service -f
sudo journalctl -u aaip-extended-collectors.service -f
```

### Database Health
```bash
sudo -u postgres psql aaip_data_trend_dev_db

-- Check recent data
SELECT COUNT(*) FROM aaip_draws;
SELECT MAX(timestamp) FROM aaip_summary;
SELECT MAX(draw_date) FROM aaip_draws;
SELECT MAX(timestamp) FROM eoi_pool_data;
SELECT MAX(timestamp) FROM aaip_news;
```

---

## 🔐 Environment Variables

### Backend & Scraper
```bash
DATABASE_URL=postgresql://randy:1234QWER$@randy-vmware-virtual-platform.tail566241.ts.net:5432/aaip_data_trend_dev_db

# Or individual components:
DB_HOST=randy-vmware-virtual-platform.tail566241.ts.net
DB_PORT=5432
DB_NAME=aaip_data_trend_dev_db
DB_USER=randy
DB_PASSWORD=1234QWER$
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
aaip-data/
├── backend/               # FastAPI backend
│   ├── main_enhanced.py   # Production backend (used)
│   ├── main_draws.py      # Legacy backend with draw support
│   └── requirements.txt
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page components
│   │   └── api*.js        # API integration
│   └── package.json
├── scraper/               # Data collection scripts
│   ├── collect_all_data.py            # Hourly orchestrator
│   ├── collect_extended_data.py       # Daily orchestrator
│   ├── scraper.py                     # Main AAIP scraper
│   ├── aaip_news_scraper.py          # News scraper
│   ├── express_entry_collector.py     # EE data
│   ├── alberta_economy_collector.py   # Economy data
│   ├── quarterly_labor_market_collector.py  # Labor data
│   └── job_bank_scraper.py           # Job Bank data
├── deployment/            # Deployment configs
│   ├── *.service         # Systemd service files
│   ├── *.timer           # Systemd timer files
│   ├── setup_collectors.sh          # Auto-setup script
│   ├── DATA_COLLECTORS_SETUP.md     # Full guide
│   └── QUICK_COMMANDS.md            # Quick reference
└── docs/                  # Additional documentation
```

---

## 🎯 Key Features Implemented

✅ Real-time AAIP processing information tracking  
✅ Historical draw records (2024 + 2025 data)  
✅ EOI Pool visualization with deduplication  
✅ News & Updates module  
✅ Express Entry comparison dashboard  
✅ Alberta economy indicators  
✅ Labor market insights  
✅ Job Bank posting trends  
✅ Multi-year filtering  
✅ Stream category filtering  
✅ Responsive charts and visualizations  
✅ Hourly + daily automated data collection  
✅ CI/CD pipeline with GitHub Actions  

---

## 🆘 Troubleshooting

### Backend Not Starting
```bash
# Check logs
sudo journalctl -u aaip-backend-test -n 100

# Restart manually
sudo systemctl restart aaip-backend-test
```

### Collectors Not Running
```bash
# Check timer status
sudo systemctl list-timers | grep aaip

# Check if enabled
sudo systemctl is-enabled aaip-scraper.timer

# Enable and start
sudo systemctl enable --now aaip-scraper.timer
sudo systemctl enable --now aaip-extended-collectors.timer
```

### Database Connection Issues
```bash
# Test connection
psql "postgresql://randy:1234QWER$@randy-vmware-virtual-platform.tail566241.ts.net:5432/aaip_data_trend_dev_db"

# Check if PostgreSQL is running
sudo systemctl status postgresql
```

---

## 📞 Quick Support Commands

```bash
# Full system status check
ssh ssh.randy.it.com
sudo systemctl status aaip-backend-test aaip-scraper.timer aaip-extended-collectors.timer

# View all timers
sudo systemctl list-timers

# Restart everything
sudo systemctl restart aaip-backend-test
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer

# View all logs
sudo journalctl -u aaip-backend-test -u aaip-scraper.service -u aaip-extended-collectors.service -f
```

---

## ✅ What's Next?

Current system is fully operational and collecting data automatically. Future enhancements could include:

- [ ] Email notifications for failed collections
- [ ] Data quality dashboards
- [ ] Automated backups
- [ ] Performance monitoring
- [ ] User authentication for admin features
- [ ] API rate limiting
- [ ] Caching layer for frequently accessed data

---

**System Status**: 🟢 All Services Running  
**Last Deployment**: Automated via GitHub Actions  
**Monitoring**: Manual via systemctl and journalctl  
**Uptime**: High (systemd auto-restart enabled)
