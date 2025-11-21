#!/usr/bin/env python3
"""
AAIP News Scraper
Collects news updates from https://www.alberta.ca/aaip-updates
and translates them to Simplified Chinese
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
from deep_translator import GoogleTranslator

# Load environment variables
load_dotenv()

# Configuration
AAIP_NEWS_URL = "https://www.alberta.ca/aaip-updates"
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


def translate_to_chinese(text):
    """
    Translate English text to Simplified Chinese using Google Translate
    Handles long text by splitting if necessary (Google Translate has a 5000 char limit)
    """
    if not text or len(text.strip()) == 0:
        return ""

    try:
        translator = GoogleTranslator(source='en', target='zh-CN')

        # If text is longer than 4500 chars, split into chunks
        if len(text) > 4500:
            chunks = []
            sentences = text.split('. ')
            current_chunk = ""

            for sentence in sentences:
                if len(current_chunk) + len(sentence) < 4500:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "

            if current_chunk:
                chunks.append(current_chunk.strip())

            # Translate each chunk
            translated_chunks = []
            for chunk in chunks:
                translated = translator.translate(chunk)
                translated_chunks.append(translated)

            return " ".join(translated_chunks)
        else:
            return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original if translation fails


def parse_date_from_heading(heading_text):
    """
    Extract date from heading like 'November 18, 2025: New streams open for AAIP applications'
    Returns: (date_object, title_without_date)
    """
    # Pattern: "Month Day, Year: Title"
    pattern = r'([A-Z][a-z]+\s+\d+,\s+\d{4}):\s*(.*)'
    match = re.match(pattern, heading_text)

    if match:
        date_str = match.group(1)
        title = match.group(2).strip()

        try:
            date_obj = datetime.strptime(date_str, "%B %d, %Y").date()
            return date_obj, title
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            return None, heading_text

    return None, heading_text


def scrape_aaip_news():
    """
    Scrape AAIP news from the updates page
    Returns list of news articles: [{date, title_en, content_en}, ...]
    """
    try:
        print(f"Fetching news from {AAIP_NEWS_URL}...")
        response = requests.get(AAIP_NEWS_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all h3 headings with class "goa-title" (news titles)
        headings = soup.find_all('h3', class_='goa-title')

        news_articles = []

        for heading in headings:
            heading_text = heading.get_text(strip=True)

            # Parse date and title from heading
            date, title = parse_date_from_heading(heading_text)

            if not date:
                print(f"Skipping heading without date: {heading_text}")
                continue

            # Extract content - look for next div with class "goa-text"
            content_div = heading.find_next_sibling('div', class_='goa-text')
            content_parts = []

            if content_div:
                # Get all paragraphs from this div
                paragraphs = content_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text:
                        content_parts.append(text)

                # Also get list items
                lists = content_div.find_all(['ul', 'ol'])
                for ul in lists:
                    list_items = ul.find_all('li')
                    for li in list_items:
                        text = li.get_text(strip=True)
                        if text:
                            content_parts.append(f"• {text}")

            content = "\n\n".join(content_parts)

            if content:
                article = {
                    'date': date,
                    'title_en': title,
                    'content_en': content
                }
                news_articles.append(article)
                print(f"Found article: {date} - {title[:50]}...")

        print(f"Total articles found: {len(news_articles)}")
        return news_articles

    except Exception as e:
        print(f"Error scraping news: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_news_to_database(news_articles):
    """
    Save news articles to database with translations
    Uses UPSERT to avoid duplicates
    """
    if not news_articles:
        print("No news articles to save")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        saved_count = 0
        updated_count = 0

        for article in news_articles:
            # Translate to Chinese
            print(f"Translating: {article['title_en'][:50]}...")
            title_zh = translate_to_chinese(article['title_en'])
            content_zh = translate_to_chinese(article['content_en'])

            # UPSERT: Insert or update if exists
            query = """
                INSERT INTO aaip_news (
                    published_date, title_en, content_en, title_zh, content_zh,
                    source_url, scraped_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (published_date, title_en)
                DO UPDATE SET
                    content_en = EXCLUDED.content_en,
                    content_zh = EXCLUDED.content_zh,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING (xmax = 0) AS inserted;
            """

            cur.execute(query, (
                article['date'],
                article['title_en'],
                article['content_en'],
                title_zh,
                content_zh,
                AAIP_NEWS_URL
            ))

            result = cur.fetchone()
            if result and result[0]:  # inserted (not updated)
                saved_count += 1
            else:
                updated_count += 1

        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Successfully saved {saved_count} new articles, updated {updated_count} articles")

    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        import traceback
        traceback.print_exc()


def log_scrape_activity(status, message):
    """Log scraping activity to scrape_log table"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Simple log - just print, don't save to DB for now
        # (scrape_log table structure may vary)
        print(f"Log: {status} - {message}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error logging scrape activity: {e}")


def main():
    """Main execution function"""
    print("=" * 70)
    print("AAIP News Scraper - Starting...")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 70)

    try:
        # Scrape news articles
        news_articles = scrape_aaip_news()

        if not news_articles:
            log_scrape_activity('warning', 'No news articles found')
            print("⚠️  No news articles found. Exiting.")
            return

        # Save to database (with translation)
        save_news_to_database(news_articles)

        # Log success
        log_scrape_activity('success', f'Scraped {len(news_articles)} articles')

        print("=" * 70)
        print("✅ AAIP News Scraper - Completed Successfully")
        print("=" * 70)

    except Exception as e:
        error_msg = f"Fatal error: {str(e)}"
        print(f"❌ {error_msg}")
        log_scrape_activity('error', error_msg)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
