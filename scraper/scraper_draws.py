#!/usr/bin/env python3
"""
AAIP Data Scraper with Draw Records Collection
Incrementally collects draw information from AAIP website
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
import re
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
        
        # Read and execute the draws schema
        schema_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup_db_draws.sql')
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                cursor.execute(f.read())
        
        # Ensure main tables exist (from original scraper)
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
                message TEXT,
                draws_collected INTEGER DEFAULT 0,
                new_draws_added INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def parse_date(date_str):
    """Parse date string to date object"""
    try:
        # Handle various date formats
        # "October 29, 2025" or "October 29, 2025"
        date_str = date_str.strip()
        return datetime.strptime(date_str, "%B %d, %Y").date()
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None


def parse_number(num_str):
    """Parse number string, handling 'Less than 10' etc."""
    try:
        num_str = num_str.strip().lower()
        if 'less than' in num_str:
            # Extract the number after "less than"
            match = re.search(r'less than (\d+)', num_str)
            if match:
                return int(match.group(1)) - 1  # Return n-1 for "less than n"
            return 5  # Default to 5 for "Less than 10"
        # Remove commas and convert
        return int(num_str.replace(',', ''))
    except Exception as e:
        print(f"Error parsing number '{num_str}': {e}")
        return None


def categorize_stream(stream_text):
    """
    Categorize stream into main category and detail
    Returns: (stream_category, stream_detail)
    """
    stream_text = stream_text.strip()
    
    # Define main categories and their patterns
    categories = {
        'Alberta Opportunity Stream': ['Alberta Opportunity Stream'],
        'Alberta Express Entry Stream': ['Alberta Express Entry'],
        'Dedicated Health Care Pathway': ['Dedicated Health Care Pathway'],
        'Tourism and Hospitality Stream': ['Tourism and Hospitality Stream'],
        'Rural Renewal Stream': ['Rural Renewal Stream'],
    }
    
    # Find main category
    main_category = None
    for category, patterns in categories.items():
        for pattern in patterns:
            if pattern in stream_text:
                main_category = category
                break
        if main_category:
            break
    
    if not main_category:
        main_category = 'Other'
    
    # Extract detail (what comes after the main category or dash)
    detail = None
    
    # Check for specific patterns
    if '–' in stream_text:
        parts = stream_text.split('–', 1)
        if len(parts) > 1:
            detail = parts[1].strip()
    elif 'Priority Sectors' in stream_text:
        # Extract sector in parentheses
        match = re.search(r'\(([^)]+)\)', stream_text)
        if match:
            detail = match.group(1)
    
    # Special handling for specific streams
    if 'Accelerated Tech Pathway' in stream_text:
        detail = 'Accelerated Tech Pathway'
    elif 'Law Enforcement Pathway' in stream_text:
        detail = 'Law Enforcement Pathway'
    
    return main_category, detail


def scrape_draw_data():
    """Scrape AAIP draw information from the website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"Fetching data from {AAIP_URL}...")
        response = requests.get(AAIP_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find the draw information table
        # Look for "Table 9" or heading containing "Draw information"
        tables = soup.find_all('table')
        draw_table = None
        
        for table in tables:
            # Check if table has the expected columns
            thead = table.find('thead')
            if thead:
                headers_text = thead.get_text()
                if 'Draw date' in headers_text and 'Worker stream' in headers_text:
                    draw_table = table
                    break
        
        if not draw_table:
            raise ValueError("Could not find draw information table")
        
        # Parse table rows
        tbody = draw_table.find('tbody')
        if not tbody:
            raise ValueError("Draw table has no tbody")
        
        rows = tbody.find_all('tr')
        draw_records = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            # Extract data
            draw_date_str = cells[0].get_text(strip=True)
            stream_text = cells[1].get_text(strip=True)
            min_score_str = cells[2].get_text(strip=True)
            invitations_str = cells[3].get_text(strip=True)
            
            # Parse values
            draw_date = parse_date(draw_date_str)
            min_score = parse_number(min_score_str)
            invitations = parse_number(invitations_str)
            
            if not draw_date:
                continue
            
            # Categorize stream
            stream_category, stream_detail = categorize_stream(stream_text)
            
            draw_record = {
                'draw_date': draw_date,
                'stream_category': stream_category,
                'stream_detail': stream_detail,
                'min_score': min_score,
                'invitations_issued': invitations,
            }
            
            draw_records.append(draw_record)
        
        print(f"Successfully scraped {len(draw_records)} draw records")
        return draw_records
        
    except Exception as e:
        print(f"Error scraping draw data: {e}")
        raise


def save_draws_to_database(draw_records):
    """
    Save draw records to database with incremental logic
    Returns: (total_processed, new_added)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        new_added = 0
        total_processed = len(draw_records)
        
        for record in draw_records:
            # Use INSERT ... ON CONFLICT to handle duplicates
            cursor.execute('''
                INSERT INTO aaip_draws 
                (draw_date, stream_category, stream_detail, min_score, invitations_issued)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (draw_date, stream_category, stream_detail) 
                DO UPDATE SET
                    min_score = EXCLUDED.min_score,
                    invitations_issued = EXCLUDED.invitations_issued,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING (xmax = 0) AS inserted
            ''', (
                record['draw_date'],
                record['stream_category'],
                record['stream_detail'],
                record['min_score'],
                record['invitations_issued']
            ))
            
            result = cursor.fetchone()
            if result and result[0]:  # New record inserted
                new_added += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Processed {total_processed} records, {new_added} new records added")
        return total_processed, new_added
        
    except Exception as e:
        print(f"Error saving draws to database: {e}")
        raise


def scrape_summary_data():
    """Scrape AAIP summary data (keep existing functionality)"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
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
        
        # Extract numeric values
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
        
        return data
        
    except Exception as e:
        print(f"Error scraping summary data: {e}")
        raise


def save_summary_to_database(data):
    """Save summary data to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error saving summary to database: {e}")
        raise


def log_scrape_result(status, message, draws_collected=0, new_draws=0):
    """Log scrape result to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scrape_log (timestamp, status, message, draws_collected, new_draws_added)
            VALUES (%s, %s, %s, %s, %s)
        ''', (datetime.now(), status, message, draws_collected, new_draws))
        
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass


def main():
    """Main function"""
    print("=" * 60)
    print("AAIP Data Scraper with Draw Records (PostgreSQL)")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        init_database()
        
        # Scrape summary data
        print("\n[1/3] Scraping summary data...")
        summary_data = scrape_summary_data()
        save_summary_to_database(summary_data)
        print(f"✓ Summary data saved")
        
        # Scrape draw data
        print("\n[2/3] Scraping draw records...")
        draw_records = scrape_draw_data()
        
        # Save draw data with incremental logic
        print("\n[3/3] Saving draw records to database...")
        total_draws, new_draws = save_draws_to_database(draw_records)
        
        # Log success
        message = f"Scraped {total_draws} draws, {new_draws} new records added"
        log_scrape_result('success', message, total_draws, new_draws)
        
        print(f"\n{'=' * 60}")
        print("✓ Scraping completed successfully!")
        print(f"  - Summary data: Updated")
        print(f"  - Draw records processed: {total_draws}")
        print(f"  - New draw records added: {new_draws}")
        print(f"{'=' * 60}")
        
        return 0
        
    except Exception as e:
        error_msg = f"Scraping failed: {e}"
        log_scrape_result('error', error_msg, 0, 0)
        print(f"\n✗ {error_msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
