# AAIP Data Tracker - Setup Guide

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Clone and Setup Scraper

```bash
# Install Python dependencies
cd scraper
pip install -r requirements.txt

# Run the scraper once to initialize database
python3 scraper.py
```

### 2. Start Backend API

```bash
# Install FastAPI dependencies
cd backend
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 3. Start Frontend

```bash
# Install npm dependencies
cd frontend
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3002`

## API Endpoints

- `GET /api/stats` - Get database statistics and latest data
- `GET /api/summary?limit=100&offset=0` - Get historical data with pagination
- `GET /api/summary/latest` - Get most recent data point
- `GET /api/logs?limit=50` - Get scraper logs

## Automated Scraping

### Option 1: GitHub Actions (Recommended)

The project includes a GitHub Actions workflow that runs every hour:

1. Push the repository to GitHub
2. The workflow in `.github/workflows/scraper.yml` will run automatically
3. Data is committed back to the repository

### Option 2: Local Cron Job

Add to your crontab:

```bash
0 * * * * cd /path/to/aaip-data/scraper && /usr/bin/python3 scraper.py
```

### Option 3: Python Schedule

Create a `scheduler.py`:

```python
import schedule
import time
import subprocess

def run_scraper():
    subprocess.run(["python3", "scraper.py"], cwd="./scraper")

schedule.every().hour.do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Deployment

### Backend Deployment (Railway/Render)

1. Create a `Procfile` in backend directory:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Push to Railway or Render
3. Set environment variables if needed

### Frontend Deployment (Vercel/Netlify)

1. Set build command: `npm run build`
2. Set output directory: `dist`
3. Set environment variable:
   - `VITE_API_URL=https://your-backend-url.com`

### Database

For production, consider:
- PostgreSQL instead of SQLite
- Backing up the SQLite file regularly
- Using a managed database service

## Monitoring

Check scraper logs:
```bash
sqlite3 data/aaip_data.db "SELECT * FROM scrape_log ORDER BY timestamp DESC LIMIT 10;"
```

Check data count:
```bash
sqlite3 data/aaip_data.db "SELECT COUNT(*) FROM aaip_summary;"
```

## Troubleshooting

### Scraper fails
- Check internet connection
- Verify the AAIP website structure hasn't changed
- Check scraper logs in database

### Backend fails
- Ensure database file exists at `../data/aaip_data.db`
- Check file permissions
- Verify all dependencies are installed

### Frontend fails to load data
- Verify backend is running
- Check CORS settings in backend
- Verify API_URL environment variable

## Development

### Run tests (if added later)
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Add more data streams

To track additional AAIP streams, modify:
1. `scraper/scraper.py` - Add scraping logic
2. `backend/main.py` - Add API endpoints
3. `frontend/src/App.jsx` - Add visualizations

## License

MIT
