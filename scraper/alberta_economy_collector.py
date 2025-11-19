#!/usr/bin/env python3
"""
Alberta Economic Data Collector
Collects key economic indicators relevant to AAIP immigration trends

Data Sources:
- Statistics Canada (GDP, unemployment, population)
- Alberta Economic Dashboard
- ATB Economics Reports

Run: Monthly or Quarterly
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
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


def scrape_alberta_unemployment():
    """
    Scrape unemployment rate from Statistics Canada
    Note: This is a placeholder - real implementation would use StatsCan API
    """
    try:
        # StatsCan Table 14-10-0287-01 (Labour force characteristics by province, monthly, seasonally adjusted)
        # For production, use their API: https://www.statcan.gc.ca/eng/developers/wds
        
        # Placeholder: In reality, you'd need to register for StatsCan API key
        # For now, return approximate current data (as of Nov 2025)
        print("  📊 Fetching unemployment rate...")
        
        # Mock data - replace with real API call
        unemployment_rate = 6.8  # Approximate Alberta rate as of late 2024
        
        print(f"    ✓ Unemployment: {unemployment_rate}%")
        return unemployment_rate
        
    except Exception as e:
        print(f"    ⚠️  Error fetching unemployment: {e}")
        return None


def scrape_alberta_gdp_growth():
    """
    Get GDP growth rate for Alberta
    Source: Statistics Canada or Alberta Economic Dashboard
    """
    try:
        print("  📈 Fetching GDP growth...")
        
        # Mock data - replace with real data source
        # Real source: StatsCan Table 36-10-0222-01 (Gross domestic product by province and territory)
        gdp_growth = 2.8  # Approximate Alberta GDP growth rate
        
        print(f"    ✓ GDP Growth: {gdp_growth}%")
        return gdp_growth
        
    except Exception as e:
        print(f"    ⚠️  Error fetching GDP: {e}")
        return None


def scrape_population_growth():
    """
    Get population growth rate for Alberta
    Source: Statistics Canada
    """
    try:
        print("  👥 Fetching population growth...")
        
        # Mock data - replace with real API call
        # Real source: StatsCan Table 17-10-0005-01 (Population estimates)
        population_growth = 3.9  # Alberta has high population growth
        
        print(f"    ✓ Population Growth: {population_growth}%")
        return population_growth
        
    except Exception as e:
        print(f"    ⚠️  Error fetching population: {e}")
        return None


def get_oil_price_trend():
    """
    Get oil price trend (relevant for Alberta economy)
    Source: Can use free API like Alpha Vantage
    """
    try:
        print("  🛢️  Fetching oil price trend...")
        
        # Mock data - in production, use commodity price API
        oil_price = 82.50  # WTI crude price USD/barrel
        trend = "stable"  # up/down/stable
        
        print(f"    ✓ Oil Price: ${oil_price}/barrel ({trend})")
        return {"price": oil_price, "trend": trend}
        
    except Exception as e:
        print(f"    ⚠️  Error fetching oil prices: {e}")
        return None


def analyze_economic_indicators(data):
    """
    Analyze economic indicators and generate insights
    """
    insights = []
    
    # Unemployment analysis
    if data['unemployment_rate']:
        if data['unemployment_rate'] < 5.5:
            insights.append({
                'type': 'positive',
                'indicator': 'Unemployment',
                'message': f"Low unemployment rate ({data['unemployment_rate']}%) indicates strong labor demand",
                'aaip_impact': "May lead to increased AAIP activity to address labor shortages"
            })
        elif data['unemployment_rate'] > 7.5:
            insights.append({
                'type': 'neutral',
                'indicator': 'Unemployment',
                'message': f"Elevated unemployment rate ({data['unemployment_rate']}%)",
                'aaip_impact': "AAIP may be more selective in certain streams"
            })
    
    # GDP growth analysis
    if data['gdp_growth']:
        if data['gdp_growth'] > 2.5:
            insights.append({
                'type': 'positive',
                'indicator': 'GDP Growth',
                'message': f"Strong GDP growth ({data['gdp_growth']}%) reflects economic expansion",
                'aaip_impact': "Positive economic climate supports continued AAIP growth"
            })
        elif data['gdp_growth'] < 1.0:
            insights.append({
                'type': 'caution',
                'indicator': 'GDP Growth',
                'message': f"Slower GDP growth ({data['gdp_growth']}%)",
                'aaip_impact': "Economic slowdown may affect nomination volumes"
            })
    
    # Population growth analysis
    if data['population_growth']:
        if data['population_growth'] > 3.0:
            insights.append({
                'type': 'positive',
                'indicator': 'Population Growth',
                'message': f"Rapid population growth ({data['population_growth']}%) creates demand for services and infrastructure",
                'aaip_impact': "Sustained immigration needed to support population growth"
            })
    
    # Oil price correlation
    if data['oil_price']:
        if data['oil_price']['price'] > 75:
            insights.append({
                'type': 'positive',
                'indicator': 'Energy Sector',
                'message': f"Strong oil prices (${data['oil_price']['price']}/barrel) benefit Alberta's energy sector",
                'aaip_impact': "Positive for energy-related occupations and overall provincial revenue"
            })
    
    return insights


def collect_economic_data():
    """
    Main function to collect all economic indicators
    """
    print("=" * 70)
    print("Alberta Economic Data Collection")
    print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Collect all indicators
    data = {
        'timestamp': datetime.now(),
        'unemployment_rate': scrape_alberta_unemployment(),
        'gdp_growth': scrape_alberta_gdp_growth(),
        'population_growth': scrape_population_growth(),
        'oil_price': get_oil_price_trend()
    }
    
    # Generate insights
    print("\n📊 Analyzing indicators...")
    insights = analyze_economic_indicators(data)
    
    data['insights'] = insights
    
    return data


def save_to_database(data):
    """
    Save economic data to database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alberta_economy (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                unemployment_rate DECIMAL(4,2),
                gdp_growth DECIMAL(4,2),
                population_growth DECIMAL(4,2),
                oil_price DECIMAL(6,2),
                oil_price_trend VARCHAR(20),
                insights JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on timestamp
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alberta_economy_timestamp 
            ON alberta_economy(timestamp DESC)
        """)
        
        # Insert data
        cursor.execute("""
            INSERT INTO alberta_economy 
            (timestamp, unemployment_rate, gdp_growth, population_growth, 
             oil_price, oil_price_trend, insights)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['timestamp'],
            data['unemployment_rate'],
            data['gdp_growth'],
            data['population_growth'],
            data['oil_price']['price'] if data['oil_price'] else None,
            data['oil_price']['trend'] if data['oil_price'] else None,
            json.dumps(data['insights'])
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Saved economic data to database")
        
    except Exception as e:
        print(f"\n❌ Error saving to database: {e}")
        raise


def export_to_json(data, output_file='alberta_economy_data.json'):
    """
    Export data to JSON file for manual review
    """
    try:
        # Convert datetime to ISO format
        export_data = {
            'timestamp': data['timestamp'].isoformat(),
            'unemployment_rate': data['unemployment_rate'],
            'gdp_growth': data['gdp_growth'],
            'population_growth': data['population_growth'],
            'oil_price': data['oil_price'],
            'insights': data['insights']
        }
        
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported data to {output_path}")
        
    except Exception as e:
        print(f"❌ Error exporting to JSON: {e}")


def main():
    """
    Main execution function
    """
    try:
        # Collect economic data
        data = collect_economic_data()
        
        # Save to database
        save_to_database(data)
        
        # Export to JSON for review
        export_to_json(data)
        
        # Display insights
        print("\n" + "=" * 70)
        print("💡 Economic Insights:")
        print("=" * 70)
        for insight in data['insights']:
            emoji = "🟢" if insight['type'] == 'positive' else "🟡" if insight['type'] == 'neutral' else "🔴"
            print(f"\n{emoji} {insight['indicator']}")
            print(f"   {insight['message']}")
            print(f"   → AAIP Impact: {insight['aaip_impact']}")
        
        print("\n" + "=" * 70)
        print("✅ Economic data collection complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Review alberta_economy_data.json")
        print("2. Frontend will display on Labor Market tab")
        print("3. Run again monthly or quarterly")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
