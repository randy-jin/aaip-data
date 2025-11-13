# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AAIP Data Tracker is a full-stack application that scrapes, stores, and visualizes Alberta Advantage Immigration Program (AAIP) processing information trends. The system tracks nomination allocations, applications processed, and remaining spaces over time for the overall program and individual immigration streams.

**Data Source**: https://www.alberta.ca/aaip-processing-information

## Branch Strategy

- **main**: Primary development branch - all development happens here
- **test**: Testing/staging branch - manually merge main → test after verification
- **Deployment**: Pushing to `test` branch triggers automatic deployment to test server via GitHub Actions

## Architecture

### Three-Component System

1. **Scraper** (`scraper/`): Python scripts that scrape AAIP data from the Alberta government website
2. **Backend** (`backend/`): FastAPI REST API that serves historical data
3. **Frontend** (`frontend/`): React dashboard with Recharts visualizations

### Database Variants

The project supports both SQLite (local development) and PostgreSQL (production):

- **SQLite files**: `scraper.py`, `main.py` - Use local `data/aaip_data.db`
- **PostgreSQL files**: `scraper_pg.py`, `main_pg.py` - Connect to PostgreSQL via environment variables
- **Enhanced files**: `scraper_enhanced.py`, `main_enhanced.py` - PostgreSQL + multi-stream support (tracks individual immigration streams like Express Entry, Rural Renewal, etc.)

The enhanced version adds multi-stream tracking with these database tables:
- `aaip_summary`: Overall program summary (2025 summary data)
- `stream_data`: Individual stream details (Alberta Opportunity Stream, Express Entry, Rural Renewal, etc.)
- `scrape_log`: Scraping activity logs

## Development Commands

### Scraper

```bash
cd scraper
pip install -r requirements.txt

# Run basic scraper (SQLite)
python scraper.py

# Run PostgreSQL scraper
python scraper_pg.py

# Run enhanced multi-stream scraper
python scraper_enhanced.py
```

### Backend

```bash
cd backend
pip install -r requirements.txt

# Run with auto-reload (SQLite)
uvicorn main:app --reload --port 8000

# Run PostgreSQL version
uvicorn main_pg:app --reload --port 8000

# Run enhanced multi-stream version
uvicorn main_enhanced:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Development server (runs on port 3002)
npm run dev

# Production build
npm run build

# Preview production build
npm preview
```

## Environment Configuration

Both scraper and backend require `.env` files. See `.env.example` in each directory.

**PostgreSQL connection** (for `_pg.py` and `_enhanced.py` files):
```
DATABASE_URL=postgresql://user:password@host:port/dbname
# OR individual parameters:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aaip_data
DB_USER=username
DB_PASSWORD=password
```

**Frontend** (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000
```

## API Endpoints

### Basic Endpoints (all versions)
- `GET /`: API information
- `GET /api/stats`: Database statistics and latest data
- `GET /api/summary`: Historical summary data (paginated)
- `GET /api/summary/latest`: Most recent summary
- `GET /api/logs`: Scrape logs

### Enhanced Multi-Stream Endpoints (main_enhanced.py only)
- `GET /api/streams/list`: Available stream names
- `GET /api/streams/{stream_name}`: Historical data for specific stream
- `GET /api/streams`: All stream data with filtering

## CI/CD

GitHub Actions workflow (`.github/workflows/test-deploy.yml`) handles:
- **Testing**: Python module validation, frontend build
- **Deployment**: Via Cloudflare Tunnel to test server using SSH
  - Deploys backend, frontend, and scraper updates
  - Restarts systemd service `aaip-backend-test`
  - Copies frontend build to `/var/www/aaip-test/`
  - Runs health checks on both endpoints

**Branch**: `test` (deployment target)
**Main branch**: Not specified (PRs typically target main)

### Deployment Requirements

**Server Configuration**:
- Cloudflare Tunnel running (`ssh.randy.it.com`)
- SSH key authentication configured for deploy user
- Sudo permissions for service restart (configured in `/etc/sudoers.d/aaip-deploy`):
  ```
  randy ALL=(ALL) NOPASSWD: /bin/systemctl restart aaip-backend-test
  randy ALL=(ALL) NOPASSWD: /bin/systemctl status aaip-backend-test
  randy ALL=(ALL) NOPASSWD: /bin/cp -r * /var/www/aaip-test/*
  ```

## Key Technical Details

### Scraper Behavior
- Extracts data from the "2025 summary" table on the Alberta government website
- Uses BeautifulSoup with lxml parser
- Handles "Less than 10" values by converting to 5 (in enhanced version)
- Prevents duplicate hourly records with UNIQUE constraint on timestamp
- Enhanced version scrapes multiple streams and pathways from the same page

### Frontend Architecture
- Uses Vite as build tool
- API base URL configured via `VITE_API_URL` environment variable (src/api.js:3)
- Recharts for time-series line charts
- date-fns for timestamp formatting
- Supports stream selection dropdown for viewing individual immigration streams (enhanced version)

### Database Schema
- SQLite for local development (`data/aaip_data.db`)
- PostgreSQL for production deployment
- Enhanced schema includes `stream_data` table with `stream_name`, `stream_type`, and `parent_stream` fields

## Testing in CI/CD
The CI tests are basic validation:
- Python: Module import tests (`python3 -c "import module"`)
- Frontend: Build test (`npm run build && test -d dist`)

No unit test framework is configured.
