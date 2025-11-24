"""Quick script to create a session for the web dashboard"""
import requests
from datetime import datetime, timedelta
import sys

API_URL = "http://localhost:8000"

def main():
    print("Creating a session for the web dashboard...")
    
    # Wait a moment for API to be ready
    import time
    time.sleep(2)
    
    # Check API
    try:
        response = requests.get(f"{API_URL}/api/sessions", timeout=5)
        print("[OK] API is running")
    except Exception as e:
        print(f"[ERROR] Cannot connect to API: {e}")
        print("Make sure the API server is running!")
        sys.exit(1)
    
    # Create course
    print("\nCreating course...")
    course_data = {
        "course_code": "CS101",
        "course_name": "Introduction to Computer Science",
        "lecturer_name": "Dr. Smith"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/courses", json=course_data, timeout=5)
        if response.status_code == 200:
            course = response.json()
            course_id = course['id']
            print(f"[OK] Course created: {course['course_code']} - {course['course_name']} (ID: {course_id})")
        else:
            # Course might exist, use ID 1
            print(f"[INFO] Using existing course (ID: 1)")
            course_id = 1
    except Exception as e:
        print(f"[WARNING] Course creation issue: {e}, using course_id=1")
        course_id = 1
    
    # Create session
    print("\nCreating session...")
    now = datetime.now()
    session_data = {
        "course_id": course_id,
        "session_name": f"Lecture Session - {now.strftime('%Y-%m-%d %H:%M')}",
        "scheduled_start": now.isoformat(),
        "scheduled_end": (now + timedelta(hours=2)).isoformat(),
        "room_location": "Room 101"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/sessions", json=session_data, timeout=5)
        if response.status_code == 200:
            session = response.json()
            session_id = session['id']
            print(f"[OK] Session created: {session['session_name']} (ID: {session_id})")
            
            # Optionally start it
            print("\nStarting session...")
            start_response = requests.post(f"{API_URL}/api/sessions/{session_id}/start", timeout=5)
            if start_response.status_code == 200:
                print("[OK] Session started successfully!")
            else:
                print(f"[INFO] Session created but not started (you can start it from the dashboard)")
            
            print("\n" + "="*50)
            print("SUCCESS! Session is ready.")
            print(f"Session ID: {session_id}")
            print("Refresh your web dashboard to see the session!")
            print("="*50)
        else:
            print(f"[ERROR] Failed to create session: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to create session: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



