#!/usr/bin/env python3
"""
AAIP Data Scraper - Consolidated Version
Collects both nomination/processing data and draw records from AAIP website
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


def extract_number(text):
    """Extract number from text, handling 'Less than 10' cases"""
    if not text:
        return None
    text = text.strip().replace(',', '')
    if 'less than' in text.lower():
        # Extract the number after "less than"
        match = re.search(r'less than (\d+)', text.lower())
        if match:
            return int(match.group(1)) - 1  # Return n-1 for "less than n"
        return 5  # Default to 5 for "Less than 10"
    try:
        return int(text)
    except:
        return None


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
            'draws': [],
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

        # 8. Scrape Draw Information
        print("Scraping draw records...")
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

        if draw_table:
            tbody = draw_table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
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
                    min_score = extract_number(min_score_str)
                    invitations = extract_number(invitations_str)

                    if not draw_date:
                        continue

                    # Categorize stream
                    stream_category, stream_detail = categorize_stream(stream_text)

                    all_data['draws'].append({
                        'draw_date': draw_date,
                        'stream_category': stream_category,
                        'stream_detail': stream_detail,
                        'min_score': min_score,
                        'invitations_issued': invitations,
                    })

                print(f"  ✓ {len(all_data['draws'])} draw records collected")
        else:
            print("  ⚠ Draw table not found (this is normal if no draws published yet)")

        print(f"\n✓ Successfully scraped {len(all_data['streams'])} streams and {len(all_data['draws'])} draws")
        return all_data

    except Exception as e:
        print(f"Error scraping data: {e}")
        raise


def check_data_changed(data):
    """Check if stream data has changed since last scrape"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get the most recent summary record
        cursor.execute('''
            SELECT nomination_allocation, nominations_issued,
                   nomination_spaces_remaining, applications_to_process
            FROM aaip_summary
            ORDER BY timestamp DESC
            LIMIT 1
        ''')

        last_summary = cursor.fetchone()
        cursor.close()
        conn.close()

        # If no previous data, it's changed
        if not last_summary:
            return True

        # Compare with current data
        if data['summary']:
            current = data['summary']
            if (current['nomination_allocation'] != last_summary['nomination_allocation'] or
                current['nominations_issued'] != last_summary['nominations_issued'] or
                current['nomination_spaces_remaining'] != last_summary['nomination_spaces_remaining'] or
                current['applications_to_process'] != last_summary['applications_to_process']):
                return True

        return False

    except Exception as e:
        print(f"Error checking data change: {e}")
        # If we can't check, assume it changed
        return True


def save_to_database(data):
    """Save scraped data to PostgreSQL database (only stream data if changed)"""
    try:
        # Check if stream data has changed
        has_changed = check_data_changed(data)

        conn = get_db_connection()
        cursor = conn.cursor()

        streams_saved = 0
        draws_new = 0
        draws_total = len(data['draws'])

        # Always save stream data if changed
        if has_changed:
            print("✓ Stream data changes detected - saving...")

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

            print(f"  ✓ Saved {streams_saved} stream records")
        else:
            print("⊘ No stream data changes - skipping stream save")

        # Always save draw data (incremental with conflict resolution)
        if data['draws']:
            print(f"Saving {draws_total} draw records...")
            for draw in data['draws']:
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
                    draw['draw_date'],
                    draw['stream_category'],
                    draw['stream_detail'],
                    draw['min_score'],
                    draw['invitations_issued']
                ))

                result = cursor.fetchone()
                if result and result[0]:  # New record inserted
                    draws_new += 1

            print(f"  ✓ Processed {draws_total} draws, {draws_new} new records added")

        # Log the scrape
        status = 'success' if (has_changed or draws_new > 0) else 'no_change'
        message = f"Streams: {'saved' if has_changed else 'unchanged'}, Draws: {draws_new} new/{draws_total} total"
        cursor.execute('''
            INSERT INTO scrape_log (timestamp, status, message, streams_collected, draws_collected, new_draws_added)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (datetime.now(), status, message, streams_saved, draws_total, draws_new))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✓ Save complete - Streams: {streams_saved}, Draws: {draws_new} new/{draws_total} total")

    except Exception as e:
        print(f"Error saving to database: {e}")
        # Log failed scrape
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scrape_log (timestamp, status, message, streams_collected, draws_collected, new_draws_added)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (datetime.now(), 'error', str(e), 0, 0, 0))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass
        raise


def main():
    """Main function"""
    print("=" * 60)
    print("AAIP Data Scraper - Consolidated Version")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)

    try:
        # Scrape all data
        data = scrape_aaip_data()

        # Save to database
        print("\nSaving to database...")
        save_to_database(data)

        print(f"\n{'=' * 60}")
        print("✓ Scraping completed successfully!")
        print(f"{'=' * 60}")

        return 0

    except Exception as e:
        print(f"\n✗ Scraping failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
