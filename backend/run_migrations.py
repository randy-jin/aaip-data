#!/usr/bin/env python3
"""
Run database migrations for success stories and other features
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return psycopg2.connect(
            dbname="aaip_tracker",
            user="aaip_user",
            password=os.getenv('DB_PASSWORD', 'aaip2024!secure'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432)
        )

def run_migration(filename):
    """Run a single migration file"""
    print(f"\n📄 Running migration: {filename}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, 'db/migrations', filename)
    if not os.path.exists(filepath):
        print(f"   ⚠️  File not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r') as f:
            sql = f.read()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"   ✅ Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("Database Migrations Runner")
    print("=" * 70)
    
    migrations = [
        '007_create_success_stories.sql'
    ]
    
    success_count = 0
    for migration in migrations:
        if run_migration(migration):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Completed {success_count}/{len(migrations)} migrations")
    print("=" * 70)

if __name__ == '__main__':
    main()
