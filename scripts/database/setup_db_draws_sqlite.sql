-- Database schema for AAIP draws tracking (SQLite version)
-- This extends the existing schema to support incremental draw data collection

-- Create draws table for historical draw records
CREATE TABLE IF NOT EXISTS aaip_draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date DATE NOT NULL,
    draw_number TEXT,  -- AAIP draw number if available
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

-- Update scrape_log to track draw collection
-- Add new column if it doesn't exist
-- Note: SQLite doesn't support ALTER COLUMN, so we check if needed
CREATE TABLE IF NOT EXISTS scrape_log_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    records_processed INTEGER,
    draws_processed INTEGER DEFAULT 0,  -- New field for draw records
    error_message TEXT
);

-- Comment on usage
-- To update scrape_log if needed, manually add the column:
-- ALTER TABLE scrape_log ADD COLUMN draws_processed INTEGER DEFAULT 0;
