-- Add EOI (Expression of Interest) Pool tracking
-- This table tracks the number of candidates waiting in the EOI pool for each stream over time

CREATE TABLE IF NOT EXISTS eoi_pool (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    stream_name TEXT NOT NULL,
    candidate_count INTEGER NOT NULL,
    last_updated TEXT,  -- Last updated date from website
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Index for efficient queries
    UNIQUE(timestamp, stream_name)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_eoi_timestamp ON eoi_pool(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_eoi_stream ON eoi_pool(stream_name);
CREATE INDEX IF NOT EXISTS idx_eoi_stream_timestamp ON eoi_pool(stream_name, timestamp DESC);

-- Create view for EOI trends analysis
CREATE OR REPLACE VIEW eoi_trends AS
SELECT
    stream_name,
    DATE_TRUNC('day', timestamp) as day,
    DATE_TRUNC('week', timestamp) as week,
    DATE_TRUNC('month', timestamp) as month,
    AVG(candidate_count) as avg_candidates,
    MIN(candidate_count) as min_candidates,
    MAX(candidate_count) as max_candidates,
    COUNT(*) as data_points
FROM eoi_pool
GROUP BY stream_name, day, week, month
ORDER BY stream_name, day DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE eoi_pool TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE eoi_pool_id_seq TO randy;
GRANT SELECT ON eoi_trends TO randy;

-- Add comments for documentation
COMMENT ON TABLE eoi_pool IS 'Expression of Interest pool statistics showing candidate counts by stream over time';
COMMENT ON COLUMN eoi_pool.stream_name IS 'Name of the stream/pathway (e.g., Alberta Opportunity Stream)';
COMMENT ON COLUMN eoi_pool.candidate_count IS 'Number of candidates in the EOI pool for this stream';
COMMENT ON COLUMN eoi_pool.timestamp IS 'When this data was collected';
COMMENT ON COLUMN eoi_pool.last_updated IS 'Last updated date from the AAIP website';
