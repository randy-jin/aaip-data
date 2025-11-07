# Multi-Stream Feature - Database Setup Required

## What's New

The scraper has been enhanced to collect data from **8 different AAIP streams**:

1. **Alberta Opportunity Stream**
2. **Rural Renewal Stream**
3. **Tourism and Hospitality Stream**
4. **Dedicated Health Care Pathways**
5. **Express Entry - Accelerated Tech Pathway**
6. **Express Entry - Law Enforcement Pathway**
7. **Express Entry - Priority Sectors**
8. **Entrepreneur Streams**

## Database Table Needed

Please ask your DBA to run this SQL as a superuser (postgres):

```sql
-- Connect to database
\c aaip_data_trend_dev_db

-- Create stream_data table
CREATE TABLE IF NOT EXISTS stream_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    stream_name TEXT NOT NULL,
    stream_type TEXT NOT NULL,
    parent_stream TEXT,
    nomination_allocation INTEGER,
    nominations_issued INTEGER,
    nomination_spaces_remaining INTEGER,
    applications_to_process INTEGER,
    processing_date TEXT,
    last_updated TEXT,
    UNIQUE(timestamp, stream_name)
);

-- Create indexes
CREATE INDEX idx_stream_data_timestamp ON stream_data(timestamp DESC);
CREATE INDEX idx_stream_data_stream_name ON stream_data(stream_name, timestamp DESC);
CREATE INDEX idx_stream_data_type ON stream_data(stream_type);

-- Grant permissions to randy
GRANT ALL PRIVILEGES ON TABLE stream_data TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE stream_data_id_seq TO randy;

-- Add streams_collected column to scrape_log
ALTER TABLE scrape_log ADD COLUMN IF NOT EXISTS streams_collected INTEGER DEFAULT 0;
```

## Or Run This Command

```bash
PGPASSWORD='superuser_password' psql -h 100.77.247.113 -p 5432 -U postgres -d aaip_data_trend_dev_db -f setup_db_enhanced.sql
```

## After Table Creation

Test the enhanced scraper:
```bash
cd scraper
python3 scraper_enhanced.py
```

## What You'll Get

- Historical data for each stream independently
- Ability to compare trends across different streams
- More detailed insights into AAIP processing

## Files Created

- `scraper/scraper_enhanced.py` - Enhanced multi-stream scraper
- `setup_db_enhanced.sql` - Database schema for multi-stream support
