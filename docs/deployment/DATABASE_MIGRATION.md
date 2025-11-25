# Database Migration Guide: SQLite → PostgreSQL

## 🎯 Goal
Migrate from SQLite (development) to PostgreSQL (production-ready database)

---

## ✅ Why PostgreSQL?

- ✅ **Better for production** - Handles concurrent connections
- ✅ **Scalable** - Can handle large datasets
- ✅ **ACID compliant** - Better data integrity
- ✅ **Full-featured** - Advanced features SQLite doesn't have
- ✅ **Cloud-ready** - Easy to deploy on cloud platforms

---

## 📋 Prerequisites

1. **PostgreSQL installed** (or use cloud database)
2. **Python packages** already in requirements.txt:
   - `psycopg2-binary` ✅ (already included)
   - `sqlalchemy` ✅ (already included)

---

## 🚀 Step 1: Set Up PostgreSQL

### **Option A: Local PostgreSQL**

**Install PostgreSQL:**
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

**Create Database:**
```bash
# Login to PostgreSQL
psql postgres

# Create database
CREATE DATABASE attendance_db;

# Create user (optional)
CREATE USER attendance_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;

# Exit
\q
```

### **Option B: Cloud PostgreSQL (Recommended)**

**Railway:**
1. Go to Railway.app
2. New → Database → PostgreSQL
3. Copy connection string

**Render:**
1. Go to Render.com
2. New → PostgreSQL
3. Copy connection string

**Supabase (Free tier):**
1. Go to supabase.com
2. Create project
3. Get connection string from Settings → Database

---

## 🔧 Step 2: Update database.py

Your `database.py` already supports PostgreSQL! Just need to set the environment variable.

**Current code (already good):**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
```

**PostgreSQL connection string format:**
```
postgresql://username:password@host:port/database
```

**Example:**
```
postgresql://attendance_user:password123@localhost:5432/attendance_db
```

---

## 📝 Step 3: Set Environment Variable

### **Local Development:**

**macOS/Linux:**
```bash
export DATABASE_URL="postgresql://attendance_user:password123@localhost:5432/attendance_db"
```

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL="postgresql://attendance_user:password123@localhost:5432/attendance_db"
```

**Windows (CMD):**
```cmd
set DATABASE_URL=postgresql://attendance_user:password123@localhost:5432/attendance_db
```

### **Using .env file (Recommended):**

Create `.env` file:
```env
DATABASE_URL=postgresql://attendance_user:password123@localhost:5432/attendance_db
```

**Install python-dotenv:**
```bash
pip install python-dotenv
```

**Update database.py:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

# Create engine with proper connection args
if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # SQLite (for local dev)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 🔄 Step 4: Migrate Data (If You Have Existing Data)

### **Create Migration Script**

Create `migrate_to_postgresql.py`:

```python
#!/usr/bin/env python3
"""
Migrate data from SQLite to PostgreSQL
"""
import sqlite3
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite connection
sqlite_conn = sqlite3.connect('attendance.db')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL connection
postgres_url = os.getenv("DATABASE_URL")
if not postgres_url:
    print("Error: DATABASE_URL not set")
    exit(1)

# Parse PostgreSQL URL
from urllib.parse import urlparse
parsed = urlparse(postgres_url)

pg_conn = psycopg2.connect(
    host=parsed.hostname,
    port=parsed.port or 5432,
    database=parsed.path[1:],  # Remove leading /
    user=parsed.username,
    password=parsed.password
)
pg_cursor = pg_conn.cursor()

print("Starting migration...")

# Migrate Students
print("Migrating students...")
sqlite_cursor.execute("SELECT * FROM students")
students = sqlite_cursor.fetchall()

for student in students:
    pg_cursor.execute("""
        INSERT INTO students (id, student_id, name, email, face_encoding, photo_path, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, student)

# Migrate Courses
print("Migrating courses...")
sqlite_cursor.execute("SELECT * FROM courses")
courses = sqlite_cursor.fetchall()

for course in courses:
    pg_cursor.execute("""
        INSERT INTO courses (id, course_code, course_name, lecturer_name, description, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, course)

# Migrate Sessions
print("Migrating sessions...")
sqlite_cursor.execute("SELECT * FROM sessions")
sessions = sqlite_cursor.fetchall()

for session in sessions:
    pg_cursor.execute("""
        INSERT INTO sessions (id, course_id, session_name, scheduled_start, scheduled_end, 
                             actual_start, actual_end, room_location, kiosk_device_id, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, session)

# Migrate Attendance Records
print("Migrating attendance records...")
sqlite_cursor.execute("SELECT * FROM attendance_records")
records = sqlite_cursor.fetchall()

for record in records:
    pg_cursor.execute("""
        INSERT INTO attendance_records (id, student_id, session_id, check_in_time, confidence_score,
                                       face_photo_path, status, notes, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, record)

# Commit changes
pg_conn.commit()

print("Migration complete!")

# Close connections
sqlite_conn.close()
pg_conn.close()
```

**Run migration:**
```bash
python3 migrate_to_postgresql.py
```

---

## 🧪 Step 5: Test PostgreSQL Connection

### **Test Script**

Create `test_postgresql.py`:

```python
#!/usr/bin/env python3
"""Test PostgreSQL connection"""
import os
from dotenv import load_dotenv
from database import engine, create_tables
from sqlalchemy import text

load_dotenv()

print("Testing PostgreSQL connection...")

try:
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Connected to PostgreSQL!")
        print(f"Version: {version}")
    
    # Create tables
    print("\nCreating tables...")
    create_tables()
    print("✅ Tables created!")
    
    # Test query
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM students"))
        count = result.fetchone()[0]
        print(f"✅ Students table accessible! Count: {count}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

**Run test:**
```bash
python3 test_postgresql.py
```

---

## 🚀 Step 6: Update for Production

### **Update database.py (Final Version)**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

# Create engine with proper settings
if DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres"):
    # PostgreSQL settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Connection pool size
        max_overflow=20  # Max overflow connections
    )
else:
    # SQLite (for local dev)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 📝 Step 7: Update .gitignore

Add to `.gitignore`:
```
.env
*.db
*.sqlite
__pycache__/
*.pyc
```

**Never commit:**
- `.env` file (contains passwords)
- Database files
- Connection strings

---

## 🔍 Step 8: Verify Migration

### **Check Tables:**
```python
from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables:", tables)
```

### **Check Data:**
```python
from database import SessionLocal
from models import Student, Course, Session, AttendanceRecord

db = SessionLocal()

# Count records
students_count = db.query(Student).count()
courses_count = db.query(Course).count()
sessions_count = db.query(Session).count()
records_count = db.query(AttendanceRecord).count()

print(f"Students: {students_count}")
print(f"Courses: {courses_count}")
print(f"Sessions: {sessions_count}")
print(f"Attendance Records: {records_count}")

db.close()
```

---

## 🎯 Quick Migration Checklist

- [ ] PostgreSQL installed/configured
- [ ] Database created
- [ ] Environment variable `DATABASE_URL` set
- [ ] `python-dotenv` installed
- [ ] `database.py` updated
- [ ] Tables created (run `create_tables()`)
- [ ] Data migrated (if existing data)
- [ ] Tested connection
- [ ] Tested all endpoints
- [ ] `.env` added to `.gitignore`

---

## 🚨 Common Issues

### **Issue: "psycopg2 not found"**
**Solution:**
```bash
pip install psycopg2-binary
```

### **Issue: "Connection refused"**
**Solution:** 
- Check PostgreSQL is running: `pg_isready`
- Check connection string format
- Verify firewall settings

### **Issue: "Authentication failed"**
**Solution:**
- Check username/password
- Verify user has permissions
- Check `pg_hba.conf` settings

### **Issue: "Database does not exist"**
**Solution:**
- Create database: `CREATE DATABASE attendance_db;`
- Check connection string database name

---

## ✅ You're Done!

Your system now uses PostgreSQL and is ready for production deployment! 🎉

**Next:** Deploy to cloud platform (see DEPLOYMENT_GUIDE.md)

