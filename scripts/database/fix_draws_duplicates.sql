-- Fix duplicate draws issue
-- Problem: UNIQUE(draw_date, stream_category, stream_detail) treats NULL as unique
-- Solution: Use COALESCE to treat NULL stream_detail as empty string in unique constraint

-- Step 1: Remove duplicate entries (keep the earliest created_at)
DELETE FROM aaip_draws a
USING aaip_draws b
WHERE a.id > b.id
  AND a.draw_date = b.draw_date
  AND a.stream_category = b.stream_category
  AND (a.stream_detail = b.stream_detail OR (a.stream_detail IS NULL AND b.stream_detail IS NULL));

-- Step 2: Drop old unique constraint
ALTER TABLE aaip_draws DROP CONSTRAINT IF EXISTS aaip_draws_draw_date_stream_category_stream_detail_key;

-- Step 3: Create unique index that treats NULL properly
-- Using COALESCE to convert NULL to empty string for uniqueness check
CREATE UNIQUE INDEX IF NOT EXISTS idx_draws_unique
ON aaip_draws (draw_date, stream_category, COALESCE(stream_detail, ''));

-- Step 4: Verify no duplicates remain
SELECT
    draw_date,
    stream_category,
    COALESCE(stream_detail, 'NULL') as detail,
    COUNT(*) as count
FROM aaip_draws
GROUP BY draw_date, stream_category, stream_detail
HAVING COUNT(*) > 1;

-- If the above query returns any rows, there are still duplicates
