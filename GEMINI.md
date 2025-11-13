# Project Overview

This is a full-stack application designed to track and visualize trends in the Alberta Advantage Immigration Program (AAIP) processing information. It automatically scrapes data from the official AAIP website, stores it, and presents it on a dashboard.

## Architecture

The project is composed of three main parts:

1.  **Scraper**: A Python script (`scraper/scraper_pg.py`) that runs periodically to collect data from the AAIP website. It uses `BeautifulSoup` for web scraping.
2.  **Backend**: A Python FastAPI server (`backend/main_pg.py`) that exposes a REST API to provide the collected data to the frontend.
3.  **Frontend**: A React application (`frontend/`) that visualizes the data using charts. It is built with Vite and styled with Tailwind CSS.

The data is stored in a PostgreSQL database.

## Building and Running

### Prerequisites

*   Python 3.11+
*   Node.js and npm
*   PostgreSQL

### 1. Database Setup

Follow the instructions in `POSTGRESQL_SETUP.md` to set up the PostgreSQL database. This includes creating a database, a user, and setting the `DATABASE_URL` environment variable in `.env` files for both the backend and the scraper.

### 2. Scraper

To run the scraper and collect the initial data:

```bash
cd scraper
pip install -r requirements.txt
python scraper_pg.py
```

### 3. Backend

To start the backend API server:

```bash
cd backend
pip install -r requirements.txt
uvicorn main_pg:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 4. Frontend

To run the frontend application:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be accessible at `http://localhost:5173` (or another port if 5173 is in use, check the output of `npm run dev`).

## Development Conventions

*   The project uses different files for SQLite and PostgreSQL. The `_pg.py` files are for PostgreSQL.
*   Environment variables are used for configuration. See the `.env.example` files in the `backend` and `scraper` directories.
*   The frontend uses `vite` for development and building.
*   GitHub Actions are used for CI/CD, as indicated by the `.github/workflows` directory.
