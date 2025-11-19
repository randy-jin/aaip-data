-- Success Stories Table
CREATE TABLE IF NOT EXISTS success_stories (
    id SERIAL PRIMARY KEY,
    story_type VARCHAR(50) NOT NULL,
    aaip_stream VARCHAR(100) NOT NULL,
    timeline_submitted DATE,
    timeline_nominated DATE,
    timeline_pr_approved DATE,
    noc_code VARCHAR(10),
    crs_score INTEGER,
    work_permit_type VARCHAR(50),
    city VARCHAR(100),
    story_text TEXT NOT NULL,
    tips TEXT,
    challenges TEXT,
    author_name VARCHAR(100),
    is_anonymous BOOLEAN DEFAULT true,
    email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_success_stories_status ON success_stories(status);
CREATE INDEX IF NOT EXISTS idx_success_stories_stream ON success_stories(aaip_stream);
CREATE INDEX IF NOT EXISTS idx_success_stories_created ON success_stories(created_at DESC);

CREATE TABLE IF NOT EXISTS story_helpful_votes (
    id SERIAL PRIMARY KEY,
    story_id INTEGER REFERENCES success_stories(id) ON DELETE CASCADE,
    voter_ip VARCHAR(45),
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(story_id, voter_ip)
);
