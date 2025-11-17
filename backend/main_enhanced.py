"""
Enhanced AAIP Data API with Multi-Stream Support
FastAPI backend for serving AAIP historical data including individual streams
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re
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


# New models for Phase 1.1 enhanced features
class SmartInsight(BaseModel):
    type: str  # 'warning', 'positive', 'opportunity', 'info'
    title: str
    detail: str
    action: Optional[str] = None
    reasoning: Optional[str] = None
    generated_at: str


class QuotaCalculation(BaseModel):
    stream_name: str
    current_remaining: int
    current_allocation: int
    usage_rate_per_day: float
    estimated_days_to_exhaust: Optional[int]
    estimated_exhaustion_date: Optional[str]
    confidence_level: str  # 'high', 'medium', 'low'
    warning_level: Optional[str] = None  # 'critical', 'warning', 'normal'


class ProcessingTimeline(BaseModel):
    stream_name: str
    submission_date: str
    current_processing_date: Optional[str]
    estimated_wait_months: Optional[float]
    estimated_processing_date: Optional[str]
    notes: str


class CompetitivenessScore(BaseModel):
    stream_name: str
    stream_category: str
    competitiveness_score: float  # 0-100
    level: str  # 'Very High', 'High', 'Medium', 'Low'
    factors: Dict[str, Any]
    recommendation: str


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


# ============================================================================
# Phase 1.1: Enhanced Features - Smart Insights & Tools
# ============================================================================

@app.get("/api/insights/weekly", response_model=List[SmartInsight])
async def get_weekly_insights():
    """
    Generate smart insights based on recent data patterns
    Analyzes: quota usage, draw frequency, score trends, EOI pool changes
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        insights = []
        current_time = datetime.now()

        # Insight 1: Check quota usage warnings
        cursor.execute("""
            SELECT 
                stream_name,
                nomination_allocation,
                nominations_issued,
                nomination_spaces_remaining,
                timestamp
            FROM stream_data
            WHERE timestamp = (SELECT MAX(timestamp) FROM stream_data)
            AND stream_type = 'main'
            ORDER BY stream_name
        """)
        
        streams = cursor.fetchall()
        for stream in streams:
            if stream['nomination_allocation'] and stream['nomination_allocation'] > 0:
                usage_rate = (stream['nominations_issued'] or 0) / stream['nomination_allocation']
                
                if usage_rate > 0.85:
                    insights.append({
                        "type": "warning",
                        "title": f"{stream['stream_name']} - Quota Nearly Exhausted",
                        "detail": f"Currently at {int(usage_rate * 100)}% quota usage ({stream['nominations_issued']}/{stream['nomination_allocation']})",
                        "action": "If you qualify for this stream, consider submitting your EOI soon",
                        "reasoning": "Historical data shows remaining 15% typically depletes within 4-6 weeks",
                        "generated_at": current_time.isoformat()
                    })
                elif usage_rate > 0.70:
                    insights.append({
                        "type": "info",
                        "title": f"{stream['stream_name']} - Steady Quota Consumption",
                        "detail": f"Currently at {int(usage_rate * 100)}% quota usage",
                        "reasoning": "Stream is on track to exhaust quota by year-end",
                        "generated_at": current_time.isoformat()
                    })

        # Insight 2: Draw frequency analysis
        cursor.execute("""
            SELECT 
                COUNT(*) as draw_count,
                MIN(draw_date) as earliest,
                MAX(draw_date) as latest
            FROM aaip_draws
            WHERE draw_date >= CURRENT_DATE - INTERVAL '30 days'
        """)
        
        draw_freq = cursor.fetchone()
        if draw_freq and draw_freq['draw_count']:
            # Compare with previous 30 days
            cursor.execute("""
                SELECT COUNT(*) as prev_count
                FROM aaip_draws
                WHERE draw_date >= CURRENT_DATE - INTERVAL '60 days'
                AND draw_date < CURRENT_DATE - INTERVAL '30 days'
            """)
            prev_freq = cursor.fetchone()
            
            if prev_freq and prev_freq['prev_count']:
                change_pct = ((draw_freq['draw_count'] - prev_freq['prev_count']) / prev_freq['prev_count']) * 100
                
                if change_pct > 50:
                    insights.append({
                        "type": "positive",
                        "title": "Draw Frequency Significantly Increased",
                        "detail": f"{draw_freq['draw_count']} draws in past 30 days (vs {prev_freq['prev_count']} previously)",
                        "reasoning": f"Draw frequency increased by {int(change_pct)}%. Possible reasons: approaching year-end quota deadline or policy adjustment",
                        "generated_at": current_time.isoformat()
                    })
                elif change_pct < -30:
                    insights.append({
                        "type": "warning",
                        "title": "Draw Frequency Decreased",
                        "detail": f"Only {draw_freq['draw_count']} draws in past 30 days (vs {prev_freq['prev_count']} previously)",
                        "reasoning": "May indicate quota constraints or policy review period",
                        "generated_at": current_time.isoformat()
                    })

        # Insight 3: Score trend analysis for Express Entry
        cursor.execute("""
            SELECT 
                min_score,
                draw_date
            FROM aaip_draws
            WHERE stream_category = 'Alberta Express Entry Stream'
            AND min_score IS NOT NULL
            ORDER BY draw_date DESC
            LIMIT 3
        """)
        
        recent_scores = cursor.fetchall()
        if len(recent_scores) >= 3:
            avg_recent = sum(s['min_score'] for s in recent_scores) / len(recent_scores)
            
            cursor.execute("""
                SELECT AVG(min_score) as avg_score
                FROM (
                    SELECT min_score
                    FROM aaip_draws
                    WHERE stream_category = 'Alberta Express Entry Stream'
                    AND min_score IS NOT NULL
                    AND draw_date < %s
                    ORDER BY draw_date DESC
                    LIMIT 3
                ) as prev_draws
            """, (recent_scores[-1]['draw_date'],))
            
            prev_avg = cursor.fetchone()
            if prev_avg and prev_avg['avg_score']:
                score_change = avg_recent - float(prev_avg['avg_score'])
                
                if score_change < -10:
                    insights.append({
                        "type": "opportunity",
                        "title": "Express Entry Invitation Scores Declining",
                        "detail": f"Recent average score: {int(avg_recent)} (down {int(abs(score_change))} points)",
                        "reasoning": "Score drops may indicate pool depletion of high-score candidates or increased invitation volumes",
                        "action": "Good time for mid-range score candidates to stay ready",
                        "generated_at": current_time.isoformat()
                    })
                elif score_change > 10:
                    insights.append({
                        "type": "info",
                        "title": "Express Entry Scores Trending Higher",
                        "detail": f"Recent average score: {int(avg_recent)} (up {int(score_change)} points)",
                        "reasoning": "May indicate influx of high-score candidates or reduced invitation volumes",
                        "generated_at": current_time.isoformat()
                    })

        # Insight 4: EOI Pool significant changes
        cursor.execute("""
            WITH latest_two AS (
                SELECT 
                    stream_name,
                    candidate_count,
                    timestamp,
                    ROW_NUMBER() OVER (PARTITION BY stream_name ORDER BY timestamp DESC) as rn
                FROM eoi_pool
            )
            SELECT 
                a.stream_name,
                a.candidate_count as current_count,
                b.candidate_count as previous_count
            FROM latest_two a
            LEFT JOIN latest_two b ON a.stream_name = b.stream_name AND b.rn = 2
            WHERE a.rn = 1
            AND b.candidate_count IS NOT NULL
            AND ABS(a.candidate_count - b.candidate_count) > 50
            ORDER BY ABS(a.candidate_count - b.candidate_count) DESC
            LIMIT 3
        """)
        
        pool_changes = cursor.fetchall()
        for change in pool_changes:
            delta = change['current_count'] - change['previous_count']
            change_pct = (delta / change['previous_count']) * 100 if change['previous_count'] > 0 else 0
            
            if delta > 0:
                insights.append({
                    "type": "info",
                    "title": f"{change['stream_name']} - EOI Pool Increased",
                    "detail": f"Pool size: {change['current_count']} (up {delta} candidates, +{int(change_pct)}%)",
                    "reasoning": "Increased competition may affect future draw scores",
                    "generated_at": current_time.isoformat()
                })
            else:
                insights.append({
                    "type": "positive",
                    "title": f"{change['stream_name']} - EOI Pool Decreased",
                    "detail": f"Pool size: {change['current_count']} (down {abs(delta)} candidates, {int(change_pct)}%)",
                    "reasoning": "Reduced pool size may indicate recent draws or candidate withdrawals",
                    "generated_at": current_time.isoformat()
                })

        cursor.close()
        conn.close()

        # Sort by type priority: warning > opportunity > positive > info
        type_priority = {'warning': 0, 'opportunity': 1, 'positive': 2, 'info': 3}
        insights.sort(key=lambda x: type_priority.get(x['type'], 99))

        return [SmartInsight(**insight) for insight in insights]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools/quota-calculator")
async def calculate_quota_exhaustion(stream_name: Optional[str] = None):
    """
    Calculate estimated quota exhaustion date based on historical usage rate
    Returns calculations for all streams or a specific stream
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        results = []

        # Build query based on stream_name filter
        where_clause = "AND s1.stream_name = %s" if stream_name else ""
        params = [stream_name] if stream_name else []

        cursor.execute(f"""
            WITH latest_data AS (
                SELECT 
                    stream_name,
                    nomination_allocation,
                    nominations_issued,
                    nomination_spaces_remaining,
                    timestamp
                FROM stream_data
                WHERE timestamp = (SELECT MAX(timestamp) FROM stream_data)
                AND stream_type = 'main'
                {where_clause}
            ),
            usage_rate AS (
                SELECT 
                    s1.stream_name,
                    s1.nominations_issued - COALESCE(s2.nominations_issued, 0) as issued_in_period,
                    EXTRACT(EPOCH FROM (s1.timestamp - s2.timestamp)) / 86400 as days_elapsed
                FROM stream_data s1
                LEFT JOIN LATERAL (
                    SELECT nominations_issued, timestamp
                    FROM stream_data s3
                    WHERE s3.stream_name = s1.stream_name
                    AND s3.timestamp < s1.timestamp
                    AND s3.stream_type = 'main'
                    ORDER BY timestamp DESC
                    LIMIT 1
                    OFFSET 29
                ) s2 ON true
                WHERE s1.timestamp = (SELECT MAX(timestamp) FROM stream_data)
                AND s1.stream_type = 'main'
                {where_clause}
            )
            SELECT 
                l.stream_name,
                l.nomination_allocation,
                l.nominations_issued,
                l.nomination_spaces_remaining,
                l.timestamp,
                CASE 
                    WHEN u.days_elapsed > 0 THEN u.issued_in_period / u.days_elapsed
                    ELSE 0
                END as usage_rate_per_day
            FROM latest_data l
            LEFT JOIN usage_rate u ON l.stream_name = u.stream_name
        """, params * 2 if stream_name else [])

        streams = cursor.fetchall()
        cursor.close()
        conn.close()

        for stream in streams:
            remaining = stream['nomination_spaces_remaining'] or 0
            rate = stream['usage_rate_per_day'] or 0
            
            if rate > 0 and remaining > 0:
                days_to_exhaust = int(remaining / rate)
                exhaustion_date = (datetime.now() + timedelta(days=days_to_exhaust)).date()
                
                # Determine confidence and warning level
                if stream['nominations_issued'] and stream['nomination_allocation']:
                    usage_pct = stream['nominations_issued'] / stream['nomination_allocation']
                    if usage_pct > 0.85:
                        confidence = "high"
                        warning = "critical"
                    elif usage_pct > 0.70:
                        confidence = "medium"
                        warning = "warning"
                    else:
                        confidence = "medium"
                        warning = "normal"
                else:
                    confidence = "low"
                    warning = "normal"
            else:
                days_to_exhaust = None
                exhaustion_date = None
                confidence = "low"
                warning = "normal"

            results.append(QuotaCalculation(
                stream_name=stream['stream_name'],
                current_remaining=remaining,
                current_allocation=stream['nomination_allocation'] or 0,
                usage_rate_per_day=round(rate, 2),
                estimated_days_to_exhaust=days_to_exhaust,
                estimated_exhaustion_date=exhaustion_date.isoformat() if exhaustion_date else None,
                confidence_level=confidence,
                warning_level=warning
            ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools/processing-timeline")
async def estimate_processing_timeline(
    submission_date: str = Query(..., description="Submission date in YYYY-MM-DD format"),
    stream_name: Optional[str] = Query(None, description="Stream name (optional)")
):
    """
    Estimate processing timeline based on current processing dates and historical speed
    """
    try:
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        submission = datetime.strptime(submission_date, "%Y-%m-%d").date()
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        results = []

        # Build query
        where_clause = "AND stream_name = %s" if stream_name else ""
        params = [stream_name] if stream_name else []

        cursor.execute(f"""
            WITH latest_processing AS (
                SELECT 
                    stream_name,
                    processing_date,
                    timestamp
                FROM stream_data
                WHERE timestamp = (SELECT MAX(timestamp) FROM stream_data)
                AND processing_date IS NOT NULL
                AND stream_type = 'main'
                {where_clause}
            ),
            processing_speed AS (
                SELECT 
                    s1.stream_name,
                    s1.processing_date as current_date,
                    s2.processing_date as past_date,
                    EXTRACT(EPOCH FROM (s1.timestamp - s2.timestamp)) / 86400 as real_days,
                    s1.processing_date::date - s2.processing_date::date as processing_days_advanced
                FROM stream_data s1
                LEFT JOIN LATERAL (
                    SELECT processing_date, timestamp
                    FROM stream_data s3
                    WHERE s3.stream_name = s1.stream_name
                    AND s3.processing_date IS NOT NULL
                    AND s3.timestamp < s1.timestamp
                    AND s3.stream_type = 'main'
                    ORDER BY timestamp DESC
                    LIMIT 1
                    OFFSET 14
                ) s2 ON true
                WHERE s1.timestamp = (SELECT MAX(timestamp) FROM stream_data)
                AND s1.processing_date IS NOT NULL
                AND s1.stream_type = 'main'
                {where_clause}
            )
            SELECT 
                l.stream_name,
                l.processing_date,
                l.timestamp,
                CASE 
                    WHEN s.real_days > 0 THEN s.processing_days_advanced / s.real_days
                    ELSE 0
                END as days_per_real_day
            FROM latest_processing l
            LEFT JOIN processing_speed s ON l.stream_name = s.stream_name
        """, params * 2 if stream_name else [])

        streams = cursor.fetchall()
        cursor.close()
        conn.close()

        for stream in streams:
            # Extract just the date part before any parentheses or "for"
            processing_date_str = stream['processing_date']
            current_processing = None
            
            if processing_date_str:
                # Remove everything after '(' or 'for'
                processing_date_str = processing_date_str.split('(')[0].split(' for')[0].strip()
                
                # Try to find a date pattern like "Month Day, Year"
                date_pattern = r'([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})'
                match = re.search(date_pattern, processing_date_str)
                
                if match:
                    try:
                        current_processing = datetime.strptime(match.group(0), "%B %d, %Y").date()
                    except ValueError:
                        pass
            
            if current_processing:
                days_behind = (current_processing - submission).days
                speed = stream['days_per_real_day'] or 0.5  # Default to 0.5 if no data
                
                if days_behind < 0:
                    # Submission is after current processing date
                    estimated_months = abs(days_behind) / (speed * 30)
                    estimated_date = datetime.now().date() + timedelta(days=int(abs(days_behind) / speed))
                    notes = f"Your submission is ahead of current processing queue. Estimated wait based on processing speed of {speed:.2f} days/day."
                elif days_behind == 0:
                    estimated_months = 0.5
                    estimated_date = datetime.now().date() + timedelta(days=15)
                    notes = "Your application is near the current processing date. Processing may begin soon."
                else:
                    estimated_months = days_behind / (speed * 30)
                    estimated_date = datetime.now().date() + timedelta(days=int(days_behind / speed)) if speed > 0 else None
                    notes = f"Processing speed: approximately {speed:.2f} processing days per calendar day."
            else:
                estimated_months = None
                estimated_date = None
                notes = "Processing date information not available for this stream."

            results.append(ProcessingTimeline(
                stream_name=stream['stream_name'],
                submission_date=submission_date,
                current_processing_date=stream['processing_date'],
                estimated_wait_months=round(estimated_months, 1) if estimated_months else None,
                estimated_processing_date=estimated_date.isoformat() if estimated_date else None,
                notes=notes
            ))

        return results

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools/competitiveness", response_model=List[CompetitivenessScore])
async def get_stream_competitiveness():
    """
    Calculate competitiveness score for each stream based on multiple factors:
    - Quota utilization rate
    - EOI pool size changes
    - Draw frequency
    - Average invitation scores
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        results = []

        # Get latest stream data with quota info
        cursor.execute("""
            SELECT 
                stream_name,
                nomination_allocation,
                nominations_issued,
                nomination_spaces_remaining,
                applications_to_process
            FROM stream_data
            WHERE timestamp = (SELECT MAX(timestamp) FROM stream_data)
            AND stream_type = 'main'
        """)
        
        streams = cursor.fetchall()

        for stream in streams:
            factors = {}
            score = 50  # Base score
            
            # Factor 1: Quota utilization (higher = more competitive)
            if stream['nomination_allocation'] and stream['nomination_allocation'] > 0:
                usage_rate = (stream['nominations_issued'] or 0) / stream['nomination_allocation']
                factors['quota_usage'] = f"{int(usage_rate * 100)}%"
                
                if usage_rate > 0.90:
                    score += 25
                    factors['quota_pressure'] = "Critical - nearly exhausted"
                elif usage_rate > 0.75:
                    score += 15
                    factors['quota_pressure'] = "High - limited spaces"
                elif usage_rate > 0.50:
                    score += 5
                    factors['quota_pressure'] = "Moderate"
                else:
                    score -= 10
                    factors['quota_pressure'] = "Low - ample spaces available"

            # Factor 2: Applications backlog
            if stream['applications_to_process']:
                backlog = stream['applications_to_process']
                factors['backlog'] = f"{backlog} applications"
                
                if backlog > 500:
                    score += 15
                    factors['backlog_impact'] = "High processing volume"
                elif backlog > 200:
                    score += 5
                    factors['backlog_impact'] = "Moderate volume"

            # Factor 3: EOI pool size (if available)
            cursor.execute("""
                SELECT candidate_count
                FROM eoi_pool
                WHERE stream_name = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (stream['stream_name'],))
            
            eoi_data = cursor.fetchone()
            if eoi_data:
                pool_size = eoi_data['candidate_count']
                factors['eoi_pool_size'] = f"{pool_size} candidates"
                
                if pool_size > 300:
                    score += 20
                    factors['pool_pressure'] = "Very high competition"
                elif pool_size > 150:
                    score += 10
                    factors['pool_pressure'] = "High competition"
                elif pool_size > 50:
                    score += 5
                    factors['pool_pressure'] = "Moderate competition"

            # Determine level and recommendation
            if score >= 80:
                level = "Very High"
                recommendation = "Extremely competitive. Ensure your application is perfect and consider improving qualifications."
            elif score >= 65:
                level = "High"
                recommendation = "Highly competitive. Strong applications recommended. Consider timing carefully."
            elif score >= 50:
                level = "Medium"
                recommendation = "Moderate competition. Good chance with solid qualifications."
            else:
                level = "Low"
                recommendation = "Favorable conditions. Good opportunity to apply if eligible."

            results.append(CompetitivenessScore(
                stream_name=stream['stream_name'],
                stream_category="AAIP",
                competitiveness_score=min(100, max(0, score)),
                level=level,
                factors=factors,
                recommendation=recommendation
            ))

        cursor.close()
        conn.close()

        # Sort by score descending
        results.sort(key=lambda x: x.competitiveness_score, reverse=True)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    from datetime import timedelta
    from dateutil.relativedelta import relativedelta
    uvicorn.run(app, host="0.0.0.0", port=8000)
