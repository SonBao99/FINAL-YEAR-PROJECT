#!/usr/bin/env python3
"""
Comprehensive test suite for the Face Recognition Attendance System
Runs all available tests and provides a summary report
"""
import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print('='*60)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Command took too long: {cmd}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to run command: {e}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60)
    
    dependencies = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'sqlalchemy': 'SQLAlchemy',
        'face_recognition': 'Face Recognition',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'requests': 'Requests'
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            missing.append(name)
    
    return len(missing) == 0, missing

def main():
    print("\n" + "="*60)
    print("FACE RECOGNITION ATTENDANCE SYSTEM - TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Test 1: Check project structure
    print("\n" + "="*60)
    print("TEST 1: PROJECT STRUCTURE")
    print("="*60)
    required_files = [
        ('attendance_tracker.py', 'Attendance Tracker module'),
        ('database.py', 'Database module'),
        ('models.py', 'Models module'),
        ('attendance_api.py', 'API server'),
        ('kiosk_app.py', 'Kiosk application'),
        ('attendance.db', 'Database file'),
        ('test_attendance.py', 'Unit tests'),
        ('check_database.py', 'Database checker'),
    ]
    
    structure_ok = True
    for filepath, desc in required_files:
        if not check_file_exists(filepath, desc):
            structure_ok = False
    
    results['Project Structure'] = structure_ok
    
    # Test 2: Check dependencies
    deps_ok, missing_deps = check_dependencies()
    results['Dependencies'] = deps_ok
    
    # Test 3: Run unit tests
    print("\n" + "="*60)
    print("TEST 3: UNIT TESTS")
    print("="*60)
    unit_tests_ok = run_command(
        "python3 -m unittest test_attendance.py -v",
        "AttendanceTracker Unit Tests"
    )
    results['Unit Tests'] = unit_tests_ok
    
    # Test 4: Database check
    print("\n" + "="*60)
    print("TEST 4: DATABASE STATE")
    print("="*60)
    db_check_ok = run_command(
        "python3 check_database.py",
        "Database Verification"
    )
    results['Database'] = db_check_ok
    
    # Test 5: API server test (if dependencies available)
    if deps_ok:
        print("\n" + "="*60)
        print("TEST 5: API SERVER STARTUP")
        print("="*60)
        api_test_ok = run_command(
            "python3 test_api_startup.py",
            "API Startup Test"
        )
        results['API Startup'] = api_test_ok
        
        # Test 6: Check if API is running
        print("\n" + "="*60)
        print("TEST 6: API SERVER STATUS")
        print("="*60)
        try:
            import requests
            try:
                response = requests.get("http://localhost:8000/api/students", timeout=2)
                if response.status_code == 200:
                    print("✓ API server is running and responding")
                    results['API Running'] = True
                else:
                    print(f"✗ API server returned status {response.status_code}")
                    results['API Running'] = False
            except requests.exceptions.ConnectionError:
                print("✗ API server is not running")
                print("  Start it with: python3 -m uvicorn attendance_api:app --reload --port 8000")
                results['API Running'] = False
        except ImportError:
            print("⚠ Cannot test API - requests module not available")
            results['API Running'] = None
    else:
        print("\n⚠ Skipping API tests - dependencies not installed")
        results['API Startup'] = None
        results['API Running'] = None
    
    # Test 7: Check sample images
    print("\n" + "="*60)
    print("TEST 7: SAMPLE IMAGES")
    print("="*60)
    images_dir = Path("images")
    if images_dir.exists():
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']:
            image_files.extend(images_dir.glob(ext))
        print(f"✓ Found {len(image_files)} sample images:")
        for img in image_files:
            print(f"  - {img}")
        results['Sample Images'] = len(image_files) > 0
    else:
        print("✗ Images directory not found")
        results['Sample Images'] = False
    
    # Test 8: Check student photos
    print("\n" + "="*60)
    print("TEST 8: ENROLLED STUDENT PHOTOS")
    print("="*60)
    student_photos_dir = Path("student_photos")
    if student_photos_dir.exists():
        photo_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            photo_files.extend(student_photos_dir.glob(ext))
        print(f"✓ Found {len(photo_files)} enrolled student photos:")
        for photo in photo_files[:5]:  # Show first 5
            print(f"  - {photo}")
        if len(photo_files) > 5:
            print(f"  ... and {len(photo_files) - 5} more")
        results['Student Photos'] = len(photo_files) > 0
    else:
        print("✗ Student photos directory not found")
        results['Student Photos'] = False
    
    # Final Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results.items():
        if result is True:
            print(f"✓ {test_name}: PASSED")
            passed += 1
        elif result is False:
            print(f"✗ {test_name}: FAILED")
            failed += 1
        else:
            print(f"⚠ {test_name}: SKIPPED")
            skipped += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed, {skipped} skipped")
    print("="*60)
    
    if missing_deps:
        print("\n⚠ MISSING DEPENDENCIES:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nTo install dependencies:")
        print("  python3 -m pip install -r requirements.txt")
        print("\nOr install core packages first:")
        print("  python3 install_dependencies.py")
    
    if not results.get('API Running', True):
        print("\n📝 TO START THE API SERVER:")
        print("  python3 -m uvicorn attendance_api:app --reload --port 8000")
        print("\n📝 TO TEST CHECK-IN FLOW:")
        print("  1. Start API server (command above)")
        print("  2. python3 test_checkin.py")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

