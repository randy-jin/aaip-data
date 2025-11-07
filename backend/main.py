"""
AAIP Data API
FastAPI backend for serving AAIP historical data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

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

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/aaip_data.db')


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
    """Get database connection"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not found")
    return sqlite3.connect(DB_PATH)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AAIP Data API",
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
        cursor = conn.cursor()
        
        # Get total records
        cursor.execute("SELECT COUNT(*) FROM aaip_summary")
        total = cursor.fetchone()[0]
        
        # Get first and last record timestamps
        cursor.execute("SELECT timestamp FROM aaip_summary ORDER BY timestamp ASC LIMIT 1")
        first = cursor.fetchone()
        first_timestamp = first[0] if first else None
        
        cursor.execute("SELECT timestamp FROM aaip_summary ORDER BY timestamp DESC LIMIT 1")
        last = cursor.fetchone()
        last_timestamp = last[0] if last else None
        
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
                id=latest_row[0],
                timestamp=latest_row[1],
                nomination_allocation=latest_row[2],
                nominations_issued=latest_row[3],
                nomination_spaces_remaining=latest_row[4],
                applications_to_process=latest_row[5],
                last_updated=latest_row[6]
            )
        
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
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, nomination_allocation, nominations_issued,
                   nomination_spaces_remaining, applications_to_process, last_updated
            FROM aaip_summary
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            AAIPSummary(
                id=row[0],
                timestamp=row[1],
                nomination_allocation=row[2],
                nominations_issued=row[3],
                nomination_spaces_remaining=row[4],
                applications_to_process=row[5],
                last_updated=row[6]
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
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, nomination_allocation, nominations_issued,
                   nomination_spaces_remaining, applications_to_process, last_updated
            FROM aaip_summary
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="No data found")
        
        return AAIPSummary(
            id=row[0],
            timestamp=row[1],
            nomination_allocation=row[2],
            nominations_issued=row[3],
            nomination_spaces_remaining=row[4],
            applications_to_process=row[5],
            last_updated=row[6]
        )
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs", response_model=List[ScrapeLog])
def get_scrape_logs(limit: Optional[int] = 50):
    """Get scrape logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, status, message
            FROM scrape_log
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            ScrapeLog(
                id=row[0],
                timestamp=row[1],
                status=row[2],
                message=row[3]
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
