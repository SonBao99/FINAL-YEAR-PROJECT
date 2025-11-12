"""
Quick session creation and activation test
"""
import requests
import os
from datetime import datetime, timedelta

def check_api_connection(api_url="http://localhost:8000"):
    """Check if API is accessible"""
    try:
        response = requests.get(f"{api_url}/api/students", timeout=3)
        return response.status_code == 200
    except:
        return False

def create_course(api_url="http://localhost:8000"):
    """Create a test course"""
    course_data = {
        "course_code": "CS101",
        "course_name": "Test Course",
        "lecturer_name": "Test Lecturer"
    }
    try:
        response = requests.post(f"{api_url}/api/courses", json=course_data)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Course created: {result['course_code']} - {result['course_name']} (ID: {result['id']})")
            return result['id']
        else:
            # Course might already exist, try to get existing courses
            print(f"[INFO] Course creation returned: {response.status_code}")
            # For now, assume course ID 1 exists or create manually
            return 1
    except Exception as e:
        print(f"[ERROR] Failed to create course: {e}")
        return 1  # Default to course ID 1

def create_session(course_id, api_url="http://localhost:8000"):
    """Create a test session"""
    now = datetime.now()
    session_data = {
        "course_id": course_id,
        "session_name": f"Test Session - {now.strftime('%Y-%m-%d %H:%M')}",
        "scheduled_start": now.isoformat(),
        "scheduled_end": (now + timedelta(hours=2)).isoformat(),
        "room_location": "Test Room"
    }
    try:
        response = requests.post(f"{api_url}/api/sessions", json=session_data)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Session created: {result['session_name']} (ID: {result['id']})")
            return result['id']
        else:
            print(f"[ERROR] Session creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] API request failed: {e}")
        return None

def start_session(session_id, api_url="http://localhost:8000"):
    """Start a session"""
    try:
        response = requests.post(f"{api_url}/api/sessions/{session_id}/start")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Session started successfully!")
            print(f"    Message: {result.get('message', 'Session is now active')}")
            return True
        else:
            print(f"[ERROR] Failed to start session: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] API request failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Quick Session Creation and Activation Test")
    print("=" * 50)
    
    api_url = "http://localhost:8000"
    
    # Check API connection
    if not check_api_connection(api_url):
        print(f"[ERROR] Cannot connect to API at {api_url}")
        print("  Make sure API server is running!")
        return
    print(f"[OK] API connection successful\n")
    
    # Create course
    print("Step 1: Creating/Getting course...")
    course_id = create_course(api_url)
    if not course_id:
        print("[ERROR] Failed to get course ID")
        return
    
    # Create session
    print("\nStep 2: Creating session...")
    session_id = create_session(course_id, api_url)
    if not session_id:
        print("[ERROR] Failed to create session")
        return
    
    # Start session
    print("\nStep 3: Starting session...")
    if start_session(session_id, api_url):
        print("\n" + "=" * 50)
        print("[SUCCESS] Session is now active!")
        print(f"  Session ID: {session_id}")
        print(f"  Course ID: {course_id}")
        print("\nNext steps:")
        print(f"  Test kiosk: python kiosk_app.py --api {api_url} --session {session_id} --verbose")
        print("=" * 50)
    else:
        print("\n[WARNING] Session created but not started")
        print(f"  Session ID: {session_id}")
        print(f"  You can start it manually later")

if __name__ == "__main__":
    main()

