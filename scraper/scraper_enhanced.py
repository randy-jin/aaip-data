#!/usr/bin/env python3
"""
Enhanced AAIP Data Scraper with Multi-Stream Support
Scrapes data for all AAIP streams and pathways
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


def extract_number(text):
    """Extract number from text, handling 'Less than 10' cases"""
    if not text:
        return None
    text = text.strip().replace(',', '')
    if 'less than' in text.lower():
        return 5  # Use 5 as approximate for "Less than 10"
    try:
        return int(text)
    except:
        return None


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
        
        # Find "Last updated" date
        last_updated = None
        strong_tags = soup.find_all('strong')
        for tag in strong_tags:
            if 'Last updated' in tag.text:
                last_updated = tag.next_sibling
                if last_updated:
                    last_updated = last_updated.strip(': ')
                break
        
        current_time = datetime.now()
        all_data = {
            'summary': None,
            'streams': [],
            'last_updated': last_updated,
            'timestamp': current_time
        }
        
        # 1. Scrape Overall Summary (2025 summary)
        print("Scraping overall summary...")
        summary_heading = soup.find('h2', string='2025 summary')
        if summary_heading:
            table = summary_heading.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        all_data['summary'] = {
                            'nomination_allocation': extract_number(cells[0].text),
                            'nominations_issued': extract_number(cells[1].text),
                            'nomination_spaces_remaining': extract_number(cells[2].text),
                            'applications_to_process': extract_number(cells[3].text)
                        }
                        print(f"  ✓ Overall summary: {all_data['summary']}")
        
        # 2. Scrape Alberta Opportunity Stream
        print("Scraping Alberta Opportunity Stream...")
        aos_heading = soup.find('h2', string='Alberta Opportunity Stream')
        if aos_heading:
            table = aos_heading.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        all_data['streams'].append({
                            'stream_name': 'Alberta Opportunity Stream',
                            'stream_type': 'main',
                            'parent_stream': None,
                            'nomination_allocation': extract_number(cells[0].text),
                            'nominations_issued': extract_number(cells[1].text),
                            'nomination_spaces_remaining': extract_number(cells[2].text),
                            'applications_to_process': extract_number(cells[3].text),
                            'processing_date': cells[4].text.strip() if len(cells) > 4 else None
                        })
                        print(f"  ✓ Alberta Opportunity Stream collected")
        
        # 3. Scrape Rural Renewal Stream
        print("Scraping Rural Renewal Stream...")
        rrs_heading = soup.find('h2', string='Rural Renewal Stream')
        if rrs_heading:
            table = rrs_heading.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        all_data['streams'].append({
                            'stream_name': 'Rural Renewal Stream',
                            'stream_type': 'main',
                            'parent_stream': None,
                            'nomination_allocation': extract_number(cells[0].text),
                            'nominations_issued': extract_number(cells[1].text),
                            'nomination_spaces_remaining': extract_number(cells[2].text),
                            'applications_to_process': extract_number(cells[3].text),
                            'processing_date': cells[4].text.strip() if len(cells) > 4 else None
                        })
                        print(f"  ✓ Rural Renewal Stream collected")
        
        # 4. Scrape Tourism and Hospitality Stream
        print("Scraping Tourism and Hospitality Stream...")
        ths_heading = soup.find('h2', string='Tourism and Hospitality Stream')
        if ths_heading:
            table = ths_heading.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        all_data['streams'].append({
                            'stream_name': 'Tourism and Hospitality Stream',
                            'stream_type': 'main',
                            'parent_stream': None,
                            'nomination_allocation': extract_number(cells[0].text),
                            'nominations_issued': extract_number(cells[1].text),
                            'nomination_spaces_remaining': extract_number(cells[2].text),
                            'applications_to_process': extract_number(cells[3].text),
                            'processing_date': cells[4].text.strip() if len(cells) > 4 else None
                        })
                        print(f"  ✓ Tourism and Hospitality Stream collected")
        
        # 5. Scrape Dedicated Health Care Pathways
        print("Scraping Dedicated Health Care Pathways...")
        dhc_heading = soup.find('h2', string='Dedicated Health Care Pathways')
        if dhc_heading:
            table = dhc_heading.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        all_data['streams'].append({
                            'stream_name': 'Dedicated Health Care Pathways',
                            'stream_type': 'main',
                            'parent_stream': None,
                            'nomination_allocation': extract_number(cells[0].text),
                            'nominations_issued': extract_number(cells[1].text),
                            'nomination_spaces_remaining': extract_number(cells[2].text),
                            'applications_to_process': extract_number(cells[3].text),
                            'processing_date': cells[4].text.strip() if len(cells) > 4 else None
                        })
                        print(f"  ✓ Dedicated Health Care Pathways collected")
        
        # 6. Scrape Alberta Express Entry Stream (with sub-pathways)
        print("Scraping Alberta Express Entry Stream...")
        aee_heading = soup.find('h2', string='Alberta Express Entry Stream')
        if aee_heading:
            table = aee_heading.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 6:
                            pathway_name = cells[0].text.strip()
                            all_data['streams'].append({
                                'stream_name': f"Express Entry - {pathway_name}",
                                'stream_type': 'sub-pathway',
                                'parent_stream': 'Alberta Express Entry Stream',
                                'nomination_allocation': extract_number(cells[1].text),
                                'nominations_issued': extract_number(cells[2].text),
                                'nomination_spaces_remaining': extract_number(cells[3].text),
                                'applications_to_process': extract_number(cells[4].text),
                                'processing_date': cells[5].text.strip() if len(cells) > 5 else None
                            })
                            print(f"  ✓ {pathway_name} collected")
        
        # 7. Scrape Entrepreneur Streams
        print("Scraping Entrepreneur Streams...")
        ent_heading = soup.find('h2', string='Entrepreneur Streams')
        if ent_heading:
            table = ent_heading.find_next('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    row = tbody.find('tr')
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        all_data['streams'].append({
                            'stream_name': 'Entrepreneur Streams',
                            'stream_type': 'main',
                            'parent_stream': None,
                            'nomination_allocation': extract_number(cells[0].text),
                            'nominations_issued': extract_number(cells[1].text),
                            'nomination_spaces_remaining': extract_number(cells[2].text),
                            'applications_to_process': extract_number(cells[3].text),
                            'processing_date': cells[4].text.strip() if len(cells) > 4 else None
                        })
                        print(f"  ✓ Entrepreneur Streams collected")
        
        print(f"\n✓ Successfully scraped {len(all_data['streams'])} streams")
        return all_data
        
    except Exception as e:
        print(f"Error scraping data: {e}")
        raise


def check_data_changed(data):
    """Check if data has changed compared to the last record"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check overall summary change
        cursor.execute('''
            SELECT nomination_allocation, nominations_issued, 
                   nomination_spaces_remaining, applications_to_process
            FROM aaip_summary
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        last_summary = cursor.fetchone()
        
        if last_summary:
            current = data['summary']
            if (current['nomination_allocation'] == last_summary[0] and
                current['nominations_issued'] == last_summary[1] and
                current['nomination_spaces_remaining'] == last_summary[2] and
                current['applications_to_process'] == last_summary[3]):
                
                # Check if all streams are also unchanged
                all_unchanged = True
                for stream in data['streams']:
                    cursor.execute('''
                        SELECT nomination_allocation, nominations_issued, 
                               nomination_spaces_remaining, applications_to_process
                        FROM stream_data
                        WHERE stream_name = %s
                        ORDER BY timestamp DESC
                        LIMIT 1
                    ''', (stream['stream_name'],))
                    
                    last_stream = cursor.fetchone()
                    if last_stream:
                        if (stream['nomination_allocation'] != last_stream[0] or
                            stream['nominations_issued'] != last_stream[1] or
                            stream['nomination_spaces_remaining'] != last_stream[2] or
                            stream['applications_to_process'] != last_stream[3]):
                            all_unchanged = False
                            break
                    else:
                        # New stream, definitely changed
                        all_unchanged = False
                        break
                
                cursor.close()
                conn.close()
                return not all_unchanged  # True if any change detected
        
        cursor.close()
        conn.close()
        return True  # First run or no previous data, save it
        
    except Exception as e:
        print(f"Warning: Could not check previous data: {e}")
        return True  # On error, save anyway


def save_to_database(data):
    """Save scraped data to PostgreSQL database (only if changed)"""
    try:
        # Check if data has changed
        has_changed = check_data_changed(data)
        
        if not has_changed:
            print("⊘ No changes detected - skipping save")
            
            # Log that we checked but didn't save
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scrape_log (timestamp, status, message, streams_collected)
                VALUES (%s, %s, %s, %s)
            ''', (datetime.now(), 'no_change', 'Data unchanged, not saved', 0))
            conn.commit()
            cursor.close()
            conn.close()
            return
        
        print("✓ Changes detected - saving data...")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        streams_saved = 0
        
        # Save overall summary
        if data['summary']:
            cursor.execute('''
                INSERT INTO aaip_summary 
                (timestamp, nomination_allocation, nominations_issued, 
                 nomination_spaces_remaining, applications_to_process, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                data['timestamp'],
                data['summary']['nomination_allocation'],
                data['summary']['nominations_issued'],
                data['summary']['nomination_spaces_remaining'],
                data['summary']['applications_to_process'],
                data.get('last_updated')
            ))
        
        # Save individual stream data
        for stream in data['streams']:
            cursor.execute('''
                INSERT INTO stream_data 
                (timestamp, stream_name, stream_type, parent_stream,
                 nomination_allocation, nominations_issued, 
                 nomination_spaces_remaining, applications_to_process,
                 processing_date, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['timestamp'],
                stream['stream_name'],
                stream['stream_type'],
                stream.get('parent_stream'),
                stream['nomination_allocation'],
                stream['nominations_issued'],
                stream['nomination_spaces_remaining'],
                stream['applications_to_process'],
                stream.get('processing_date'),
                data.get('last_updated')
            ))
            streams_saved += 1
        
        # Log successful scrape with save
        cursor.execute('''
            INSERT INTO scrape_log (timestamp, status, message, streams_collected)
            VALUES (%s, %s, %s, %s)
        ''', (datetime.now(), 'success', f'Data changed and saved', streams_saved))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Data saved to database ({streams_saved} streams)")
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        # Log failed scrape
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scrape_log (timestamp, status, message, streams_collected)
                VALUES (%s, %s, %s, %s)
            ''', (datetime.now(), 'error', str(e), 0))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass
        raise


def main():
    """Main function"""
    print("=" * 60)
    print("AAIP Enhanced Data Scraper (Multi-Stream)")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        data = scrape_aaip_data()
        save_to_database(data)
        print("\n" + "=" * 60)
        print("✓ Scraping completed successfully!")
        print(f"  - Overall summary: {'✓' if data['summary'] else '✗'}")
        print(f"  - Individual streams: {len(data['streams'])}")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ Scraping failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
