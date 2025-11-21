# AAIP Data Tracker - Project Structure

**Last Updated**: 2024-11-21

## Directory Organization

```
aaip-data/
├── backend/                 # FastAPI backend application
│   ├── main_enhanced.py    # Current production backend (v3.0.0)
│   ├── main_draws.py       # Legacy backend with draws support (v2.0.0)
│   ├── main_pg.py          # Basic PostgreSQL backend (v1.0.0)
│   └── requirements.txt
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.js
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── scraper/                # Data collection scripts
│   ├── scraper.py          # Main AAIP scraper
│   ├── import_2024_draws.py # 2024 data import
│   ├── express_entry_collector.py
│   ├── alberta_economy_collector.py
│   └── requirements.txt
├── data/                   # Data files
│   ├── aaip_data.db       # SQLite database (dev)
│   └── aaip_draw_history_2025.csv
├── docs/                   # Active documentation
│   ├── archive/           # Historical/obsolete docs
│   ├── DRAWS_FEATURE_README.md
│   ├── DRAWS_VISUALIZATION.md
│   ├── DEPLOYMENT.md
│   ├── FRONTEND_SETUP.md
│   ├── SCRAPER_SETUP.md
│   └── QUICK_REFERENCE.md
├── scripts/                # Utility scripts
│   ├── database/          # Database scripts
│   └── archive/           # Old/obsolete scripts
├── screenshots/            # UI screenshots and references
├── deployment/             # Deployment configurations
├── .github/workflows/      # CI/CD workflows
├── CLAUDE.md              # AI assistant instructions
├── README.md              # Main project README
└── SEO.md                 # SEO documentation
```

## Active Documentation

### Core Documentation (Root)
- **CLAUDE.md** - Instructions for Claude Code assistant
- **README.md** - Main project overview and quick start
- **SEO.md** - SEO optimization documentation

### Technical Documentation (docs/)
- **DRAWS_FEATURE_README.md** - Draw history feature documentation
- **DRAWS_VISUALIZATION.md** - Visualization components guide
- **DRAWS_QUICKSTART.md** - Quick start guide for draws feature
- **DEPLOYMENT.md** - Deployment procedures and server setup
- **FRONTEND_SETUP.md** - Frontend development setup
- **SCRAPER_SETUP.md** - Scraper configuration and usage
- **QUARTERLY_LABOR_MARKET_GUIDE.md** - Labor market data collection
- **QUICK_REFERENCE.md** - Quick reference for common tasks
- **NGINX_TROUBLESHOOTING.md** - NGINX configuration troubleshooting

## Archived Content

### Archived Documentation (docs/archive/)
Historical implementation reports and phase documentation:
- Phase 1, 2, 3 implementation reports
- Feasibility analysis documents
- Project delivery reports
- Implementation checklists
- Success stories implementation
- Data import summaries

Total: 16 archived documents

### Archived Scripts (scripts/archive/)
Old deployment and testing scripts:
- `test_draws_feature.py`
- `test-phase-1.1.sh`
- `activate_feature.sh`
- `merge-to-test.sh`
- `verify_deployment.sh`

## Key Files by Purpose

### Development
- **Backend**: `backend/main_enhanced.py` (production)
- **Frontend**: `frontend/src/App.jsx` (main entry)
- **API Client**: `frontend/src/api.js`

### Data Collection
- **Main Scraper**: `scraper/scraper.py`
- **2024 Import**: `scraper/import_2024_draws.py`
- **EE Data**: `scraper/express_entry_collector.py`

### Configuration
- **Backend Env**: `backend/.env` (not in repo)
- **Frontend Env**: `frontend/.env` (not in repo)
- **Scraper Env**: `scraper/.env` (not in repo)

### Database
- **Dev SQLite**: `data/aaip_data.db`
- **Production**: PostgreSQL (configured via env vars)
- **Schemas**: `scripts/database/`

### CI/CD
- **Deployment**: `.github/workflows/test-deploy.yml`
- **Test Branch**: Triggers automatic deployment

## Environment Files (Not in Git)

```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@host:port/dbname

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000

# scraper/.env
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## Cleanup History

**2024-11-21**: Major project reorganization
- Removed obsolete phase documentation from root
- Archived 16 implementation/phase documents
- Archived 5 old deployment scripts
- Moved data files to `data/` directory
- Organized all docs into `docs/` and `docs/archive/`
- Cleaned up root directory (kept only essential docs)

## Notes

- Keep root directory clean (only CLAUDE.md, README.md, SEO.md)
- Archive old documentation instead of deleting
- Maintain this document when adding new major features
- See CLAUDE.md for development guidelines
