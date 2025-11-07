# PostgreSQL Setup Guide

## Prerequisites

Install PostgreSQL:

### macOS
```bash
brew install postgresql@16
brew services start postgresql@16
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Docker (Recommended for Development)
```bash
docker run --name aaip-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=aaip_data \
  -p 5432:5432 \
  -d postgres:16
```

## Database Setup

### 1. Create Database and User

Connect to PostgreSQL:
```bash
psql postgres
```

Create database and user:
```sql
CREATE DATABASE aaip_data;
CREATE USER aaip_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE aaip_data TO aaip_user;
\q
```

### 2. Configure Environment Variables

#### Scraper
Create `scraper/.env`:
```bash
DATABASE_URL=postgresql://aaip_user:your_secure_password@localhost:5432/aaip_data
```

#### Backend
Create `backend/.env`:
```bash
DATABASE_URL=postgresql://aaip_user:your_secure_password@localhost:5432/aaip_data
```

## Installation

### 1. Install Python Dependencies

```bash
# Scraper
cd scraper
pip install -r requirements.txt

# Backend
cd ../backend
pip install -r requirements.txt
```

### 2. Initialize Database

The scraper will automatically create tables on first run:

```bash
cd scraper
python3 scraper_pg.py
```

Or manually:
```bash
psql -U aaip_user -d aaip_data -c "
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

CREATE INDEX idx_aaip_summary_timestamp ON aaip_summary(timestamp DESC);
CREATE INDEX idx_scrape_log_timestamp ON scrape_log(timestamp DESC);
"
```

## Usage

### Run Scraper (PostgreSQL version)
```bash
cd scraper
python3 scraper_pg.py
```

### Run Backend API (PostgreSQL version)
```bash
cd backend
python3 -m uvicorn main_pg:app --reload
```

## Migration from SQLite

If you have existing SQLite data to migrate:

```bash
# Export from SQLite
sqlite3 data/aaip_data.db .dump > dump.sql

# Import to PostgreSQL (requires manual conversion)
# Or use a tool like pgloader
```

## Production Deployment

### Heroku
```bash
# Heroku automatically provides DATABASE_URL
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Railway
1. Add PostgreSQL plugin
2. Set DATABASE_URL environment variable (auto-provided)
3. Deploy

### AWS RDS / Azure / GCP
1. Create PostgreSQL instance
2. Get connection string
3. Set DATABASE_URL in your environment

## Database Maintenance

### Backup
```bash
pg_dump -U aaip_user aaip_data > backup.sql
```

### Restore
```bash
psql -U aaip_user aaip_data < backup.sql
```

### View Data
```bash
psql -U aaip_user -d aaip_data

# In psql:
SELECT * FROM aaip_summary ORDER BY timestamp DESC LIMIT 10;
SELECT COUNT(*) FROM aaip_summary;
\q
```

## Connection Pooling (Production)

For production, consider using connection pooling:

```python
from psycopg2 import pool

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
```

## Troubleshooting

### Connection refused
- Check if PostgreSQL is running: `pg_isready`
- Verify port 5432 is not blocked

### Authentication failed
- Check username and password in .env
- Verify user has correct privileges

### Database not found
- Create database: `createdb -U postgres aaip_data`

### Permission denied
- Grant privileges: `GRANT ALL ON DATABASE aaip_data TO aaip_user;`

## Performance Tips

1. **Indexes**: Already created on timestamp columns
2. **Vacuum**: Run `VACUUM ANALYZE;` periodically
3. **Connection pooling**: Use PgBouncer in production
4. **Monitoring**: Use pg_stat_statements for query analysis

## Security Best Practices

1. **Never commit .env files**: Already in .gitignore
2. **Use strong passwords**: Generate with `openssl rand -base64 32`
3. **Restrict network access**: Configure pg_hba.conf
4. **Use SSL**: Enable SSL in production
5. **Regular backups**: Automate with cron or cloud backups

## File Changes

Updated files for PostgreSQL:
- `scraper/scraper_pg.py` - New PostgreSQL scraper
- `backend/main_pg.py` - New PostgreSQL backend
- `scraper/requirements.txt` - Added psycopg2-binary
- `backend/requirements.txt` - Added psycopg2-binary, python-dotenv
- `scraper/.env.example` - PostgreSQL config template
- `backend/.env.example` - PostgreSQL config template

Original SQLite files are preserved:
- `scraper/scraper.py` - Original SQLite scraper
- `backend/main.py` - Original SQLite backend
