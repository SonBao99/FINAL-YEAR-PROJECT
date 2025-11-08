import requests
import os
import sys
from datetime import datetime, timedelta

def get_courses(api_url="http://localhost:8000"):
    """Get all existing courses"""
    try:
        # Note: There might not be a GET /api/courses endpoint, so we'll handle that
        # For now, we'll create a course if needed
        return []
    except Exception as e:
        print(f"Error fetching courses: {e}")
        return []

def create_course(course_code, course_name, lecturer_name, description=None, api_url="http://localhost:8000"):
    """Create a new course"""
    course_data = {
        "course_code": course_code,
        "course_name": course_name,
        "lecturer_name": lecturer_name
    }
    if description:
        course_data["description"] = description
    
    try:
        response = requests.post(f"{api_url}/api/courses", json=course_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Course created: {result['course_code']} - {result['course_name']}")
            return result['id']
        else:
            print(f"✗ Error creating course: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        return None

def create_session(course_id, session_name, scheduled_start, scheduled_end, room_location=None, api_url="http://localhost:8000"):
    """Create a new attendance session"""
    session_data = {
        "course_id": course_id,
        "session_name": session_name,
        "scheduled_start": scheduled_start.isoformat(),
        "scheduled_end": scheduled_end.isoformat()
    }
    if room_location:
        session_data["room_location"] = room_location
    
    try:
        response = requests.post(f"{api_url}/api/sessions", json=session_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Session created: {result['session_name']} (ID: {result['id']})")
            return result['id']
        else:
            print(f"✗ Error creating session: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        return None

def start_session(session_id, api_url="http://localhost:8000"):
    """Start an attendance session"""
    try:
        response = requests.post(f"{api_url}/api/sessions/{session_id}/start")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Session started successfully!")
            return True
        else:
            print(f"✗ Error starting session: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        return False

def main():
    """Create and start a new attendance session"""
    print("=" * 50)
    print("Session Creation and Activation")
    print("=" * 50)
    
    # Get API URL
    api_url = os.getenv("API_URL", "http://localhost:8000")
    print(f"\nAPI URL: {api_url}")
    
    # Course information
    print("\n--- Course Information ---")
    use_existing = input("Do you want to use an existing course? (y/n): ").strip().lower()
    
    course_id = None
    
    if use_existing == 'y':
        course_id_input = input("Enter existing course ID: ").strip()
        try:
            course_id = int(course_id_input)
        except ValueError:
            print("Invalid course ID. Creating new course instead...")
            use_existing = 'n'
    
    if not course_id:
        print("\nCreating a new course...")
        course_code = input("Enter course code (e.g., CS101): ").strip()
        course_name = input("Enter course name: ").strip()
        lecturer_name = input("Enter lecturer name: ").strip()
        description = input("Enter course description (optional): ").strip() or None
        
        course_id = create_course(course_code, course_name, lecturer_name, description, api_url)
        if not course_id:
            print("Failed to create course. Exiting.")
            return
    
    # Session information
    print("\n--- Session Information ---")
    session_name = input("Enter session name (e.g., 'Lecture 1', 'Lab Session'): ").strip()
    
    # Get scheduled times
    print("\nEnter scheduled start time:")
    print("You can enter 'now' for current time, or a time in format: YYYY-MM-DD HH:MM")
    start_input = input("Start time: ").strip()
    
    if start_input.lower() == 'now':
        scheduled_start = datetime.now()
    else:
        try:
            scheduled_start = datetime.strptime(start_input, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid format. Using current time.")
            scheduled_start = datetime.now()
    
    # Default end time is 2 hours after start
    default_end = scheduled_start + timedelta(hours=2)
    print(f"\nEnter scheduled end time (default: {default_end.strftime('%Y-%m-%d %H:%M')}):")
    end_input = input("End time (press Enter for default): ").strip()
    
    if not end_input:
        scheduled_end = default_end
    else:
        try:
            scheduled_end = datetime.strptime(end_input, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid format. Using default (2 hours after start).")
            scheduled_end = default_end
    
    room_location = input("Enter room location (optional): ").strip() or None
    
    # Create session
    print("\n" + "-" * 50)
    print("Creating session...")
    session_id = create_session(
        course_id, 
        session_name, 
        scheduled_start, 
        scheduled_end, 
        room_location, 
        api_url
    )
    
    if not session_id:
        print("Failed to create session. Exiting.")
        return
    
    # Start session
    print("\n" + "-" * 50)
    start_now = input("Do you want to start the session now? (y/n): ").strip().lower()
    
    if start_now == 'y':
        print("Starting session...")
        if start_session(session_id, api_url):
            print("\n" + "=" * 50)
            print(f"✓ Session is now active!")
            print(f"  Session ID: {session_id}")
            print(f"  Session Name: {session_name}")
            print(f"  You can now use this session ID in the kiosk app")
            print("=" * 50)
        else:
            print("\nSession created but failed to start. You can start it later.")
    else:
        print("\n" + "=" * 50)
        print(f"✓ Session created (not started yet)")
        print(f"  Session ID: {session_id}")
        print(f"  Session Name: {session_name}")
        print(f"  To start it later, use: POST /api/sessions/{session_id}/start")
        print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

