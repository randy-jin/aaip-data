#!/usr/bin/env python3
"""
AAIP Data Scraper with PostgreSQL
Scrapes Alberta Advantage Immigration Program processing information
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AAIP_URL = "https://www.alberta.ca/aaip-processing-information"
DATABASE_URL = os.getenv('DATABASE_URL')

# Alternative: individual parameters
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


def init_database():
    """Initialize PostgreSQL database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aaip_summary (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                nomination_allocation INTEGER,
                nominations_issued INTEGER,
                nomination_spaces_remaining INTEGER,
                applications_to_process INTEGER,
                last_updated TEXT,
                UNIQUE(timestamp)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                message TEXT
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_aaip_summary_timestamp 
            ON aaip_summary(timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scrape_log_timestamp 
            ON scrape_log(timestamp DESC)
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def scrape_aaip_data():
    """Scrape AAIP processing information from the website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"Fetching data from {AAIP_URL}...")
        response = requests.get(AAIP_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find the "2025 summary" section
        summary_heading = soup.find('h2', string='2025 summary')
        if not summary_heading:
            raise ValueError("Could not find '2025 summary' heading")
        
        # Find the table after the heading
        table = summary_heading.find_next('table')
        if not table:
            raise ValueError("Could not find summary table")
        
        # Extract data from table
        tbody = table.find('tbody')
        if not tbody:
            raise ValueError("Could not find table body")
        
        row = tbody.find('tr')
        cells = row.find_all('td')
        
        if len(cells) < 4:
            raise ValueError(f"Expected 4 cells, found {len(cells)}")
        
        # Extract numeric values (remove commas and convert to int)
        data = {
            'nomination_allocation': int(cells[0].text.strip().replace(',', '')),
            'nominations_issued': int(cells[1].text.strip().replace(',', '')),
            'nomination_spaces_remaining': int(cells[2].text.strip().replace(',', '')),
            'applications_to_process': int(cells[3].text.strip().replace(',', '')),
        }
        
        # Find "Last updated" date
        last_updated = None
        strong_tags = soup.find_all('strong')
        for tag in strong_tags:
            if 'Last updated' in tag.text:
                last_updated = tag.next_sibling
                if last_updated:
                    last_updated = last_updated.strip(': ')
                break
        
        data['last_updated'] = last_updated
        data['timestamp'] = datetime.now()
        
        print(f"Successfully scraped data: {data}")
        return data
        
    except Exception as e:
        print(f"Error scraping data: {e}")
        raise


def save_to_database(data):
    """Save scraped data to PostgreSQL database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert data (ignore if duplicate timestamp)
        cursor.execute('''
            INSERT INTO aaip_summary 
            (timestamp, nomination_allocation, nominations_issued, 
             nomination_spaces_remaining, applications_to_process, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp) DO NOTHING
        ''', (
            data['timestamp'],
            data['nomination_allocation'],
            data['nominations_issued'],
            data['nomination_spaces_remaining'],
            data['applications_to_process'],
            data.get('last_updated')
        ))
        
        # Log successful scrape
        cursor.execute('''
            INSERT INTO scrape_log (timestamp, status, message)
            VALUES (%s, %s, %s)
        ''', (datetime.now(), 'success', 'Data scraped successfully'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Data saved to database successfully")
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        # Log failed scrape
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scrape_log (timestamp, status, message)
                VALUES (%s, %s, %s)
            ''', (datetime.now(), 'error', str(e)))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass
        raise


def main():
    """Main function"""
    print("=" * 50)
    print("AAIP Data Scraper (PostgreSQL)")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 50)
    
    try:
        init_database()
        data = scrape_aaip_data()
        save_to_database(data)
        print("\n✓ Scraping completed successfully!")
        return 0
    except Exception as e:
        print(f"\n✗ Scraping failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
