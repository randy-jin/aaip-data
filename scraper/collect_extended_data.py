#!/usr/bin/env python3
"""
Extended Data Collectors Orchestrator
Runs additional data collectors with appropriate frequencies

Collection Schedule:
- Express Entry: Daily (draws happen every 2 weeks, but check daily)
- Alberta Economy: Daily (some indicators update daily)
- Labor Market: Daily (will check quarter internally)
- Job Bank: Daily (job postings change frequently)

Usage:
  python3 collect_extended_data.py [--collector NAME] [--verbose]
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
import argparse

# Set up paths
SCRIPT_DIR = Path(__file__).parent
os.chdir(SCRIPT_DIR)

# Collector configurations
COLLECTORS = {
    'express_entry': {
        'script': 'express_entry_collector.py',
        'name': 'Express Entry Comparison Data',
        'critical': False,
        'timeout': 300,  # 5 minutes
    },
    'alberta_economy': {
        'script': 'alberta_economy_collector.py',
        'name': 'Alberta Economic Indicators',
        'critical': False,
        'timeout': 300,
    },
    'labor_market': {
        'script': 'quarterly_labor_market_collector.py',
        'name': 'Labor Market Data',
        'critical': False,
        'timeout': 300,
    },
    'job_bank': {
        'script': 'job_bank_scraper.py',
        'name': 'Job Bank Postings',
        'critical': False,
        'timeout': 600,  # 10 minutes (more data to scrape)
    },
}


def print_header(text):
    """Print formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def run_collector(collector_key, verbose=False):
    """Run a single data collector"""
    config = COLLECTORS[collector_key]
    script_path = SCRIPT_DIR / config['script']
    
    if not script_path.exists():
        print(f"❌ ERROR: {config['script']} not found at {script_path}")
        return False
    
    print(f"▶️  Running: {config['name']}")
    print(f"   Script: {config['script']}")
    print(f"   Timeout: {config['timeout']}s")
    
    start_time = datetime.now()
    
    try:
        # Run the collector
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=config['timeout']
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.returncode == 0:
            print(f"✅ SUCCESS ({elapsed:.1f}s)")
            if verbose and result.stdout:
                print(f"   Output: {result.stdout[:200]}")
            return True
        else:
            print(f"❌ FAILED (exit code: {result.returncode}, {elapsed:.1f}s)")
            if result.stderr:
                print(f"   Error: {result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"⏱️  TIMEOUT after {elapsed:.1f}s")
        return False
        
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"❌ EXCEPTION ({elapsed:.1f}s): {str(e)}")
        return False


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Run extended data collectors')
    parser.add_argument('--collector', '-c', choices=list(COLLECTORS.keys()),
                       help='Run only specific collector')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output')
    args = parser.parse_args()
    
    print_header("AAIP Extended Data Collectors")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {SCRIPT_DIR}")
    
    # Determine which collectors to run
    if args.collector:
        collectors_to_run = {args.collector: COLLECTORS[args.collector]}
        print(f"\n🎯 Running single collector: {args.collector}")
    else:
        collectors_to_run = COLLECTORS
        print(f"\n🎯 Running all {len(COLLECTORS)} collectors")
    
    # Run collectors
    results = {}
    for key, config in collectors_to_run.items():
        print(f"\n{'─' * 70}")
        success = run_collector(key, verbose=args.verbose)
        results[key] = success
    
    # Print summary
    print_header("Summary")
    
    total = len(results)
    succeeded = sum(1 for success in results.values() if success)
    failed = total - succeeded
    
    print(f"Total collectors: {total}")
    print(f"✅ Succeeded: {succeeded}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print(f"\n❌ Failed collectors:")
        for key, success in results.items():
            if not success:
                print(f"   - {COLLECTORS[key]['name']} ({COLLECTORS[key]['script']})")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    # Note: Non-critical collectors, so we exit 0 even if some failed
    # This allows systemd to consider the service successful
    sys.exit(0)


if __name__ == '__main__':
    main()
