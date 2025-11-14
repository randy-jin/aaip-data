-- Database schema for AAIP draws tracking
-- This extends the existing schema to support incremental draw data collection

-- Create draws table for historical draw records
CREATE TABLE IF NOT EXISTS aaip_draws (
    id SERIAL PRIMARY KEY,
    draw_date DATE NOT NULL,
    draw_number VARCHAR(50),  -- AAIP draw number if available
    stream_category TEXT NOT NULL,  -- Main category (e.g., "Alberta Opportunity Stream")
    stream_detail TEXT,  -- Sub-category (e.g., "Construction", "Agriculture")
    min_score INTEGER,
    invitations_issued INTEGER,
    applications_received INTEGER,  -- For future use if data becomes available
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Ensure uniqueness based on draw date and stream details
    UNIQUE(draw_date, stream_category, stream_detail)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_draws_date ON aaip_draws(draw_date DESC);
CREATE INDEX IF NOT EXISTS idx_draws_category ON aaip_draws(stream_category);
CREATE INDEX IF NOT EXISTS idx_draws_category_date ON aaip_draws(stream_category, draw_date DESC);
CREATE INDEX IF NOT EXISTS idx_draws_created ON aaip_draws(created_at DESC);

-- Create a view for easy querying of draw trends
CREATE OR REPLACE VIEW draw_trends AS
SELECT 
    stream_category,
    stream_detail,
    DATE_TRUNC('month', draw_date) as month,
    DATE_TRUNC('year', draw_date) as year,
    COUNT(*) as draw_count,
    AVG(min_score) as avg_min_score,
    MIN(min_score) as lowest_score,
    MAX(min_score) as highest_score,
    SUM(invitations_issued) as total_invitations,
    AVG(invitations_issued) as avg_invitations
FROM aaip_draws
GROUP BY stream_category, stream_detail, month, year
ORDER BY year DESC, month DESC;

-- Update scrape_log to track draws collection
ALTER TABLE scrape_log ADD COLUMN IF NOT EXISTS draws_collected INTEGER DEFAULT 0;
ALTER TABLE scrape_log ADD COLUMN IF NOT EXISTS new_draws_added INTEGER DEFAULT 0;

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE aaip_draws TO randy;
GRANT ALL PRIVILEGES ON SEQUENCE aaip_draws_id_seq TO randy;
GRANT SELECT ON draw_trends TO randy;

-- Add comments for documentation
COMMENT ON TABLE aaip_draws IS 'Historical AAIP draw records with incremental updates';
COMMENT ON COLUMN aaip_draws.stream_category IS 'Main stream category (e.g., Alberta Opportunity Stream)';
COMMENT ON COLUMN aaip_draws.stream_detail IS 'Specific pathway or sector (e.g., Construction, Tech)';
COMMENT ON COLUMN aaip_draws.min_score IS 'Minimum score of invited candidates';
COMMENT ON COLUMN aaip_draws.invitations_issued IS 'Number of invitations issued in this draw';
