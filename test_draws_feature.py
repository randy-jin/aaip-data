#!/usr/bin/env python3
"""
Test script for AAIP Draw Records Feature
Tests database, scraper, and API functionality
"""

import sys
import requests
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://aaip.randy.it.com/api')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'aaip_data')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def test_database():
    """Test database schema and data"""
    print("\n" + "="*60)
    print("Testing Database")
    print("="*60)
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Test 1: Check if aaip_draws table exists
        print("\n[1/5] Checking if aaip_draws table exists...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'aaip_draws'
            );
        """)
        exists = cursor.fetchone()[0]
        if exists:
            print_success("Table 'aaip_draws' exists")
        else:
            print_error("Table 'aaip_draws' not found")
            return False
        
        # Test 2: Check unique constraint
        print("\n[2/5] Checking unique constraint...")
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'aaip_draws' 
            AND constraint_type = 'UNIQUE';
        """)
        constraints = cursor.fetchall()
        if constraints:
            print_success(f"Unique constraint found: {constraints[0][0]}")
        else:
            print_warning("No unique constraint found")
        
        # Test 3: Check indexes
        print("\n[3/5] Checking indexes...")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'aaip_draws';
        """)
        indexes = cursor.fetchall()
        print_info(f"Found {len(indexes)} indexes")
        for idx in indexes:
            print(f"  - {idx[0]}")
        
        # Test 4: Count records
        print("\n[4/5] Counting draw records...")
        cursor.execute("SELECT COUNT(*) FROM aaip_draws;")
        count = cursor.fetchone()[0]
        print_info(f"Total draw records: {count}")
        
        if count == 0:
            print_warning("No draw records found. Run scraper to collect data.")
        else:
            print_success(f"Found {count} draw records")
        
        # Test 5: Check data quality
        print("\n[5/5] Checking data quality...")
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT stream_category) as categories,
                COUNT(DISTINCT stream_detail) as details,
                MIN(draw_date) as earliest,
                MAX(draw_date) as latest,
                AVG(min_score) as avg_score,
                SUM(invitations_issued) as total_invitations
            FROM aaip_draws;
        """)
        stats = cursor.fetchone()
        
        print_info(f"Categories: {stats[0]}")
        print_info(f"Pathways/Details: {stats[1]}")
        print_info(f"Date range: {stats[2]} to {stats[3]}")
        print_info(f"Avg min score: {stats[4]:.1f if stats[4] else 'N/A'}")
        print_info(f"Total invitations: {stats[5] if stats[5] else 0}")
        
        cursor.close()
        conn.close()
        
        print_success("Database tests passed")
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False

def test_api():
    """Test API endpoints"""
    print("\n" + "="*60)
    print("Testing API Endpoints")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Stats endpoint
    print("\n[1/5] Testing /api/stats...")
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Stats endpoint working. Total draws: {data.get('total_draws', 0)}")
            tests_passed += 1
        else:
            print_error(f"Stats endpoint returned {response.status_code}")
    except Exception as e:
        print_error(f"Stats endpoint failed: {e}")
    
    # Test 2: Draws endpoint
    print("\n[2/5] Testing /api/draws...")
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/draws?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Draws endpoint working. Returned {len(data)} records")
            if len(data) > 0:
                print_info(f"Sample: {data[0].get('stream_category')} - {data[0].get('draw_date')}")
            tests_passed += 1
        else:
            print_error(f"Draws endpoint returned {response.status_code}")
    except Exception as e:
        print_error(f"Draws endpoint failed: {e}")
    
    # Test 3: Streams endpoint
    print("\n[3/5] Testing /api/draws/streams...")
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/draws/streams", timeout=10)
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            streams = data.get('streams', [])
            print_success(f"Streams endpoint working. {len(categories)} categories, {len(streams)} streams")
            if categories:
                print_info(f"Sample category: {categories[0]}")
            tests_passed += 1
        else:
            print_error(f"Streams endpoint returned {response.status_code}")
    except Exception as e:
        print_error(f"Streams endpoint failed: {e}")
    
    # Test 4: Trends endpoint
    print("\n[4/5] Testing /api/draws/trends...")
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/draws/trends?year=2025&limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Trends endpoint working. Returned {len(data)} records")
            tests_passed += 1
        else:
            print_error(f"Trends endpoint returned {response.status_code}")
    except Exception as e:
        print_error(f"Trends endpoint failed: {e}")
    
    # Test 5: Draw stats endpoint
    print("\n[5/5] Testing /api/draws/stats...")
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/draws/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Draw stats endpoint working. Returned {len(data)} stream stats")
            if len(data) > 0:
                print_info(f"Sample: {data[0].get('stream_category')} - {data[0].get('total_draws')} draws")
            tests_passed += 1
        else:
            print_error(f"Draw stats endpoint returned {response.status_code}")
    except Exception as e:
        print_error(f"Draw stats endpoint failed: {e}")
    
    print(f"\nAPI Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total

def test_scraper():
    """Test scraper functionality"""
    print("\n" + "="*60)
    print("Testing Scraper")
    print("="*60)
    
    print("\n[1/1] Checking scraper status...")
    
    # Check if scraper file exists
    scraper_path = "scraper/scraper_draws.py"
    if os.path.exists(scraper_path):
        print_success(f"Scraper file exists: {scraper_path}")
    else:
        print_error(f"Scraper file not found: {scraper_path}")
        return False
    
    # Check scraper service status (if on Linux with systemd)
    if os.name != 'nt':  # Not Windows
        import subprocess
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'aaip-scraper.timer'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_success("Scraper timer is active")
            else:
                print_warning("Scraper timer is not active. Enable with: sudo systemctl start aaip-scraper.timer")
        except:
            print_info("Could not check scraper service status (systemctl not available)")
    
    print_info("To test scraper manually, run: python3 scraper/scraper_draws.py")
    return True

def main():
    print(f"""
{'='*60}
AAIP Draw Records Feature - Test Suite
{'='*60}
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    results = {
        'database': False,
        'api': False,
        'scraper': False
    }
    
    # Run tests
    results['database'] = test_database()
    results['api'] = test_api()
    results['scraper'] = test_scraper()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = print_success if passed else print_error
        status(f"{test_name.capitalize()} tests: {'PASSED' if passed else 'FAILED'}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print_success("All tests passed! System is working correctly.")
        print("\nNext steps:")
        print("1. Visit https://aaip.randy.it.com")
        print("2. Click 'Draw History' tab")
        print("3. Explore the visualizations!")
    else:
        print_error("Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        if not results['database']:
            print("- Run: sudo -u postgres psql aaip_data < setup_db_draws.sql")
        if not results['api']:
            print("- Check backend status: sudo systemctl status aaip-backend-test")
            print("- Check logs: sudo journalctl -u aaip-backend-test -n 50")
        if not results['scraper']:
            print("- Run scraper manually: python3 scraper/scraper_draws.py")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
