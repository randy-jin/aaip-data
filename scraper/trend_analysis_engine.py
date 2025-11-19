#!/usr/bin/env python3
"""
Historical Trend Analysis Engine for AAIP Data

Analyzes historical draw patterns to identify:
- Draw frequency patterns
- CRS score trends
- Seasonal variations
- Invitation volume trends

Purpose: Power predictive insights and help users understand patterns
"""

import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'aaip_data')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


def get_db_connection():
    """Get PostgreSQL database connection"""
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


def get_historical_draws():
    """Fetch all historical draws from database"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            draw_date,
            stream_category,
            min_score,
            invitations_issued
        FROM aaip_draws
        WHERE draw_date IS NOT NULL
        ORDER BY draw_date ASC
    """)
    
    draws = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return draws


def analyze_draw_frequency(draws):
    """
    Analyze how frequently draws occur
    Returns: avg days between draws, by stream
    """
    print("\n📅 Analyzing Draw Frequency Patterns...")
    
    # Group by stream
    by_stream = defaultdict(list)
    for draw in draws:
        by_stream[draw['stream_category']].append(draw['draw_date'])
    
    frequency_analysis = {}
    
    for stream, dates in by_stream.items():
        if len(dates) < 2:
            continue
            
        # Calculate days between consecutive draws
        intervals = []
        sorted_dates = sorted(dates)
        
        for i in range(1, len(sorted_dates)):
            delta = (sorted_dates[i] - sorted_dates[i-1]).days
            intervals.append(delta)
        
        if intervals:
            frequency_analysis[stream] = {
                'avg_days': round(statistics.mean(intervals), 1),
                'median_days': statistics.median(intervals),
                'min_days': min(intervals),
                'max_days': max(intervals),
                'total_draws': len(dates),
                'most_recent': sorted_dates[-1].isoformat()
            }
            
            print(f"  {stream}:")
            print(f"    Average: {frequency_analysis[stream]['avg_days']} days between draws")
            print(f"    Total draws: {frequency_analysis[stream]['total_draws']}")
    
    return frequency_analysis


def analyze_crs_trends(draws):
    """
    Analyze CRS score trends over time
    Detect if scores are rising, falling, or stable
    """
    print("\n📊 Analyzing CRS Score Trends...")
    
    by_stream = defaultdict(list)
    for draw in draws:
        if draw['min_score'] is not None:
            by_stream[draw['stream_category']].append({
                'date': draw['draw_date'],
                'score': draw['min_score']
            })
    
    trends = {}
    
    for stream, data in by_stream.items():
        if len(data) < 3:
            continue
        
        # Sort by date
        sorted_data = sorted(data, key=lambda x: x['date'])
        
        # Get recent vs older scores
        recent_scores = [d['score'] for d in sorted_data[-5:]]  # Last 5 draws
        older_scores = [d['score'] for d in sorted_data[-10:-5]] if len(sorted_data) >= 10 else []
        
        recent_avg = statistics.mean(recent_scores)
        
        # Determine trend
        trend = 'stable'
        if older_scores:
            older_avg = statistics.mean(older_scores)
            diff = recent_avg - older_avg
            
            if diff > 5:
                trend = 'increasing'
            elif diff < -5:
                trend = 'decreasing'
        
        trends[stream] = {
            'recent_avg': round(recent_avg, 1),
            'recent_min': min(recent_scores),
            'recent_max': max(recent_scores),
            'trend': trend,
            'data_points': len(sorted_data),
            'all_time_min': min(d['score'] for d in sorted_data),
            'all_time_max': max(d['score'] for d in sorted_data)
        }
        
        emoji = '📈' if trend == 'increasing' else '📉' if trend == 'decreasing' else '➡️'
        print(f"  {stream}:")
        print(f"    {emoji} Trend: {trend}")
        print(f"    Recent avg: {trends[stream]['recent_avg']} (range: {trends[stream]['recent_min']}-{trends[stream]['recent_max']})")
    
    return trends


def analyze_seasonal_patterns(draws):
    """
    Detect if draws are more frequent in certain months/quarters
    """
    print("\n🗓️  Analyzing Seasonal Patterns...")
    
    by_month = defaultdict(int)
    by_quarter = defaultdict(int)
    
    for draw in draws:
        month = draw['draw_date'].month
        quarter = (month - 1) // 3 + 1
        
        by_month[month] += 1
        by_quarter[quarter] += 1
    
    # Find most active periods
    most_active_month = max(by_month.items(), key=lambda x: x[1]) if by_month else (None, 0)
    most_active_quarter = max(by_quarter.items(), key=lambda x: x[1]) if by_quarter else (None, 0)
    
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    seasonal = {
        'by_month': dict(by_month),
        'by_quarter': dict(by_quarter),
        'most_active_month': {
            'month': month_names.get(most_active_month[0], 'N/A'),
            'count': most_active_month[1]
        },
        'most_active_quarter': {
            'quarter': f'Q{most_active_quarter[0]}',
            'count': most_active_quarter[1]
        }
    }
    
    if most_active_month[0]:
        print(f"  Most active month: {month_names[most_active_month[0]]} ({most_active_month[1]} draws)")
    if most_active_quarter[0]:
        print(f"  Most active quarter: Q{most_active_quarter[0]} ({most_active_quarter[1]} draws)")
    
    return seasonal


def analyze_invitation_trends(draws):
    """
    Analyze trends in number of invitations issued
    """
    print("\n✉️  Analyzing Invitation Volume Trends...")
    
    by_stream = defaultdict(list)
    for draw in draws:
        if draw['invitations_issued'] is not None:
            by_stream[draw['stream_category']].append({
                'date': draw['draw_date'],
                'invitations': draw['invitations_issued']
            })
    
    invitation_trends = {}
    
    for stream, data in by_stream.items():
        if not data:
            continue
        
        sorted_data = sorted(data, key=lambda x: x['date'])
        
        recent = [d['invitations'] for d in sorted_data[-5:]]
        all_time = [d['invitations'] for d in sorted_data]
        
        invitation_trends[stream] = {
            'recent_avg': round(statistics.mean(recent)),
            'recent_total': sum(recent),
            'all_time_avg': round(statistics.mean(all_time)),
            'all_time_total': sum(all_time),
            'min_issued': min(all_time),
            'max_issued': max(all_time)
        }
        
        print(f"  {stream}:")
        print(f"    Recent avg: {invitation_trends[stream]['recent_avg']} per draw")
        print(f"    All-time total: {invitation_trends[stream]['all_time_total']} invitations")
    
    return invitation_trends


def calculate_success_probabilities(draws):
    """
    Calculate approximate success rates by CRS score range
    Based on historical cutoff scores
    """
    print("\n🎯 Calculating Success Probability Estimates...")
    
    by_stream = defaultdict(list)
    for draw in draws:
        if draw['min_score'] is not None:
            by_stream[draw['stream_category']].append(draw['min_score'])
    
    probabilities = {}
    
    for stream, scores in by_stream.items():
        if len(scores) < 5:
            continue
        
        # Define score ranges
        ranges = [
            (0, 300, '0-300'),
            (301, 400, '301-400'),
            (401, 500, '401-500'),
            (501, 600, '501-600'),
            (601, 1200, '601+')
        ]
        
        range_success = {}
        
        for min_val, max_val, label in ranges:
            # Count how many draws had cutoff in or below this range
            successful_draws = sum(1 for s in scores if s <= max_val)
            total_draws = len(scores)
            
            if total_draws > 0:
                probability = (successful_draws / total_draws) * 100
                range_success[label] = {
                    'probability': round(probability, 1),
                    'interpretation': get_probability_interpretation(probability)
                }
        
        probabilities[stream] = {
            'by_range': range_success,
            'median_cutoff': statistics.median(scores),
            'recent_cutoff': scores[-1] if scores else None
        }
        
        print(f"  {stream}:")
        print(f"    Median cutoff: {probabilities[stream]['median_cutoff']}")
        for range_label, data in range_success.items():
            print(f"    {range_label}: {data['probability']}% - {data['interpretation']}")
    
    return probabilities


def get_probability_interpretation(prob):
    """Convert probability to human-readable interpretation"""
    if prob >= 90:
        return "Very High"
    elif prob >= 70:
        return "High"
    elif prob >= 50:
        return "Moderate"
    elif prob >= 30:
        return "Low"
    else:
        return "Very Low"


def generate_trend_report(draws):
    """
    Generate comprehensive trend analysis report
    """
    print("=" * 70)
    print("AAIP Historical Trend Analysis Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total draws analyzed: {len(draws)}")
    print("=" * 70)
    
    frequency = analyze_draw_frequency(draws)
    crs_trends = analyze_crs_trends(draws)
    seasonal = analyze_seasonal_patterns(draws)
    invitations = analyze_invitation_trends(draws)
    probabilities = calculate_success_probabilities(draws)
    
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_draws': len(draws),
            'date_range': {
                'earliest': min(d['draw_date'] for d in draws).isoformat(),
                'latest': max(d['draw_date'] for d in draws).isoformat()
            }
        },
        'draw_frequency': frequency,
        'crs_trends': crs_trends,
        'seasonal_patterns': seasonal,
        'invitation_trends': invitations,
        'success_probabilities': probabilities
    }
    
    return report


def save_trend_analysis(report, output_file='trend_analysis.json'):
    """Save trend analysis to JSON file"""
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Trend analysis saved to {output_path}")


def save_to_database(report):
    """Save trend analysis results to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table for trend analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trend_analysis (
                id SERIAL PRIMARY KEY,
                analysis_date DATE NOT NULL,
                report_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(analysis_date)
            )
        """)
        
        # Insert or update
        cursor.execute("""
            INSERT INTO trend_analysis (analysis_date, report_data)
            VALUES (CURRENT_DATE, %s)
            ON CONFLICT (analysis_date) 
            DO UPDATE SET
                report_data = EXCLUDED.report_data,
                created_at = CURRENT_TIMESTAMP
        """, (json.dumps(report),))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Trend analysis saved to database")
        
    except Exception as e:
        print(f"⚠️  Error saving to database: {e}")


def main():
    """Main execution"""
    try:
        print("\n" + "=" * 70)
        print("AAIP Historical Trend Analysis Engine")
        print("=" * 70)
        
        # Fetch historical data
        draws = get_historical_draws()
        
        if not draws:
            print("❌ No historical draw data found")
            return 1
        
        print(f"\n✓ Loaded {len(draws)} historical draws")
        
        # Generate comprehensive report
        report = generate_trend_report(draws)
        
        # Save results
        save_trend_analysis(report)
        save_to_database(report)
        
        print("\n" + "=" * 70)
        print("✅ Trend Analysis Complete!")
        print("=" * 70)
        print("\nKey Insights:")
        print("1. Draw frequency patterns identified")
        print("2. CRS score trends analyzed")
        print("3. Seasonal patterns detected")
        print("4. Success probabilities calculated")
        print("\nNext: Use this data for predictions in Phase 3.2")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
