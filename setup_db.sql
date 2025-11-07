-- Grant schema permissions
GRANT ALL ON SCHEMA public TO randy;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO randy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO randy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO randy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO randy;

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

-- Grant permissions on new tables
GRANT ALL PRIVILEGES ON TABLE aaip_summary TO randy;
GRANT ALL PRIVILEGES ON TABLE scrape_log TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE aaip_summary_id_seq TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE scrape_log_id_seq TO randy;
