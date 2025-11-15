-- Enhanced database schema for multi-stream tracking

-- Drop existing tables if recreating
-- DROP TABLE IF EXISTS stream_data CASCADE;
-- DROP TABLE IF EXISTS aaip_summary CASCADE;
-- DROP TABLE IF EXISTS scrape_log CASCADE;

-- Main summary table (keep for overall totals)
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

-- New table for individual stream data
CREATE TABLE IF NOT EXISTS stream_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    stream_name TEXT NOT NULL,
    stream_type TEXT NOT NULL, -- 'main', 'sub-pathway'
    parent_stream TEXT, -- For sub-pathways
    nomination_allocation INTEGER,
    nominations_issued INTEGER,
    nomination_spaces_remaining INTEGER,
    applications_to_process INTEGER,
    processing_date TEXT,
    last_updated TEXT,
    UNIQUE(timestamp, stream_name)
);

-- Scrape log table
CREATE TABLE IF NOT EXISTS scrape_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    streams_collected INTEGER
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_aaip_summary_timestamp ON aaip_summary(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stream_data_timestamp ON stream_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stream_data_stream_name ON stream_data(stream_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stream_data_type ON stream_data(stream_type);
CREATE INDEX IF NOT EXISTS idx_scrape_log_timestamp ON scrape_log(timestamp DESC);

-- Grant permissions to randy
GRANT ALL PRIVILEGES ON TABLE aaip_summary TO randy;
GRANT ALL PRIVILEGES ON TABLE stream_data TO randy;
GRANT ALL PRIVILEGES ON TABLE scrape_log TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE aaip_summary_id_seq TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE stream_data_id_seq TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE scrape_log_id_seq TO randy;
