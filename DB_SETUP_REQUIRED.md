# Database Setup Instructions

The database user `randy` needs CREATE privileges to set up the tables.

## Option 1: Ask your DBA to run this (Recommended)

Connect as superuser (postgres) and run:

```sql
-- Connect to the database
\c aaip_data_trend_dev_db

-- Grant schema permissions
GRANT CREATE ON SCHEMA public TO randy;
GRANT ALL PRIVILEGES ON SCHEMA public TO randy;

-- Create tables
CREATE TABLE IF NOT EXISTS aaip_summary (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    nomination_allocation INTEGER,
    nominations_issued INTEGER,
    nomination_spaces_remaining INTEGER,
    applications_to_process INTEGER,
    last_updated TEXT,
    UNIQUE(timestamp)
);

CREATE TABLE IF NOT EXISTS scrape_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    message TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_aaip_summary_timestamp ON aaip_summary(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_scrape_log_timestamp ON scrape_log(timestamp DESC);

-- Grant permissions to randy
GRANT ALL PRIVILEGES ON TABLE aaip_summary TO randy;
GRANT ALL PRIVILEGES ON TABLE scrape_log TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE aaip_summary_id_seq TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE scrape_log_id_seq TO randy;
```

## Option 2: Run via psql (if you have superuser access)

```bash
PGPASSWORD='superuser_password' psql -h 100.77.247.113 -p 5432 -U postgres -d aaip_data_trend_dev_db -f setup_db.sql
```

## After Setup

Once tables are created, the scraper and backend will work with the randy user.

## Test Connection

```bash
cd scraper
python3 scraper_pg.py
```

## If Tables Already Exist

If the DBA already created the tables, just make sure randy has permissions:

```sql
GRANT ALL PRIVILEGES ON TABLE aaip_summary TO randy;
GRANT ALL PRIVILEGES ON TABLE scrape_log TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE aaip_summary_id_seq TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE scrape_log_id_seq TO randy;
```
