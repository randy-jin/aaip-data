# Quick Command Reference - AAIP Data Collectors

## 🚀 One-Time Setup (Run on Server)

```bash
ssh ssh.randy.it.com
cd /home/randy/deploy/aaip-data
./deployment/setup_collectors.sh
```

---

## 📊 Check Status

```bash
# See all scheduled collectors and next run times
sudo systemctl list-timers | grep aaip

# Check if timers are running
sudo systemctl status aaip-scraper.timer
sudo systemctl status aaip-extended-collectors.timer
```

---

## 🔄 Manual Run (for testing)

```bash
# Run hourly collector (AAIP data, draws, EOI, news)
sudo systemctl start aaip-scraper.service

# Run daily collector (EE, economy, labor, job bank)
sudo systemctl start aaip-extended-collectors.service
```

---

## 📝 View Logs

```bash
# Real-time logs (follow mode)
sudo journalctl -u aaip-scraper.service -f
sudo journalctl -u aaip-extended-collectors.service -f

# Last 100 lines
sudo journalctl -u aaip-scraper.service -n 100
sudo journalctl -u aaip-extended-collectors.service -n 100

# Today's logs only
sudo journalctl -u aaip-scraper.service --since today
```

---

## 🔧 After Code Updates

```bash
# When you push new code to test branch, GitHub Actions will deploy
# But you need to restart timers manually:

ssh ssh.randy.it.com
sudo systemctl restart aaip-scraper.timer
sudo systemctl restart aaip-extended-collectors.timer

# Verify they restarted
sudo systemctl list-timers | grep aaip
```

---

## 🛑 Stop/Start Timers

```bash
# Stop automatic collection
sudo systemctl stop aaip-scraper.timer
sudo systemctl stop aaip-extended-collectors.timer

# Start automatic collection
sudo systemctl start aaip-scraper.timer
sudo systemctl start aaip-extended-collectors.timer
```

---

## 🗂️ What Gets Collected

### Hourly Collection (aaip-scraper)
- ✅ AAIP Processing Information
- ✅ AAIP Draw History Records
- ✅ EOI Pool Data (with deduplication)
- ✅ AAIP News & Updates

### Daily Collection (aaip-extended-collectors) at 3 AM
- ✅ Express Entry Federal Draws
- ✅ Alberta Economy Indicators
- ✅ Labor Market Statistics
- ✅ Job Bank Posting Trends

---

## 🆘 Troubleshooting

```bash
# Check for errors in last run
sudo journalctl -u aaip-scraper.service -n 50 | grep -i error
sudo journalctl -u aaip-extended-collectors.service -n 50 | grep -i error

# Check timer is enabled (should say "enabled")
sudo systemctl is-enabled aaip-scraper.timer
sudo systemctl is-enabled aaip-extended-collectors.timer

# Reload systemd if you modified service files
sudo systemctl daemon-reload
```

---

## 📍 Key Files

- Service definitions: `/etc/systemd/system/aaip-*.service`
- Timer definitions: `/etc/systemd/system/aaip-*.timer`
- Collector scripts: `/home/randy/deploy/aaip-data/scraper/`
- Orchestrator: `collect_all_data.py` (hourly) and `collect_extended_data.py` (daily)

---

**Quick Copy-Paste:**

```bash
# Full status check
sudo systemctl list-timers | grep aaip && \
sudo systemctl status aaip-scraper.timer --no-pager && \
sudo systemctl status aaip-extended-collectors.timer --no-pager

# View both logs
sudo journalctl -u aaip-scraper.service -u aaip-extended-collectors.service -f

# Restart both timers
sudo systemctl restart aaip-scraper.timer && \
sudo systemctl restart aaip-extended-collectors.timer
```
