# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AAIP Data Tracker - A comprehensive full-stack application that tracks and visualizes Alberta Advantage Immigration Program (AAIP) data, including processing times, draw history, labor market indicators, and Express Entry comparisons.

**Primary Data Source**: https://www.alberta.ca/aaip-processing-information

## Technology Stack

- **Backend**: FastAPI (Python 3.11+) with PostgreSQL
- **Frontend**: React 18 + Vite + TailwindCSS + Recharts
- **Data Collection**: BeautifulSoup4 + requests (scheduled scraping)
- **Deployment**: GitHub Actions → Cloudflare Tunnel → systemd services

## Branch Strategy

- **main**: Primary development branch - all feature development happens here
- **test**: Testing/staging branch - manually merge main → test after verification
- **Deployment**: Push to `test` branch triggers automatic deployment via GitHub Actions

## Development Commands

### Backend Development

```bash
cd backend
pip install -r requirements.txt

# Run current backend (with draws support)
uvicorn main_draws:app --reload --port 8000

# Run PostgreSQL version (basic)
uvicorn main_pg:app --reload --port 8000

# Run database migrations
python run_migrations.py
```

### Scraper Operations

```bash
cd scraper
pip install -r requirements.txt

# AUTOMATED COLLECTION (Recommended)
# Run all collectors in sequence with orchestrator
python3 collect_all_data.py

# Or use the setup script for automation
./setup_automation.sh

# MANUAL COLLECTION (Individual Scripts)
python scraper.py                              # Main AAIP processing info + draw records
python aaip_news_scraper.py                    # News updates from /aaip-updates
python express_entry_collector.py              # Federal EE draw data
python alberta_economy_collector.py            # Economic indicators
python quarterly_labor_market_collector.py     # Labor market data
python job_bank_scraper.py                     # Job Bank data
python trend_analysis_engine.py                # Trend analysis

# Testing
python test_collectors.py                      # Test all collectors can import

# Seed sample data
python seed_success_stories.py
```

### Frontend Development

```bash
cd frontend
npm install

# Development server (port 3002)
npm run dev

# Production build
npm run build

# Preview build
npm preview
```

## Architecture

### Three-Tier System

1. **Data Collection Layer** (`scraper/`)
   - `collect_all_data.py`: **Orchestrator script** - runs all collectors hourly (automated)
   - `scraper.py`: Main scraper for AAIP processing info and draw records
   - `aaip_news_scraper.py`: News updates from https://www.alberta.ca/aaip-updates
   - `express_entry_collector.py`: Federal Express Entry comparison data
   - `alberta_economy_collector.py`: Provincial economic indicators
   - `quarterly_labor_market_collector.py`: Labor market statistics
   - `job_bank_scraper.py`: Job posting trends
   - `trend_analysis_engine.py`: Historical pattern analysis engine
   - `setup_automation.sh`: Helper script to set up automated collection
   - `test_collectors.py`: Test suite for all collectors

2. **API Layer** (`backend/`)
   - `main_draws.py`: Current production backend (v2.0.0) with full draw support
   - `main_pg.py`: Basic PostgreSQL backend (v1.0.0) - legacy
   - `main_enhanced.py`: Multi-stream enhanced version

3. **Presentation Layer** (`frontend/`)
   - Main App (`src/App.jsx`): Tab-based interface with summary and draws visualization
   - Components:
     - `DrawsVisualization.jsx`: Historical draw data charts
     - `EOIPoolVisualization.jsx`: Expression of Interest pool tracking
     - `SmartInsights.jsx`: AI-powered trend analysis and insights
     - `ToolsDashboard.jsx`: Application planning tools
     - `LaborMarketInsights.jsx`: Job market data visualization
     - `ExpressEntryComparison.jsx`: Federal vs. provincial comparison
     - `SuccessStories.jsx`: Anonymized success case studies
     - `WhatIfCalculator.jsx`: Score and timeline prediction tool
   - Pages:
     - `pages/Predictions.jsx`: Predictive analytics dashboard

### Database Schema (PostgreSQL)

**Core Tables:**
- `aaip_summary`: Overall program statistics (allocation, issued, remaining, applications)
- `stream_data`: Individual stream tracking (Alberta Opportunity, Express Entry, etc.)
- `aaip_draws`: Historical draw records with scores and invitation counts
- `scrape_log`: Scraping activity logs

**Extended Tables:**
- `express_entry_draws`: Federal EE draw comparison data
- `eoi_pool_data`: Expression of Interest pool statistics
- `alberta_economy`: Provincial economic indicators
- `labor_market_data`: Employment and wage statistics
- `success_stories`: Anonymized application success cases
- `job_postings`: Job Bank scraping results

## API Endpoints

### Core Endpoints (main_draws.py)

**Summary Data:**
- `GET /`: API information and version
- `GET /api/stats`: Database statistics and latest snapshot
- `GET /api/summary`: Historical summary data (paginated)
- `GET /api/summary/latest`: Most recent summary
- `GET /api/logs`: Scrape logs

**Draw Data:**
- `GET /api/draws`: All historical draws (filterable by stream, date range)
- `GET /api/draws/latest`: Most recent draws
- `GET /api/draws/stats`: Draw statistics by stream
- `GET /api/draws/streams`: Available stream categories

**Stream Data:**
- `GET /api/streams/list`: Available stream names
- `GET /api/streams/{stream_name}`: Historical data for specific stream
- `GET /api/streams`: All stream data with filtering

**Extended Features:**
- `GET /api/insights/weekly`: Smart insights and trend analysis
- `GET /api/predictions`: Score and timeline predictions
- `GET /api/express-entry/comparison`: Federal vs. AAIP comparison
- `GET /api/labor-market`: Labor market indicators
- `GET /api/success-stories`: Success case studies

## Environment Configuration

**Backend** (`backend/.env`):
```bash
# PostgreSQL connection (required)
DATABASE_URL=postgresql://user:password@host:port/dbname
# OR individual parameters:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aaip_data
DB_USER=username
DB_PASSWORD=password
```

**Scraper** (`scraper/.env`):
```bash
# Same as backend - shares database
DATABASE_URL=postgresql://user:password@host:port/dbname
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Key Technical Details

### Scraper Behavior

- **Main Scraper** (`scraper.py`): Consolidated scraper that collects both:
  1. 2025 Summary table (allocations, issued, remaining, applications)
  2. Draw records table (historical draws with scores and invitations)
- **Stream Categorization**: Automatically categorizes streams into main categories and subcategories:
  - Alberta Opportunity Stream
  - Alberta Express Entry Stream
  - Dedicated Health Care Pathway
  - Tourism and Hospitality Stream
  - Rural Renewal Stream
- **Data Handling**:
  - Converts "Less than 10" to `n-1` (e.g., "Less than 10" → 9)
  - Uses UNIQUE constraints to prevent duplicate records
  - Logs all scraping activity to `scrape_log` table

### Frontend Architecture

- **Build Tool**: Vite (development port 3002)
- **State Management**: React hooks (useState, useEffect)
- **Data Fetching**: Axios via `src/api.js` (uses `VITE_API_BASE_URL`)
- **Visualization**: Recharts for all charts and graphs
- **Internationalization**: react-i18next for multi-language support
- **Date Handling**: date-fns for formatting and parsing
- **Styling**: TailwindCSS + custom components
- **Icons**: Heroicons React

### CI/CD Pipeline

**Workflow**: `.github/workflows/test-deploy.yml`

**Test Phase:**
- Python module import validation
- Frontend build verification
- No unit tests configured

**Deployment Phase** (test branch only):
1. Connect via Cloudflare Tunnel (`ssh.randy.it.com`)
2. Pull latest code from test branch
3. Update backend dependencies (venv)
4. Restart `aaip-backend-test` systemd service
5. Build and deploy frontend to `/var/www/aaip-test/`
6. Update scraper dependencies

**Server Requirements:**
- Cloudflare Tunnel configured for SSH
- Deploy user with sudo permissions (configured in `/etc/sudoers.d/aaip-deploy`)
- Systemd services: `aaip-backend-test`, `aaip-scraper.service`, `aaip-scraper.timer`

## Common Workflows

### Deploying Code Changes

```bash
# 1. Develop and test on main branch
git checkout main
# ... make changes ...
git add .
git commit -m "your changes"
git push origin main

# 2. Merge to test branch for deployment
git checkout test
git merge main
git push origin test  # Triggers automatic deployment

# OR use the helper script on server
./deployment/update.sh
```

### Running Scraper Manually

```bash
# On server
sudo systemctl start aaip-scraper.service

# Check logs
sudo journalctl -u aaip-scraper.service -f
```

### Checking Service Status

```bash
# Backend status
sudo systemctl status aaip-backend-test
sudo journalctl -u aaip-backend-test -f

# Scraper timer status
sudo systemctl status aaip-scraper.timer
sudo systemctl list-timers aaip-scraper.timer
```

### Database Operations

```bash
# Connect to database
sudo -u postgres psql aaip_data

# Check recent data
SELECT * FROM aaip_summary ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM stream_data ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM aaip_draws ORDER BY draw_date DESC LIMIT 10;

# View scrape logs
SELECT * FROM scrape_log ORDER BY timestamp DESC LIMIT 20;
```

## Important Notes

### Current Backend Version

The production backend is `main_draws.py` (v2.0.0), which supports:
- All legacy endpoints from v1.0.0
- Full draw record support
- Stream categorization
- Extended analytics endpoints

When working on backend features, modify `main_draws.py` unless specifically instructed otherwise.

### Frontend API Integration

The frontend's `src/api.js` exports all API functions. The base URL is configured via `import.meta.env.VITE_API_BASE_URL`. Components use these functions for data fetching, not direct fetch/axios calls.

### Multi-Language Support

The application supports English and Chinese (Simplified) via react-i18next. Translation keys are managed in `frontend/src/i18n/` (if exists) or inline. When adding new features, ensure text is wrapped with `t('key')` from `useTranslation()` hook.

### Testing Strategy

The project uses minimal automated testing:
- Python: Import validation only
- Frontend: Build success verification only
- No unit test framework (Jest, pytest) configured

Manual testing is the primary validation method before merging to test branch.

## Automated Data Collection

### Overview

The system has **two automated data collection pipelines**:

#### 1. Main Pipeline (Hourly)
Collects **critical, time-sensitive data** every hour:
- ✅ **AAIP Processing Info & Draw Records** - https://www.alberta.ca/aaip-processing-information
- ✅ **AAIP News Updates** - https://www.alberta.ca/aaip-updates (with Chinese translation)
- ✅ **Trend Analysis Engine** - Historical pattern analysis

**Orchestrator**: `scraper/collect_all_data.py`
**Timer**: `aaip-scraper.timer` (runs at :00 minutes every hour)

#### 2. Extended Pipeline (Daily)
Collects **supplementary data** once per day at 3:00 AM:
- ✅ **Express Entry Comparison** - Federal EE draw data (updates every 2 weeks, check daily)
- ✅ **Alberta Economy Indicators** - Provincial economic data
- ✅ **Labor Market Data** - Employment and wage statistics (quarterly)
- ✅ **Job Bank Postings** - Job market trends

**Orchestrator**: `scraper/collect_extended_data.py`
**Timer**: `aaip-extended-collectors.timer` (runs daily at 3:00 AM)

### Quick Setup - Local Testing

```bash
# Test main pipeline
cd scraper
python3 collect_all_data.py --verbose

# Test extended pipeline
python3 collect_extended_data.py --verbose

# Test specific extended collector
python3 collect_extended_data.py --collector express_entry -v
```

### Production Deployment

#### Main Pipeline Setup
```bash
# Already deployed - check status
sudo systemctl status aaip-scraper.timer
sudo systemctl list-timers | grep aaip
sudo journalctl -u aaip-scraper.service -f
```

#### Extended Pipeline Setup
```bash
# Deploy new timer
cd /home/randy/deploy/aaip-data
git pull origin test

sudo cp deployment/aaip-extended-collectors.service /etc/systemd/system/
sudo cp deployment/aaip-extended-collectors.timer /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable aaip-extended-collectors.timer
sudo systemctl start aaip-extended-collectors.timer

# Verify
sudo systemctl status aaip-extended-collectors.timer
sudo systemctl list-timers | grep extended

# Manual trigger
sudo systemctl start aaip-extended-collectors.service
sudo journalctl -u aaip-extended-collectors.service -f
```

### Monitoring Data Collection

```bash
# Main pipeline logs
sudo journalctl -u aaip-scraper.service --since today

# Extended pipeline logs
sudo journalctl -u aaip-extended-collectors.service --since today

# Check scrape history
psql -d aaip_data_trend_dev_db -c "SELECT * FROM scrape_log ORDER BY timestamp DESC LIMIT 10;"

# Check draw data
psql -d aaip_data_trend_dev_db -c "SELECT draw_date, stream_category, lowest_score FROM aaip_draws ORDER BY draw_date DESC LIMIT 10;"

# Check news
psql -d aaip_data_trend_dev_db -c "SELECT published_date, title_en FROM aaip_news ORDER BY published_date DESC LIMIT 10;"

# Check extended data
psql -d aaip_data_trend_dev_db -c "SELECT draw_date, crs_cutoff FROM express_entry_draws ORDER BY draw_date DESC LIMIT 5;"
psql -d aaip_data_trend_dev_db -c "SELECT recorded_date, indicator_name, value FROM alberta_economy ORDER BY recorded_date DESC LIMIT 5;"
```

**See `scraper/AUTOMATION_SETUP.md`, `scraper/AUTOMATION_SUMMARY.md`, and `scraper/EXTENDED_COLLECTORS_README.md` for complete documentation.**
