import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"

def create_sample_course():
    """Create a sample course"""
    course_data = {
        "course_code": "CS101",
        "course_name": "Introduction to Computer Science",
        "lecturer_name": "Dr. Smith",
        "description": "Basic computer science concepts"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/courses", json=course_data)
        if response.status_code == 200:
            course = response.json()
            print(f"✓ Created course: {course['course_name']}")
            return course['id']
        else:
            print(f"✗ Failed to create course: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating course: {e}")
        return None

def create_sample_session(course_id):
    """Create a sample session"""
    now = datetime.now()
    session_data = {
        "course_id": course_id,
        "session_name": "Lecture 1 - Introduction",
        "scheduled_start": now.isoformat(),
        "scheduled_end": (now + timedelta(hours=2)).isoformat(),
        "room_location": "Room 101"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/sessions", json=session_data)
        if response.status_code == 200:
            session = response.json()
            print(f"✓ Created session: {session['session_name']}")
            return session['id']
        else:
            print(f"✗ Failed to create session: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating session: {e}")
        return None

def main():
    print("Setting up sample data...")
    print("Make sure the API server is running on http://localhost:8000")
    
    # Create course
    course_id = create_sample_course()
    if not course_id:
        print("Failed to create course. Exiting.")
        return
    
    # Create session
    session_id = create_sample_session(course_id)
    if not session_id:
        print("Failed to create session. Exiting.")
        return
    
    print(f"\n✅ Sample data created successfully!")
    print(f"Course ID: {course_id}")
    print(f"Session ID: {session_id}")
    print("\nYou can now:")
    print("1. Enroll students using: python enroll_students.py")
    print("2. Start the kiosk using: python kiosk_simple.py")
    print("3. Open the web dashboard: web_dashboard.html")

if __name__ == "__main__":
    main()