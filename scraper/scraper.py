#!/usr/bin/env python3
"""
AAIP Data Scraper
Scrapes Alberta Advantage Immigration Program processing information
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import sqlite3
import os
import sys

# Configuration
AAIP_URL = "https://www.alberta.ca/aaip-processing-information"
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/aaip_data.db')


def init_database():
    """Initialize SQLite database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aaip_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            status TEXT NOT NULL,
            message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


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
        data['timestamp'] = datetime.now().isoformat()
        
        print(f"Successfully scraped data: {data}")
        return data
        
    except Exception as e:
        print(f"Error scraping data: {e}")
        raise


def save_to_database(data):
    """Save scraped data to SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert data (ignore if duplicate timestamp within same hour)
        cursor.execute('''
            INSERT OR IGNORE INTO aaip_summary 
            (timestamp, nomination_allocation, nominations_issued, 
             nomination_spaces_remaining, applications_to_process, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
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
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), 'success', 'Data scraped successfully'))
        
        conn.commit()
        conn.close()
        
        print(f"Data saved to database successfully")
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        # Log failed scrape
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scrape_log (timestamp, status, message)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), 'error', str(e)))
        conn.commit()
        conn.close()
        raise


def main():
    """Main function"""
    print("=" * 50)
    print("AAIP Data Scraper")
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
