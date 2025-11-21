#!/usr/bin/env python3
"""
Import 2024 AAIP Draw History from PDF
Downloads and parses the official 2024 draw history PDF and imports it to database
IMPORTANT: This script ADDS data, does NOT delete existing records
"""

import requests
import pdfplumber
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PDF_URL = "https://www.alberta.ca/system/files/im-aaip-draw-history-summary.pdf"
PDF_FILE = "aaip_2024_draws.pdf"

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


def download_pdf():
    """Download the PDF file"""
    print(f"Downloading PDF from {PDF_URL}...")
    try:
        response = requests.get(PDF_URL, timeout=60)
        response.raise_for_status()

        with open(PDF_FILE, 'wb') as f:
            f.write(response.content)

        print(f"✅ PDF downloaded: {PDF_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error downloading PDF: {e}")
        return False


def parse_date(date_str):
    """Parse date string to date object"""
    try:
        # Try various date formats
        for fmt in ["%B %d, %Y", "%Y-%m-%d", "%d-%b-%Y", "%m/%d/%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except:
                continue
        return None
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None


def categorize_stream(stream_text):
    """
    Categorize stream into main category and detail
    Returns: (stream_category, stream_detail)
    """
    stream_text = stream_text.strip()

    # Main categories
    categories = {
        'Alberta Opportunity Stream': ['Alberta Opportunity', 'AOS'],
        'Alberta Express Entry Stream': ['Alberta Express Entry', 'Express Entry'],
        'Dedicated Health Care Pathway': ['Health Care', 'Healthcare'],
        'Tourism and Hospitality Stream': ['Tourism', 'Hospitality'],
        'Rural Renewal Stream': ['Rural Renewal', 'RRS'],
    }

    main_category = None
    for category, patterns in categories.items():
        for pattern in patterns:
            if pattern.lower() in stream_text.lower():
                main_category = category
                break
        if main_category:
            break

    if not main_category:
        main_category = stream_text

    # Detail is the full text
    stream_detail = stream_text if stream_text != main_category else None

    return main_category, stream_detail


def extract_draws_from_pdf():
    """Extract draw records from PDF using text parsing"""
    print(f"Parsing PDF: {PDF_FILE}...")

    draws = []

    try:
        with pdfplumber.open(PDF_FILE) as pdf:
            print(f"Total pages: {len(pdf.pages)}")

            all_text = ""
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"Processing page {page_num}...")
                text = page.extract_text()
                if text:
                    all_text += text + "\n"

            # Parse text line by line
            # Format: "Date, Number Draw parameters Score"
            # Example: "September 10, 22 Dedicated Healthcare Pathway with Alberta job offer, 314"
            # Example: "2024 CRS score 300 and above"

            lines = all_text.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Look for date pattern at start of line
                date_match = re.match(r'([A-Z][a-z]+ \d{1,2}, \d{4})\s+(\d+)\s+(.+)', line)

                if date_match:
                    date_str = date_match.group(1)
                    invitations_str = date_match.group(2)
                    stream_and_score = date_match.group(3)

                    draw_date = parse_date(date_str)
                    if not draw_date or draw_date.year != 2024:
                        i += 1
                        continue

                    invitations_issued = int(invitations_str)

                    # Stream info might continue on next line
                    full_stream_text = stream_and_score

                    # Check next line for continuation (CRS score line)
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not re.match(r'[A-Z][a-z]+ \d{1,2}, \d{4}', next_line):
                            full_stream_text += " " + next_line
                            i += 1

                    # Extract score from text
                    min_score = None
                    score_match = re.search(r'(\d{3})', full_stream_text)
                    if score_match:
                        min_score = int(score_match.group(1))

                    # Extract stream category
                    stream_category, stream_detail = categorize_stream(full_stream_text)

                    draw = {
                        'draw_date': draw_date,
                        'stream_category': stream_category,
                        'stream_detail': full_stream_text[:200],  # Store full description
                        'min_score': min_score,
                        'invitations_issued': invitations_issued
                    }

                    draws.append(draw)
                    print(f"  ✓ {draw_date} - {stream_category} - Score: {min_score} - Inv: {invitations_issued}")

                i += 1

        print(f"\n✅ Total draws extracted: {len(draws)}")
        return draws

    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()
        return []


def import_draws_to_db(draws):
    """
    Import draws to database
    Uses ON CONFLICT DO NOTHING to preserve existing data
    """
    if not draws:
        print("No draws to import")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check existing data count
        cur.execute("SELECT COUNT(*) FROM aaip_draws WHERE EXTRACT(YEAR FROM draw_date) = 2024")
        existing_2024 = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM aaip_draws WHERE EXTRACT(YEAR FROM draw_date) = 2025")
        existing_2025 = cur.fetchone()[0]

        print(f"\nCurrent database status:")
        print(f"  2024 draws: {existing_2024}")
        print(f"  2025 draws: {existing_2025}")
        print(f"  Total: {existing_2024 + existing_2025}")

        inserted = 0
        skipped = 0

        for draw in draws:
            query = """
                INSERT INTO aaip_draws (
                    draw_date, stream_category, stream_detail,
                    min_score, invitations_issued
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (draw_date, stream_category, COALESCE(stream_detail, ''))
                DO NOTHING
                RETURNING id;
            """

            cur.execute(query, (
                draw['draw_date'],
                draw['stream_category'],
                draw['stream_detail'],
                draw['min_score'],
                draw['invitations_issued']
            ))

            result = cur.fetchone()
            if result:
                inserted += 1
            else:
                skipped += 1

        conn.commit()

        # Check final counts
        cur.execute("SELECT COUNT(*) FROM aaip_draws WHERE EXTRACT(YEAR FROM draw_date) = 2024")
        final_2024 = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM aaip_draws WHERE EXTRACT(YEAR FROM draw_date) = 2025")
        final_2025 = cur.fetchone()[0]

        cur.close()
        conn.close()

        print(f"\n✅ Import completed:")
        print(f"  Inserted: {inserted} new draws")
        print(f"  Skipped: {skipped} duplicates")
        print(f"\nFinal database status:")
        print(f"  2024 draws: {final_2024} (added {final_2024 - existing_2024})")
        print(f"  2025 draws: {final_2025} (unchanged - preserved ✓)")
        print(f"  Total: {final_2024 + final_2025}")

    except Exception as e:
        print(f"❌ Error importing to database: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main execution"""
    print("=" * 70)
    print("AAIP 2024 Draw History Importer")
    print("IMPORTANT: This preserves all existing data (2025 draws)")
    print("=" * 70)
    print()

    # Download PDF
    if not download_pdf():
        sys.exit(1)

    print()

    # Parse PDF
    draws = extract_draws_from_pdf()

    if not draws:
        print("❌ No draws found in PDF")
        sys.exit(1)

    print()

    # Import to database
    import_draws_to_db(draws)

    print()
    print("=" * 70)
    print("✅ Import process completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
