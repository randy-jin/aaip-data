"""
Enhanced AAIP Data API with Multi-Stream Support
FastAPI backend for serving AAIP historical data including individual streams
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date
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
    total_draws: int = 0
    latest_draw_date: Optional[str] = None


class DrawRecord(BaseModel):
    id: int
    draw_date: str
    draw_number: Optional[str]
    stream_category: str
    stream_detail: Optional[str]
    min_score: Optional[int]
    invitations_issued: Optional[int]
    created_at: str
    updated_at: str


class DrawStats(BaseModel):
    stream_category: str
    stream_detail: Optional[str]
    total_draws: int
    total_invitations: int
    avg_score: Optional[float]
    min_score: Optional[int]
    max_score: Optional[int]
    latest_draw_date: Optional[str]
    earliest_draw_date: Optional[str]


class StreamList(BaseModel):
    categories: List[str]
    streams: List[Dict[str, str]]


class DrawTrendData(BaseModel):
    date: str
    min_score: Optional[int]
    invitations: Optional[int]
    stream_category: str
    stream_detail: Optional[str]


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
        "message": "AAIP Data API (Enhanced with Multi-Stream and Draws Support)",
        "version": "2.1.0",
        "endpoints": {
            "stats": "/api/stats",
            "summary": "/api/summary",
            "latest": "/api/summary/latest",
            "streams": "/api/streams",
            "stream_by_name": "/api/streams/{stream_name}",
            "stream_list": "/api/streams/list",
            "draws": "/api/draws",
            "draw_streams": "/api/draws/streams",
            "draw_trends": "/api/draws/trends",
            "draw_stats": "/api/draws/stats",
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

        # Get draws stats
        try:
            cursor.execute("SELECT COUNT(*) as count FROM aaip_draws")
            total_draws = cursor.fetchone()['count']

            cursor.execute("SELECT draw_date FROM aaip_draws ORDER BY draw_date DESC LIMIT 1")
            latest_draw = cursor.fetchone()
            latest_draw_date = latest_draw['draw_date'].isoformat() if latest_draw else None
        except:
            total_draws = 0
            latest_draw_date = None

        cursor.close()
        conn.close()

        return Stats(
            total_records=total,
            first_record=first_timestamp,
            last_record=last_timestamp,
            latest_data=latest_data,
            total_streams=total_streams,
            available_streams=available_streams,
            total_draws=total_draws,
            latest_draw_date=latest_draw_date
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


@app.get("/api/draws", response_model=List[DrawRecord])
def get_draws(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    stream_category: Optional[str] = None,
    stream_detail: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get draw records with optional filtering

    - **limit**: Maximum number of records to return
    - **offset**: Number of records to skip
    - **stream_category**: Filter by stream category
    - **stream_detail**: Filter by stream detail/pathway
    - **start_date**: Filter draws on or after this date (YYYY-MM-DD)
    - **end_date**: Filter draws on or before this date (YYYY-MM-DD)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, draw_date, draw_number, stream_category, stream_detail,
                   min_score, invitations_issued, created_at, updated_at
            FROM aaip_draws
            WHERE 1=1
        """
        params = []

        if stream_category:
            query += " AND stream_category = %s"
            params.append(stream_category)

        if stream_detail:
            # Handle "General" as NULL stream_detail
            if stream_detail == "General":
                query += " AND stream_detail IS NULL"
            else:
                query += " AND stream_detail = %s"
                params.append(stream_detail)

        if start_date:
            query += " AND draw_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND draw_date <= %s"
            params.append(end_date)

        query += " ORDER BY draw_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            DrawRecord(
                id=row['id'],
                draw_date=row['draw_date'].isoformat(),
                draw_number=row['draw_number'],
                stream_category=row['stream_category'],
                stream_detail=row['stream_detail'],
                min_score=row['min_score'],
                invitations_issued=row['invitations_issued'],
                created_at=row['created_at'].isoformat(),
                updated_at=row['updated_at'].isoformat()
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/draws/streams", response_model=StreamList)
def get_draw_streams():
    """Get list of all stream categories and their details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get unique categories
        cursor.execute("""
            SELECT DISTINCT stream_category
            FROM aaip_draws
            ORDER BY stream_category
        """)
        categories = [row['stream_category'] for row in cursor.fetchall()]

        # Get category-detail combinations
        cursor.execute("""
            SELECT DISTINCT stream_category, stream_detail
            FROM aaip_draws
            ORDER BY stream_category, stream_detail
        """)
        streams = [
            {
                'category': row['stream_category'],
                'detail': row['stream_detail'] or 'General'
            }
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        return StreamList(categories=categories, streams=streams)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/draws/trends", response_model=List[DrawTrendData])
def get_draw_trends(
    stream_category: Optional[str] = None,
    stream_detail: Optional[str] = None,
    year: Optional[int] = None,
    limit: Optional[int] = 365
):
    """
    Get draw trend data for visualization

    - **stream_category**: Filter by stream category
    - **stream_detail**: Filter by stream detail
    - **year**: Filter by year (e.g., 2025)
    - **limit**: Maximum number of records
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT draw_date, stream_category, stream_detail,
                   min_score, invitations_issued
            FROM aaip_draws
            WHERE 1=1
        """
        params = []

        if stream_category:
            query += " AND stream_category = %s"
            params.append(stream_category)

        if stream_detail:
            # Handle "General" as NULL stream_detail
            if stream_detail == "General":
                query += " AND stream_detail IS NULL"
            else:
                query += " AND stream_detail = %s"
                params.append(stream_detail)

        if year:
            query += " AND EXTRACT(YEAR FROM draw_date) = %s"
            params.append(year)

        query += " ORDER BY draw_date ASC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            DrawTrendData(
                date=row['draw_date'].isoformat(),
                min_score=row['min_score'],
                invitations=row['invitations_issued'],
                stream_category=row['stream_category'],
                stream_detail=row['stream_detail'] or 'General'
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/draws/stats", response_model=List[DrawStats])
def get_draw_stats(stream_category: Optional[str] = None):
    """Get aggregated statistics for each stream"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                stream_category,
                stream_detail,
                COUNT(*) as total_draws,
                SUM(invitations_issued) as total_invitations,
                AVG(min_score) as avg_score,
                MIN(min_score) as min_score,
                MAX(min_score) as max_score,
                MAX(draw_date) as latest_draw_date,
                MIN(draw_date) as earliest_draw_date
            FROM aaip_draws
        """
        params = []

        if stream_category:
            query += " WHERE stream_category = %s"
            params.append(stream_category)

        query += """
            GROUP BY stream_category, stream_detail
            ORDER BY stream_category, stream_detail
        """

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            DrawStats(
                stream_category=row['stream_category'],
                stream_detail=row['stream_detail'],
                total_draws=row['total_draws'],
                total_invitations=row['total_invitations'],
                avg_score=round(row['avg_score'], 1) if row['avg_score'] else None,
                min_score=row['min_score'],
                max_score=row['max_score'],
                latest_draw_date=row['latest_draw_date'].isoformat() if row['latest_draw_date'] else None,
                earliest_draw_date=row['earliest_draw_date'].isoformat() if row['earliest_draw_date'] else None
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# EOI Pool Endpoints
# ============================================

class EOIPool(BaseModel):
    stream_name: str
    candidate_count: int
    timestamp: str
    last_updated: Optional[str] = None


class EOITrend(BaseModel):
    stream_name: str
    timestamp: str
    candidate_count: int
    change_from_previous: Optional[int] = None
    change_percentage: Optional[float] = None


class EOIAlert(BaseModel):
    stream_name: str
    current_count: int
    previous_count: int
    change: int
    change_percentage: float
    timestamp: str
    alert_type: str  # 'significant_increase', 'significant_decrease', 'stable'


@app.get("/api/eoi/latest", response_model=List[EOIPool])
async def get_latest_eoi_pool():
    """Get the most recent EOI pool data for all streams"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get the most recent timestamp
        cursor.execute("SELECT MAX(timestamp) as latest FROM eoi_pool")
        latest = cursor.fetchone()

        if not latest or not latest['latest']:
            cursor.close()
            conn.close()
            return []

        # Get all streams for the latest timestamp
        cursor.execute("""
            SELECT stream_name, candidate_count, timestamp, last_updated
            FROM eoi_pool
            WHERE timestamp = %s
            ORDER BY candidate_count DESC
        """, (latest['latest'],))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            EOIPool(
                stream_name=row['stream_name'],
                candidate_count=row['candidate_count'],
                timestamp=row['timestamp'].isoformat(),
                last_updated=row['last_updated']
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/eoi/trends", response_model=List[EOITrend])
async def get_eoi_trends(
    stream_name: Optional[str] = None,
    days: int = 7
):
    """Get EOI pool trends over time for a specific stream or all streams"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Build query
        query = """
            WITH ordered_data AS (
                SELECT
                    stream_name,
                    timestamp,
                    candidate_count,
                    LAG(candidate_count) OVER (PARTITION BY stream_name ORDER BY timestamp) as prev_count
                FROM eoi_pool
                WHERE timestamp >= NOW() - INTERVAL '%s days'
        """

        params = [days]

        if stream_name:
            query += " AND stream_name = %s"
            params.append(stream_name)

        query += """
            )
            SELECT
                stream_name,
                timestamp,
                candidate_count,
                candidate_count - prev_count as change_from_previous,
                CASE
                    WHEN prev_count > 0
                    THEN ROUND(((candidate_count - prev_count)::numeric / prev_count * 100), 2)
                    ELSE NULL
                END as change_percentage
            FROM ordered_data
            ORDER BY stream_name, timestamp DESC
        """

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            EOITrend(
                stream_name=row['stream_name'],
                timestamp=row['timestamp'].isoformat(),
                candidate_count=row['candidate_count'],
                change_from_previous=row['change_from_previous'],
                change_percentage=float(row['change_percentage']) if row['change_percentage'] else None
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/eoi/alerts", response_model=List[EOIAlert])
async def get_eoi_alerts(threshold_percentage: float = 5.0):
    """
    Get EOI pool alerts for significant changes
    threshold_percentage: Minimum percentage change to trigger alert (default 5%)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get latest two data points for each stream
        cursor.execute("""
            WITH ranked_data AS (
                SELECT
                    stream_name,
                    candidate_count,
                    timestamp,
                    ROW_NUMBER() OVER (PARTITION BY stream_name ORDER BY timestamp DESC) as rn
                FROM eoi_pool
            ),
            latest_data AS (
                SELECT
                    a.stream_name,
                    a.candidate_count as current_count,
                    a.timestamp as current_timestamp,
                    b.candidate_count as previous_count
                FROM ranked_data a
                LEFT JOIN ranked_data b
                    ON a.stream_name = b.stream_name AND b.rn = 2
                WHERE a.rn = 1
            )
            SELECT
                stream_name,
                current_count,
                previous_count,
                current_count - COALESCE(previous_count, current_count) as change,
                CASE
                    WHEN previous_count > 0
                    THEN ROUND(((current_count - previous_count)::numeric / previous_count * 100), 2)
                    ELSE 0
                END as change_percentage,
                current_timestamp
            FROM latest_data
            WHERE previous_count IS NOT NULL
            ORDER BY ABS(current_count - previous_count) DESC
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        alerts = []
        for row in rows:
            change_pct = float(row['change_percentage']) if row['change_percentage'] else 0

            # Determine alert type
            if abs(change_pct) < threshold_percentage:
                alert_type = 'stable'
            elif change_pct > 0:
                alert_type = 'significant_increase'
            else:
                alert_type = 'significant_decrease'

            # Only include significant changes
            if abs(change_pct) >= threshold_percentage:
                alerts.append(
                    EOIAlert(
                        stream_name=row['stream_name'],
                        current_count=row['current_count'],
                        previous_count=row['previous_count'],
                        change=row['change'],
                        change_percentage=change_pct,
                        timestamp=row['current_timestamp'].isoformat(),
                        alert_type=alert_type
                    )
                )

        return alerts

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
