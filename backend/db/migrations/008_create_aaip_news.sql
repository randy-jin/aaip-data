-- AAIP News/Updates Table
-- Stores news articles from https://www.alberta.ca/aaip-updates
-- with both English (original) and Chinese (translated) versions

CREATE TABLE IF NOT EXISTS aaip_news (
    id SERIAL PRIMARY KEY,

    -- English version (original from government website)
    title_en TEXT NOT NULL,
    content_en TEXT NOT NULL,

    -- Chinese version (translated)
    title_zh TEXT NOT NULL,
    content_zh TEXT NOT NULL,

    -- Metadata
    published_date DATE NOT NULL,
    source_url VARCHAR(500) DEFAULT 'https://www.alberta.ca/aaip-updates',

    -- Tracking
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Prevent duplicate news entries
    UNIQUE(published_date, title_en)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_aaip_news_published_date ON aaip_news(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_aaip_news_scraped_at ON aaip_news(scraped_at DESC);

-- Comments for documentation
COMMENT ON TABLE aaip_news IS 'AAIP news and updates from official Alberta government website, with English and Chinese translations';
COMMENT ON COLUMN aaip_news.title_en IS 'Original English title from government website';
COMMENT ON COLUMN aaip_news.title_zh IS 'Simplified Chinese translation of title';
COMMENT ON COLUMN aaip_news.content_en IS 'Original English content/summary';
COMMENT ON COLUMN aaip_news.content_zh IS 'Simplified Chinese translation of content';
COMMENT ON COLUMN aaip_news.published_date IS 'Official publication date from the news article';
COMMENT ON COLUMN aaip_news.source_url IS 'URL to the official government news source';
