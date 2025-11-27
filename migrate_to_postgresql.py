"""
Script to migrate data from SQLite to PostgreSQL
Run this after Railway deployment to migrate existing data
"""
import sqlite3
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URLs
SQLITE_DB = "attendance.db"
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    print("❌ DATABASE_URL not set!")
    print("Set it in Railway environment variables or .env file")
    sys.exit(1)

if not POSTGRES_URL.startswith("postgresql"):
    print("❌ DATABASE_URL is not a PostgreSQL connection string")
    sys.exit(1)

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    print("=" * 50)
    print("SQLite to PostgreSQL Migration")
    print("=" * 50)
    
    # Connect to SQLite
    if not os.path.exists(SQLITE_DB):
        print(f"❌ SQLite database '{SQLITE_DB}' not found")
        sys.exit(1)
    
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    try:
        postgres_engine = create_engine(POSTGRES_URL)
        postgres_conn = postgres_engine.connect()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)
    
    # Tables to migrate
    tables = ['courses', 'lecturers', 'students', 'sessions', 'attendance_records']
    
    for table in tables:
        try:
            # Get data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"⏭️  {table}: No data to migrate")
                continue
            
            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]
            
            # Insert into PostgreSQL
            # Note: This assumes tables already exist (created by create_tables())
            for row in rows:
                placeholders = ', '.join([':' + col for col in columns])
                columns_str = ', '.join(columns)
                
                # Build insert statement
                insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                
                # Create dict for values
                values = dict(zip(columns, row))
                
                try:
                    postgres_conn.execute(text(insert_sql), values)
                except Exception as e:
                    print(f"⚠️  Error inserting row into {table}: {e}")
                    continue
            
            postgres_conn.commit()
            print(f"✅ {table}: Migrated {len(rows)} rows")
            
        except Exception as e:
            print(f"❌ Error migrating {table}: {e}")
            continue
    
    # Close connections
    sqlite_conn.close()
    postgres_conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Migration complete!")
    print("=" * 50)

if __name__ == "__main__":
    migrate_data()

