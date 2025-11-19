#!/usr/bin/env python3
"""
Alberta Labor Market Quarterly Data Collector
Collects data from official sources to update the Labor Market Context page

Run quarterly: January, April, July, October
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
import sys

# Add parent directory to path for database imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Configuration
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


def get_current_quarter():
    """Get current quarter and year"""
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{quarter}", now.strftime("%B %Y")


def scrape_job_bank_outlook(noc_code):
    """
    Scrape Job Bank for occupation outlook in Alberta
    Returns: 'Good', 'Fair', 'Limited', or None
    """
    try:
        url = f"https://www.jobbank.gc.ca/marketreport/outlook-occupation/{noc_code}/48"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; AAIP-Tracker/1.0)'}
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find outlook text
        outlook_section = soup.find('div', class_='outlook-summary')
        if outlook_section:
            text = outlook_section.get_text()
            if 'good' in text.lower():
                return 'Good'
            elif 'fair' in text.lower():
                return 'Fair'
            elif 'limited' in text.lower():
                return 'Limited'
        
        return None
        
    except Exception as e:
        print(f"  ⚠️  Error scraping NOC {noc_code}: {e}")
        return None


def analyze_stream_demand(stream_name, noc_codes, aaip_data):
    """
    Analyze demand for a stream based on multiple factors
    Returns: demand_level, trend, summary
    """
    print(f"\n📊 Analyzing {stream_name}...")
    
    # Collect outlook data from Job Bank
    outlooks = []
    for noc in noc_codes:
        outlook = scrape_job_bank_outlook(noc)
        if outlook:
            outlooks.append(outlook)
            print(f"  NOC {noc}: {outlook}")
    
    # Calculate demand score (Good=3, Fair=2, Limited=1)
    outlook_scores = {'Good': 3, 'Fair': 2, 'Limited': 1}
    avg_score = sum(outlook_scores.get(o, 0) for o in outlooks) / max(len(outlooks), 1)
    
    # Get AAIP activity data (nominations, draws, pool size)
    recent_nominations = aaip_data.get('nominations', {}).get(stream_name, 0)
    recent_draws = aaip_data.get('draws', {}).get(stream_name, 0)
    pool_size = aaip_data.get('pool', {}).get(stream_name, 0)
    
    # Determine demand level
    if avg_score >= 2.5 or recent_nominations > 100:
        demand = 'strong'
    elif avg_score >= 1.5 or recent_nominations > 50:
        demand = 'moderate'
    else:
        demand = 'declining'
    
    # Determine trend (compare with previous quarter if available)
    # For now, base on recent activity
    if recent_draws > 3:
        trend = 'up'
    elif recent_draws < 2:
        trend = 'down'
    else:
        trend = 'stable'
    
    print(f"  → Demand: {demand}, Trend: {trend}")
    
    return demand, trend


def get_aaip_activity_data():
    """
    Get AAIP activity data from our database for the past 3 months
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        data = {
            'nominations': {},
            'draws': {},
            'pool': {}
        }
        
        # Get recent nominations by stream
        cursor.execute("""
            SELECT 
                stream_name,
                SUM(nominations_issued) as total_nominations
            FROM stream_data
            WHERE last_updated::timestamp >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY stream_name
        """)
        
        for row in cursor.fetchall():
            data['nominations'][row['stream_name']] = row['total_nominations'] or 0
        
        # Get recent draw counts by stream
        cursor.execute("""
            SELECT 
                stream_category,
                COUNT(*) as draw_count
            FROM aaip_draws
            WHERE draw_date::timestamp >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY stream_category
        """)
        
        for row in cursor.fetchall():
            data['draws'][row['stream_category']] = row['draw_count']
        
        # Get pool sizes
        cursor.execute("""
            SELECT 
                stream_name,
                candidate_count
            FROM eoi_pool
            WHERE timestamp = (SELECT MAX(timestamp) FROM eoi_pool)
        """)
        
        for row in cursor.fetchall():
            data['pool'][row['stream_name']] = row['candidate_count'] or 0
        
        cursor.close()
        conn.close()
        
        return data
        
    except Exception as e:
        print(f"⚠️  Could not get AAIP activity data: {e}")
        return {'nominations': {}, 'draws': {}, 'pool': {}}


def generate_stream_summaries():
    """
    Generate quarterly summaries for all streams
    """
    quarter, update_date = get_current_quarter()
    print("=" * 70)
    print(f"Alberta Labor Market Quarterly Data Collection")
    print(f"Quarter: {quarter} ({update_date})")
    print("=" * 70)
    
    # Get AAIP activity data
    aaip_data = get_aaip_activity_data()
    
    # Define streams and their key NOC codes
    streams = {
        'Healthcare (DHCP)': {
            'noc_codes': ['31301', '32101', '33102'],  # Nurses, LPNs, Healthcare Aides
            'sectors': ['Registered Nurses', 'Licensed Practical Nurses', 'Healthcare Aides', 'Medical Lab Technologists'],
            'stream_db_name': 'Dedicated Health Care Pathways'
        },
        'Tourism & Hospitality': {
            'noc_codes': ['62020', '63200', '64300'],  # Supervisors, Cooks, Hotel staff
            'sectors': ['Cooks', 'Food Service Supervisors', 'Hotel Front Desk', 'Restaurant Managers'],
            'stream_db_name': 'Tourism and Hospitality Stream'
        },
        'Technology (Accelerated Tech)': {
            'noc_codes': ['21231', '21232', '21233'],  # Software engineers, developers
            'sectors': ['Software Engineers', 'Data Scientists', 'DevOps Engineers', 'Cybersecurity'],
            'stream_db_name': 'Express Entry'
        },
        'Construction & Trades': {
            'noc_codes': ['72010', '72011', '72012', '72013'],  # Electricians, plumbers, carpenters
            'sectors': ['Electricians', 'Plumbers', 'Carpenters', 'Welders'],
            'stream_db_name': 'Alberta Opportunity Stream'
        },
        'Agriculture & Rural': {
            'noc_codes': ['82030', '84120', '94141'],  # Farm supervisors, meat cutters
            'sectors': ['Farm Supervisors', 'Agricultural Workers', 'Meat Cutters', 'Food Processing'],
            'stream_db_name': 'Rural Renewal Stream'
        },
        'General Business & Services': {
            'noc_codes': ['62010', '73300', '13110'],  # Retail, trucking, admin
            'sectors': ['Retail Supervisors', 'Truck Drivers', 'Administrative Assistants', 'Customer Service'],
            'stream_db_name': 'Alberta Opportunity Stream'
        }
    }
    
    results = {
        'quarter': quarter,
        'update_date': update_date,
        'generated_at': datetime.now().isoformat(),
        'streams': []
    }
    
    # Analyze each stream
    for stream_name, stream_info in streams.items():
        demand, trend = analyze_stream_demand(
            stream_name, 
            stream_info['noc_codes'],
            aaip_data
        )
        
        results['streams'].append({
            'name': stream_name,
            'demand': demand,
            'trend': trend,
            'sectors': stream_info['sectors'],
            'noc_codes': stream_info['noc_codes']
        })
    
    return results


def save_to_database(data):
    """
    Save quarterly labor market data to database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labor_market_quarterly (
                id SERIAL PRIMARY KEY,
                quarter VARCHAR(10) NOT NULL,
                update_date VARCHAR(50) NOT NULL,
                stream_name VARCHAR(255) NOT NULL,
                demand_level VARCHAR(20) NOT NULL,
                trend VARCHAR(20) NOT NULL,
                sectors TEXT,
                noc_codes TEXT,
                generated_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(quarter, stream_name)
            )
        """)
        
        # Insert data for each stream
        for stream in data['streams']:
            cursor.execute("""
                INSERT INTO labor_market_quarterly 
                (quarter, update_date, stream_name, demand_level, trend, sectors, noc_codes, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (quarter, stream_name) 
                DO UPDATE SET
                    demand_level = EXCLUDED.demand_level,
                    trend = EXCLUDED.trend,
                    sectors = EXCLUDED.sectors,
                    noc_codes = EXCLUDED.noc_codes,
                    generated_at = EXCLUDED.generated_at
            """, (
                data['quarter'],
                data['update_date'],
                stream['name'],
                stream['demand'],
                stream['trend'],
                json.dumps(stream['sectors']),
                json.dumps(stream['noc_codes']),
                data['generated_at']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Saved {len(data['streams'])} stream summaries to database")
        
    except Exception as e:
        print(f"\n❌ Error saving to database: {e}")
        raise


def export_to_json(data, output_file='labor_market_data.json'):
    """
    Export data to JSON file for manual review
    """
    try:
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported data to {output_path}")
        
    except Exception as e:
        print(f"❌ Error exporting to JSON: {e}")


def main():
    """
    Main execution function
    """
    try:
        # Generate quarterly summaries
        data = generate_stream_summaries()
        
        # Save to database
        save_to_database(data)
        
        # Export to JSON for review
        export_to_json(data)
        
        print("\n" + "=" * 70)
        print("✅ Quarterly data collection complete!")
        print("=" * 70)
        print(f"\nQuarter: {data['quarter']}")
        print(f"Streams analyzed: {len(data['streams'])}")
        print(f"\nNext steps:")
        print("1. Review the generated labor_market_data.json file")
        print("2. Manually refine summaries and recommendations")
        print("3. Frontend will automatically load from database")
        print("4. Update again next quarter (in 3 months)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
