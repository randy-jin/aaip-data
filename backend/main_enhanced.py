"""
Enhanced AAIP Data API with Multi-Stream Support
FastAPI backend for serving AAIP historical data including individual streams
"""

from fastapi import FastAPI, HTTPException, Query
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
    title="AAIP Data API (Enhanced)",
    description="API for Alberta Advantage Immigration Program processing data with multi-stream support",
    version="2.0.0"
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


class StreamData(BaseModel):
    id: int
    timestamp: str
    stream_name: str
    stream_type: str
    parent_stream: Optional[str]
    nomination_allocation: Optional[int]
    nominations_issued: Optional[int]
    nomination_spaces_remaining: Optional[int]
    applications_to_process: Optional[int]
    processing_date: Optional[str]
    last_updated: Optional[str]


class ScrapeLog(BaseModel):
    id: int
    timestamp: str
    status: str
    message: Optional[str]
    streams_collected: Optional[int] = 0


class Stats(BaseModel):
    total_records: int
    first_record: Optional[str]
    last_record: Optional[str]
    latest_data: Optional[AAIPSummary]
    total_streams: int
    available_streams: List[str]


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
        "message": "AAIP Data API (Enhanced with Multi-Stream Support)",
        "version": "2.0.0",
        "endpoints": {
            "stats": "/api/stats",
            "summary": "/api/summary",
            "latest": "/api/summary/latest",
            "streams": "/api/streams (NEW)",
            "stream_by_name": "/api/streams/{stream_name} (NEW)",
            "stream_list": "/api/streams/list (NEW)",
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
        
        # Get stream statistics
        try:
            cursor.execute("SELECT COUNT(DISTINCT stream_name) as count FROM stream_data")
            total_streams = cursor.fetchone()['count']
            
            cursor.execute("SELECT DISTINCT stream_name FROM stream_data ORDER BY stream_name")
            available_streams = [row['stream_name'] for row in cursor.fetchall()]
        except:
            total_streams = 0
            available_streams = []
        
        cursor.close()
        conn.close()
        
        return Stats(
            total_records=total,
            first_record=first_timestamp,
            last_record=last_timestamp,
            latest_data=latest_data,
            total_streams=total_streams,
            available_streams=available_streams
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


@app.get("/api/streams/list")
def get_stream_list():
    """Get list of available streams"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT DISTINCT stream_name, stream_type, parent_stream
            FROM stream_data
            ORDER BY stream_type, stream_name
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "streams": [
                {
                    "stream_name": row['stream_name'],
                    "stream_type": row['stream_type'],
                    "parent_stream": row['parent_stream']
                }
                for row in rows
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/streams", response_model=List[StreamData])
def get_all_streams(
    limit: Optional[int] = Query(100, ge=1, le=1000),
    offset: Optional[int] = Query(0, ge=0),
    stream_type: Optional[str] = Query(None, description="Filter by stream type: 'main' or 'sub-pathway'")
):
    """Get all stream data with optional filtering"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if stream_type:
            cursor.execute("""
                SELECT id, timestamp, stream_name, stream_type, parent_stream,
                       nomination_allocation, nominations_issued, 
                       nomination_spaces_remaining, applications_to_process,
                       processing_date, last_updated
                FROM stream_data
                WHERE stream_type = %s
                ORDER BY timestamp DESC, stream_name
                LIMIT %s OFFSET %s
            """, (stream_type, limit, offset))
        else:
            cursor.execute("""
                SELECT id, timestamp, stream_name, stream_type, parent_stream,
                       nomination_allocation, nominations_issued, 
                       nomination_spaces_remaining, applications_to_process,
                       processing_date, last_updated
                FROM stream_data
                ORDER BY timestamp DESC, stream_name
                LIMIT %s OFFSET %s
            """, (limit, offset))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            StreamData(
                id=row['id'],
                timestamp=row['timestamp'].isoformat(),
                stream_name=row['stream_name'],
                stream_type=row['stream_type'],
                parent_stream=row['parent_stream'],
                nomination_allocation=row['nomination_allocation'],
                nominations_issued=row['nominations_issued'],
                nomination_spaces_remaining=row['nomination_spaces_remaining'],
                applications_to_process=row['applications_to_process'],
                processing_date=row['processing_date'],
                last_updated=row['last_updated']
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/streams/{stream_name}", response_model=List[StreamData])
def get_stream_by_name(
    stream_name: str,
    limit: Optional[int] = Query(100, ge=1, le=1000)
):
    """Get historical data for a specific stream"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, timestamp, stream_name, stream_type, parent_stream,
                   nomination_allocation, nominations_issued, 
                   nomination_spaces_remaining, applications_to_process,
                   processing_date, last_updated
            FROM stream_data
            WHERE stream_name = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (stream_name, limit))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"Stream '{stream_name}' not found")
        
        return [
            StreamData(
                id=row['id'],
                timestamp=row['timestamp'].isoformat(),
                stream_name=row['stream_name'],
                stream_type=row['stream_type'],
                parent_stream=row['parent_stream'],
                nomination_allocation=row['nomination_allocation'],
                nominations_issued=row['nominations_issued'],
                nomination_spaces_remaining=row['nomination_spaces_remaining'],
                applications_to_process=row['applications_to_process'],
                processing_date=row['processing_date'],
                last_updated=row['last_updated']
            )
            for row in rows
        ]
        
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs", response_model=List[ScrapeLog])
def get_scrape_logs(limit: Optional[int] = 50):
    """Get scrape logs"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, timestamp, status, message, 
                   COALESCE(streams_collected, 0) as streams_collected
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
                message=row['message'],
                streams_collected=row['streams_collected']
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
