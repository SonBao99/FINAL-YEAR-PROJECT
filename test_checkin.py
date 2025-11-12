"""
Test check-in flow - simulates kiosk check-in using enrolled student image
"""
import requests
import base64
import cv2
import os

def test_checkin_with_image(image_path, session_id, api_url="http://localhost:8000"):
    """Test check-in using an image file"""
    
    # Read and encode image
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Could not load image {image_path}")
        return False
    
    # Encode to base64
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Prepare check-in request (both session_id and face_image_base64 in JSON body)
    payload = {
        "session_id": session_id,
        "face_image_base64": image_base64
    }
    
    try:
        print(f"Sending check-in request to {api_url}/api/attendance/check-in")
        print(f"Session ID: {session_id}")
        print(f"Image: {os.path.basename(image_path)}")
        
        response = requests.post(
            f"{api_url}/api/attendance/check-in",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"\n[SUCCESS] Check-in successful!")
                print(f"  Message: {result.get('message')}")
                print(f"  Student: {result.get('student_name')} (ID: {result.get('student_id')})")
                print(f"  Confidence: {result.get('confidence', 0):.2%}")
                return True
            else:
                print(f"\n[FAILED] Check-in failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"\n[ERROR] API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False

def check_api_connection(api_url="http://localhost:8000"):
    """Check if API is accessible"""
    try:
        response = requests.get(f"{api_url}/api/students", timeout=3)
        return response.status_code == 200
    except:
        return False

def get_active_sessions(api_url="http://localhost:8000"):
    """Get list of active sessions"""
    try:
        response = requests.get(f"{api_url}/api/sessions", timeout=3)
        if response.status_code == 200:
            sessions = response.json()
            active = [s for s in sessions if s.get('is_active', False)]
            return active
        return []
    except:
        return []

def main():
    print("=" * 50)
    print("End-to-End Check-in Test")
    print("=" * 50)
    
    api_url = "http://localhost:8000"
    
    # Check API connection
    print("\nStep 1: Checking API connection...")
    if not check_api_connection(api_url):
        print(f"[ERROR] Cannot connect to API at {api_url}")
        print("  Make sure API server is running!")
        return
    print("[OK] API connection successful")
    
    # Get active sessions
    print("\nStep 2: Getting active sessions...")
    active_sessions = get_active_sessions(api_url)
    if not active_sessions:
        print("[ERROR] No active sessions found")
        print("  Create and start a session first using: python quick_session_test.py")
        return
    
    print(f"[OK] Found {len(active_sessions)} active session(s):")
    for s in active_sessions:
        print(f"  - Session {s['id']}: {s['session_name']} (Course: {s.get('course', {}).get('course_code', 'N/A')})")
    
    # Use first active session
    session_id = active_sessions[0]['id']
    print(f"\nUsing Session ID: {session_id}")
    
    # Test with enrolled student image
    print("\nStep 3: Testing check-in with enrolled student image...")
    test_image = "images/sample_image.png"  # This is the image we used for enrollment
    
    if not os.path.exists(test_image):
        print(f"[ERROR] Test image not found: {test_image}")
        print("  Available images in images/ folder:")
        for f in os.listdir("images"):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                print(f"    - images/{f}")
        return
    
    success = test_checkin_with_image(test_image, session_id, api_url)
    
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] End-to-end test completed successfully!")
        print("\nNext step: Verify database with: python check_database.py")
    else:
        print("[FAILED] Check-in test failed")
        print("  Check API logs for details")
    print("=" * 50)

if __name__ == "__main__":
    main()

