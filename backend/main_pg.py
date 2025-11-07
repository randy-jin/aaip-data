"""
AAIP Data API with PostgreSQL
FastAPI backend for serving AAIP historical data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AAIP Data API",
    description="API for Alberta Advantage Immigration Program processing data",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'aaip_data')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


# Pydantic models
class AAIPSummary(BaseModel):
    id: int
    timestamp: str
    nomination_allocation: Optional[int]
    nominations_issued: Optional[int]
    nomination_spaces_remaining: Optional[int]
    applications_to_process: Optional[int]
    last_updated: Optional[str]


class ScrapeLog(BaseModel):
    id: int
    timestamp: str
    status: str
    message: Optional[str]


class Stats(BaseModel):
    total_records: int
    first_record: Optional[str]
    last_record: Optional[str]
    latest_data: Optional[AAIPSummary]


def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        else:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AAIP Data API (PostgreSQL)",
        "version": "1.0.0",
        "endpoints": {
            "stats": "/api/stats",
            "summary": "/api/summary",
            "latest": "/api/summary/latest",
            "logs": "/api/logs"
        }
    }


@app.get("/api/stats", response_model=Stats)
def get_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total records
        cursor.execute("SELECT COUNT(*) as count FROM aaip_summary")
        total = cursor.fetchone()['count']
        
        # Get first and last record timestamps
        cursor.execute("SELECT timestamp FROM aaip_summary ORDER BY timestamp ASC LIMIT 1")
        first = cursor.fetchone()
        first_timestamp = first['timestamp'].isoformat() if first else None
        
        cursor.execute("SELECT timestamp FROM aaip_summary ORDER BY timestamp DESC LIMIT 1")
        last = cursor.fetchone()
        last_timestamp = last['timestamp'].isoformat() if last else None
        
        # Get latest data
        cursor.execute("""
            SELECT id, timestamp, nomination_allocation, nominations_issued,
                   nomination_spaces_remaining, applications_to_process, last_updated
            FROM aaip_summary
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        latest_row = cursor.fetchone()
        
        latest_data = None
        if latest_row:
            latest_data = AAIPSummary(
                id=latest_row['id'],
                timestamp=latest_row['timestamp'].isoformat(),
                nomination_allocation=latest_row['nomination_allocation'],
                nominations_issued=latest_row['nominations_issued'],
                nomination_spaces_remaining=latest_row['nomination_spaces_remaining'],
                applications_to_process=latest_row['applications_to_process'],
                last_updated=latest_row['last_updated']
            )
        
        cursor.close()
        conn.close()
        
        return Stats(
            total_records=total,
            first_record=first_timestamp,
            last_record=last_timestamp,
            latest_data=latest_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary", response_model=List[AAIPSummary])
def get_summary(limit: Optional[int] = 100, offset: Optional[int] = 0):
    """Get all summary data with pagination"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, timestamp, nomination_allocation, nominations_issued,
                   nomination_spaces_remaining, applications_to_process, last_updated
            FROM aaip_summary
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            AAIPSummary(
                id=row['id'],
                timestamp=row['timestamp'].isoformat(),
                nomination_allocation=row['nomination_allocation'],
                nominations_issued=row['nominations_issued'],
                nomination_spaces_remaining=row['nomination_spaces_remaining'],
                applications_to_process=row['applications_to_process'],
                last_updated=row['last_updated']
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary/latest", response_model=AAIPSummary)
def get_latest_summary():
    """Get the most recent summary data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, timestamp, nomination_allocation, nominations_issued,
                   nomination_spaces_remaining, applications_to_process, last_updated
            FROM aaip_summary
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="No data found")
        
        return AAIPSummary(
            id=row['id'],
            timestamp=row['timestamp'].isoformat(),
            nomination_allocation=row['nomination_allocation'],
            nominations_issued=row['nominations_issued'],
            nomination_spaces_remaining=row['nomination_spaces_remaining'],
            applications_to_process=row['applications_to_process'],
            last_updated=row['last_updated']
        )
        
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs", response_model=List[ScrapeLog])
def get_scrape_logs(limit: Optional[int] = 50):
    """Get scrape logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, timestamp, status, message
            FROM scrape_log
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            ScrapeLog(
                id=row['id'],
                timestamp=row['timestamp'].isoformat(),
                status=row['status'],
                message=row['message']
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
