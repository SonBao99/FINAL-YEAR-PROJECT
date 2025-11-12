"""
Quick enrollment test script using sample images
"""
import requests
import base64
import cv2
import os

def enroll_student_from_image(image_path, student_id, name, email, api_url="http://localhost:8000"):
    """Enroll a student using an image file"""
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Could not load image {image_path}")
        return False
    
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    student_data = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "photo_base64": image_base64
    }
    
    try:
        response = requests.post(f"{api_url}/api/students/enroll", json=student_data)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Enrolled: {result['name']} (ID: {result['student_id']}) from {os.path.basename(image_path)}")
            return True
        else:
            print(f"[ERROR] Enrollment failed: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] API request failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Quick Enrollment Test")
    print("=" * 50)
    
    api_url = "http://localhost:8000"
    
    # Check API connection
    try:
        r = requests.get(f"{api_url}/api/students", timeout=3)
        print(f"[OK] API connection successful")
    except:
        print(f"[ERROR] Cannot connect to API at {api_url}")
        print("  Make sure API server is running!")
        return
    
    # Student info
    student_id = "TEST001"
    name = "Test Student"
    email = "test@example.com"
    
    # Image paths
    image_paths = [
        "images/sample_image.png",
        "images/sample_image1.png",
        "images/sample_image2.jpg"
    ]
    
    print(f"\nEnrolling student: {name} (ID: {student_id})")
    print(f"Using {len(image_paths)} images from images/ folder")
    print("-" * 50)
    
    success_count = 0
    for i, image_path in enumerate(image_paths, 1):
        if os.path.exists(image_path):
            print(f"\n[{i}/{len(image_paths)}] Processing: {os.path.basename(image_path)}")
            if enroll_student_from_image(image_path, student_id, name, email, api_url):
                success_count += 1
        else:
            print(f"[WARNING] Image not found: {image_path}")
    
    print("\n" + "=" * 50)
    if success_count > 0:
        print(f"[SUCCESS] Enrollment complete: {success_count}/{len(image_paths)} images processed")
        print(f"Student {name} (ID: {student_id}) is now enrolled!")
        print("\nNext steps:")
        print("1. Create a session: python start_session.py")
        print("2. Start the session (answer 'y' when prompted)")
        print("3. Test kiosk: python kiosk_app.py --api http://localhost:8000 --session X")
    else:
        print("[FAILED] No images were successfully processed")
    print("=" * 50)

if __name__ == "__main__":
    main()


