#!/usr/bin/env python3
"""
Job Bank Labor Market Data Scraper
Scrapes Alberta labor market outlook data from Job Bank Canada
"""

import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import sys
import re
from dotenv import load_dotenv

load_dotenv()

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'aaip_data')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Key occupations relevant to AAIP streams
OCCUPATION_MAPPING = {
    # Healthcare (Dedicated Health Care Pathways)
    'nurses': {
        'noc': '31301',
        'title': 'Registered Nurses and Registered Psychiatric Nurses',
        'stream': 'Dedicated Health Care Pathways'
    },
    'healthcare_assistants': {
        'noc': '33102',
        'title': 'Nurse Aides, Orderlies and Patient Service Associates',
        'stream': 'Dedicated Health Care Pathways'
    },
    
    # Tourism & Hospitality
    'food_service_supervisors': {
        'noc': '62020',
        'title': 'Food Service Supervisors',
        'stream': 'Tourism and Hospitality Stream'
    },
    'cooks': {
        'noc': '63200',
        'title': 'Cooks',
        'stream': 'Tourism and Hospitality Stream'
    },
    'food_service_workers': {
        'noc': '65201',
        'title': 'Food Counter Attendants, Kitchen Helpers',
        'stream': 'Tourism and Hospitality Stream'
    },
    
    # IT/Tech (Express Entry - Accelerated Tech)
    'software_engineers': {
        'noc': '21231',
        'title': 'Software Engineers and Designers',
        'stream': 'Express Entry - Accelerated Tech Pathway'
    },
    'computer_programmers': {
        'noc': '21232',
        'title': 'Software Developers and Programmers',
        'stream': 'Express Entry - Accelerated Tech Pathway'
    },
    
    # General (Alberta Opportunity Stream)
    'retail_supervisors': {
        'noc': '62010',
        'title': 'Retail Sales Supervisors',
        'stream': 'Alberta Opportunity Stream'
    },
    'transport_drivers': {
        'noc': '73300',
        'title': 'Transport Truck Drivers',
        'stream': 'Alberta Opportunity Stream'
    }
}


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


def scrape_job_bank_occupation(noc_code, occupation_title):
    """
    Scrape Job Bank for a specific occupation in Alberta
    Returns: dict with outlook data or None
    """
    try:
        # Job Bank URL structure for Alberta (area code 48)
        url = f"https://www.jobbank.gc.ca/marketreport/outlook-occupation/{noc_code}/48"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"  Fetching {occupation_title} (NOC {noc_code})...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"    ⚠️  HTTP {response.status_code} - Skipping")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {
            'noc_code': noc_code,
            'occupation_title': occupation_title,
            'outlook': None,
            'job_openings': None,
            'job_seekers': None,
            'median_wage': None,
            'outlook_description': None
        }
        
        # Try to extract outlook rating (Good, Fair, Limited)
        outlook_elem = soup.find('span', class_='outlook-icon')
        if outlook_elem:
            outlook_text = outlook_elem.get_text(strip=True)
            data['outlook'] = outlook_text
            
        # Try to extract employment outlook description
        outlook_desc = soup.find('div', class_='outlook-description')
        if outlook_desc:
            data['outlook_description'] = outlook_desc.get_text(strip=True)[:500]
        
        # Try to extract job openings and seekers
        stats_section = soup.find_all('dd', class_='stat-value')
        if len(stats_section) >= 2:
            try:
                data['job_openings'] = int(stats_section[0].get_text(strip=True).replace(',', ''))
                data['job_seekers'] = int(stats_section[1].get_text(strip=True).replace(',', ''))
            except:
                pass
        
        # Try to extract median wage
        wage_elem = soup.find('span', class_='wage-value')
        if wage_elem:
            wage_text = wage_elem.get_text(strip=True)
            # Extract number from "$XX.XX"
            match = re.search(r'\$?([\d,]+\.?\d*)', wage_text)
            if match:
                try:
                    data['median_wage'] = float(match.group(1).replace(',', ''))
                except:
                    pass
        
        print(f"    ✓ Outlook: {data['outlook']}, Openings: {data['job_openings']}")
        return data
        
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


def save_job_bank_data(data_list):
    """Save scraped job bank data to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_bank_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                noc_code VARCHAR(10) NOT NULL,
                occupation_title VARCHAR(255) NOT NULL,
                outlook VARCHAR(50),
                job_openings INTEGER,
                job_seekers INTEGER,
                median_wage DECIMAL(10,2),
                outlook_description TEXT,
                aaip_stream VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on timestamp
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_bank_timestamp 
            ON job_bank_data(timestamp DESC)
        """)
        
        current_time = datetime.now()
        saved_count = 0
        
        for data in data_list:
            if data:
                cursor.execute("""
                    INSERT INTO job_bank_data 
                    (timestamp, noc_code, occupation_title, outlook, 
                     job_openings, job_seekers, median_wage, outlook_description, aaip_stream)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    current_time,
                    data['noc_code'],
                    data['occupation_title'],
                    data['outlook'],
                    data['job_openings'],
                    data['job_seekers'],
                    data['median_wage'],
                    data['outlook_description'],
                    data['aaip_stream']
                ))
                saved_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✓ Saved {saved_count} occupation records to database")
        
    except Exception as e:
        print(f"✗ Error saving to database: {e}")
        raise


def main():
    """Main scraper function"""
    print("=" * 70)
    print("Job Bank Labor Market Data Scraper")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 70)
    print()
    
    scraped_data = []
    
    for key, occupation in OCCUPATION_MAPPING.items():
        data = scrape_job_bank_occupation(occupation['noc'], occupation['title'])
        if data:
            data['aaip_stream'] = occupation['stream']
            scraped_data.append(data)
    
    if scraped_data:
        save_job_bank_data(scraped_data)
        print(f"\n✓ Successfully scraped {len(scraped_data)} occupations")
    else:
        print("\n⚠️  No data scraped")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
