#!/usr/bin/env python3
"""
AAIP Data Collection Orchestrator
Runs all data collection scripts in the correct order
Designed to be run hourly via systemd timer or cron
"""

import subprocess
import sys
from datetime import datetime
import os
from pathlib import Path

# Change to scraper directory
SCRAPER_DIR = Path(__file__).parent
os.chdir(SCRAPER_DIR)

# Data collection scripts in order of execution
COLLECTORS = [
    {
        'name': 'AAIP Processing Info & Draw Records',
        'script': 'scraper.py',
        'description': 'Collects processing times, allocations, and draw history',
        'critical': True  # If this fails, stop execution
    },
    {
        'name': 'AAIP News Updates',
        'script': 'aaip_news_scraper.py',
        'description': 'Collects and translates news from /aaip-updates',
        'critical': False
    },
    {
        'name': 'Express Entry Comparison Data',
        'script': 'express_entry_collector.py',
        'description': 'Collects federal Express Entry draw data for comparison',
        'critical': False
    },
    {
        'name': 'Alberta Economy Indicators',
        'script': 'alberta_economy_collector.py',
        'description': 'Collects provincial economic indicators',
        'critical': False
    },
    {
        'name': 'Labor Market Data',
        'script': 'quarterly_labor_market_collector.py',
        'description': 'Collects employment and wage statistics',
        'critical': False
    },
    {
        'name': 'Job Bank Postings',
        'script': 'job_bank_scraper.py',
        'description': 'Collects job posting trends from Job Bank',
        'critical': False
    },
    {
        'name': 'Trend Analysis Engine',
        'script': 'trend_analysis_engine.py',
        'description': 'Analyzes historical patterns and generates insights',
        'critical': False
    }
]


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def run_collector(collector):
    """
    Run a single data collector script
    Returns: (success: bool, duration_seconds: float)
    """
    name = collector['name']
    script = collector['script']
    description = collector['description']
    
    print(f"\n📊 Running: {name}")
    print(f"   Script: {script}")
    print(f"   Description: {description}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    start_time = datetime.now()
    
    try:
        # Run the script with Python3
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS - {name} completed in {duration:.1f}s")
            return True, duration
        else:
            print(f"❌ FAILED - {name} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr}")
            return False, duration
            
    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"⏱️  TIMEOUT - {name} exceeded 5 minute timeout")
        return False, duration
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"💥 EXCEPTION - {name} raised exception: {e}")
        import traceback
        traceback.print_exc()
        return False, duration


def main():
    """Main orchestration function"""
    print_header(f"AAIP Data Collection Orchestrator - Started at {datetime.now()}")
    
    results = []
    total_start = datetime.now()
    
    for collector in COLLECTORS:
        success, duration = run_collector(collector)
        
        results.append({
            'name': collector['name'],
            'success': success,
            'duration': duration,
            'critical': collector['critical']
        })
        
        # If critical collector fails, stop
        if not success and collector['critical']:
            print_header(f"❌ CRITICAL FAILURE - Stopping execution")
            print(f"Critical collector '{collector['name']}' failed.")
            print("Subsequent collectors will not run.")
            break
    
    # Print summary
    total_duration = (datetime.now() - total_start).total_seconds()
    print_header("Collection Summary")
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"\nTotal Time: {total_duration:.1f}s")
    print(f"Collectors Run: {total_count}/{len(COLLECTORS)}")
    print(f"Success: {success_count}/{total_count}")
    print(f"Failed: {total_count - success_count}/{total_count}")
    
    print("\nDetailed Results:")
    print("-" * 80)
    for r in results:
        status = "✅ SUCCESS" if r['success'] else "❌ FAILED"
        critical = " (CRITICAL)" if r['critical'] else ""
        print(f"{status:12} | {r['duration']:6.1f}s | {r['name']}{critical}")
    
    # Check if any collectors didn't run
    not_run = len(COLLECTORS) - len(results)
    if not_run > 0:
        print(f"\n⚠️  {not_run} collector(s) did not run (stopped due to critical failure)")
    
    print_header(f"AAIP Data Collection Orchestrator - Completed at {datetime.now()}")
    
    # Exit with appropriate code
    if success_count == total_count:
        print("\n🎉 All collectors completed successfully!")
        sys.exit(0)
    elif success_count > 0:
        print(f"\n⚠️  Partial success: {success_count}/{total_count} collectors succeeded")
        sys.exit(1)
    else:
        print("\n💥 All collectors failed!")
        sys.exit(2)


if __name__ == "__main__":
    main()
