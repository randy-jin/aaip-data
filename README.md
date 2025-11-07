# AAIP Data Tracker

A full-stack application to track and visualize Alberta Advantage Immigration Program (AAIP) processing information trends over time.

## Features

- **Automated Data Collection**: Scrapes AAIP data every hour
- **Historical Tracking**: Stores historical data to show trends
- **Visual Dashboard**: Line charts showing changes in:
  - 2025 nomination allocation
  - 2025 nominations issued
  - 2025 nomination spaces remaining
  - Applications to be processed

## Tech Stack

### Backend
- Python 3.11+
- BeautifulSoup4 for web scraping
- FastAPI for REST API
- SQLite for data storage
- Schedule for periodic tasks

### Frontend
- React 18
- Chart.js/Recharts for visualizations
- Tailwind CSS for styling
- Axios for API calls

### Deployment
- GitHub Actions for scheduled scraping
- Railway/Render for backend
- Vercel/Netlify for frontend

## Project Structure

```
aaip-data/
├── scraper/          # Python web scraper
├── backend/          # FastAPI REST API
├── frontend/         # React dashboard
├── data/             # SQLite database
└── .github/workflows # GitHub Actions config
```

## Quick Start

### Scraper
```bash
cd scraper
pip install -r requirements.txt
python scraper.py
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:3002`

## Data Source

https://www.alberta.ca/aaip-processing-information
