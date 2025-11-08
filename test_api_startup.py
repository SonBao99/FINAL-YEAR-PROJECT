"""
Quick test script to verify API can start and database is initialized
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import attendance_api
        print("[OK] attendance_api imported successfully")
        
        from database import create_tables, get_db
        print("[OK] database module imported successfully")
        
        from models import Student, Course, Session, AttendanceRecord
        print("[OK] models imported successfully")
        
        import face_recognition
        print("[OK] face_recognition imported successfully")
        
        import cv2
        print("[OK] opencv imported successfully")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_database():
    """Test database connection and table creation"""
    print("\nTesting database...")
    try:
        from database import create_tables, engine
        create_tables()
        print("[OK] Database tables created successfully")
        
        # Test connection
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"[OK] Found {len(tables)} tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("API Startup Test")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_database()
    
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] All tests passed! API should start successfully.")
        print("\nNext steps:")
        print("1. Start API: python -m uvicorn attendance_api:app --reload --port 8000")
        print("2. Test enrollment: python enroll.py")
        print("3. Create session: python start_session.py")
        print("4. Start kiosk: python kiosk_app.py --api http://localhost:8000 --verbose")
    else:
        print("[FAILED] Some tests failed. Please fix the errors above.")
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

