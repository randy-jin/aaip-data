# AAIP Data Collectors - Deployment Guide

This directory contains all the configuration and scripts needed to deploy and manage the AAIP data collection system on the server.

## 📁 Files Overview

### Service Configuration Files
- `aaip-backend-test.service` - FastAPI backend service configuration
- `aaip-scraper.service` - Hourly data collection service
- `aaip-scraper.timer` - Timer for hourly collection (runs every :00)
- `aaip-extended-collectors.service` - Daily extended data collection service
- `aaip-extended-collectors.timer` - Timer for daily collection (runs at 3:00 AM)

### Setup Scripts
- **`setup_collectors.sh`** ⭐ - **One-click setup** for all data collectors
- `check_health.sh` - Health check and monitoring script
- `update.sh` - Manual deployment update script (if exists)

### Documentation
- **`QUICK_COMMANDS.md`** ⭐ - Quick reference for common operations
- **`DATA_COLLECTORS_SETUP.md`** ⭐ - Complete setup and management guide
- **`DEPLOYMENT_SUMMARY.md`** ⭐ - Full system overview
- `README.md` - This file

---

## 🚀 Quick Start (First Time Setup)

```bash
# 1. SSH to server
ssh ssh.randy.it.com

# 2. Go to project directory
cd /home/randy/deploy/aaip-data

# 3. Pull latest code
git pull origin test

# 4. Run one-click setup
./deployment/setup_collectors.sh

# 5. Verify it's working
./deployment/check_health.sh
```

That's it! Your data collectors are now running automatically.

---

## 📊 What Gets Collected?

### Hourly Collection (aaip-scraper)
Runs every hour at :00 minutes
- AAIP Processing Information
- Draw History Records  
- EOI Pool Data (with deduplication)
- News & Updates

### Daily Collection (aaip-extended-collectors)
Runs once per day at 3:00 AM
- Express Entry Federal Draws
- Alberta Economy Indicators
- Labor Market Statistics
- Job Bank Posting Trends

---

## 🔍 Monitoring & Maintenance

### Check Status
```bash
# Quick health check
./deployment/check_health.sh

# Check when next collection will run
sudo systemctl list-timers | grep aaip

# Check service status
sudo systemctl status aaip-scraper.timer
sudo systemctl status aaip-extended-collectors.timer
```

### View Logs
```bash
# Real-time logs
sudo journalctl -u aaip-scraper.service -f
sudo journalctl -u aaip-extended-collectors.service -f

# Last 100 lines
sudo journalctl -u aaip-scraper.service -n 100
```

### Manual Test Run
```bash
# Trigger hourly collection manually
sudo systemctl start aaip-scraper.service

# Trigger daily collection manually
sudo systemctl start aaip-extended-collectors.service
```

---

## 🔄 After Code Updates

When you push code to the `test` branch, GitHub Actions will automatically deploy the backend and frontend. However, you need to manually restart the data collection timers:

```bash
ssh ssh.randy.it.com
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer
```

Or just pull the code and re-run setup:
```bash
cd /home/randy/deploy/aaip-data
git pull origin test
./deployment/setup_collectors.sh
```

---

## 📖 Detailed Documentation

For more details, see:
- **Quick Commands**: `QUICK_COMMANDS.md` - Copy-paste ready commands
- **Full Setup Guide**: `DATA_COLLECTORS_SETUP.md` - Complete configuration details
- **System Overview**: `DEPLOYMENT_SUMMARY.md` - Architecture and troubleshooting

---

## ⚙️ Service Details

### Backend Service
- **Name**: `aaip-backend-test.service`
- **Port**: 8000
- **Script**: `main_enhanced.py`
- **Auto-start**: Yes (enabled on boot)

### Data Collector Services
- **Hourly**: `aaip-scraper.service` + `aaip-scraper.timer`
- **Daily**: `aaip-extended-collectors.service` + `aaip-extended-collectors.timer`
- **Auto-start**: Yes (enabled on boot)
- **Logs**: systemd journal

---

## 🆘 Common Issues

### Collectors Not Running
```bash
# Check if timers are enabled
sudo systemctl is-enabled aaip-scraper.timer

# Enable if not
sudo systemctl enable --now aaip-scraper.timer
sudo systemctl enable --now aaip-extended-collectors.timer
```

### Check for Errors
```bash
# Check recent errors
sudo journalctl -u aaip-scraper.service --since today | grep -i error
sudo journalctl -u aaip-extended-collectors.service --since today | grep -i error
```

### Service Files Changed
```bash
# If you modified .service or .timer files, reload systemd
sudo systemctl daemon-reload
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer
```

---

## 📞 Quick Support

```bash
# Full system status
sudo systemctl status aaip-backend-test aaip-scraper.timer aaip-extended-collectors.timer

# Restart everything
sudo systemctl restart aaip-backend-test
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer

# View all logs
sudo journalctl -u aaip-backend-test -u aaip-scraper.service -u aaip-extended-collectors.service -f
```

---

## ✅ System Requirements

- Ubuntu/Debian server
- systemd (for service management)
- Python 3.11+
- PostgreSQL database
- Cloudflare Tunnel (for SSH access)

---

**Last Updated**: November 21, 2024  
**Maintained by**: Randy Jin  
**Server**: ssh.randy.it.com
