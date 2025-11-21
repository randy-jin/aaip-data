# EOI Pool Data Deduplication - Next Steps

## What Was Changed

Modified `scraper/scraper.py` to automatically skip saving EOI pool data if it's identical to the most recent record.

### Deduplication Logic
```python
# Check if data actually changed
cursor.execute("""
    SELECT eoi_data FROM eoi_pool_data 
    ORDER BY timestamp DESC LIMIT 1
""")
recent = cursor.fetchone()
if recent and recent[0] == json.dumps(eoi_data, sort_keys=True):
    print(f"⏭️  Skipping EOI pool data - identical to previous record")
    return
```

## What You Should Do Next

### Option 1: Test Locally (Recommended First)
```bash
cd scraper
python3 scraper.py
```

Check the output - if EOI data hasn't changed, you'll see:
```
⏭️  Skipping EOI pool data - identical to previous record
```

### Option 2: Deploy to Test Server

Since you're already running **aaip-scraper.service** with **aaip-scraper.timer** (hourly), you just need to:

1. **Push code to test branch**:
```bash
git add scraper/scraper.py
git commit -m "feat: add EOI pool data deduplication"
git push origin main
git checkout test
git merge main
git push origin test  # Triggers deployment
```

2. **No need for new services!** 
   - ❌ DON'T create `aaip-eoi-pool-collector.service`
   - ✅ Existing `aaip-scraper.service` already runs hourly
   - ✅ It calls `collect_all_data.py` → `scraper.py` (includes EOI pool)

3. **After deployment, verify on server**:
```bash
ssh your-server
sudo systemctl status aaip-scraper.timer
sudo journalctl -u aaip-scraper.service -f  # Watch next run
```

## Architecture Clarification

```
aaip-scraper.timer (hourly)
    ↓
aaip-scraper.service
    ↓
collect_all_data.py (orchestrator)
    ↓
    ├── scraper.py ✅ (AAIP processing + draws + EOI pool - NOW WITH DEDUPLICATION)
    ├── aaip_news_scraper.py
    ├── express_entry_collector.py
    ├── alberta_economy_collector.py
    ├── quarterly_labor_market_collector.py
    ├── job_bank_scraper.py
    └── trend_analysis_engine.py
```

## Expected Behavior

- **First hour**: EOI pool data saved (e.g., 100 records in General category)
- **Second hour**: If data unchanged → skipped, log shows "⏭️  Skipping..."
- **Third hour**: If data changed (e.g., 105 records) → saved new record

This reduces database growth from **24 records/day** to **~2-3 records/day** (only when data actually changes).

## Verification Query

After a few hours, check database:
```sql
SELECT timestamp, eoi_data 
FROM eoi_pool_data 
ORDER BY timestamp DESC 
LIMIT 10;
```

You should see gaps in timestamps where unchanged data was skipped.
