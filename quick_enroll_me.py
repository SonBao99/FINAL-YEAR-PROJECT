#!/usr/bin/env python3
"""
Quick enrollment script for enrolling yourself
"""
import requests
import base64
import cv2
import os
import sys
from pathlib import Path

def enroll_student_from_image(image_path, student_id, name, email, api_url="http://localhost:8000"):
    """Enroll a student using an image file"""
    
    # Read and encode image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return False
    
    # Encode to base64
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Prepare student data
    student_data = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "photo_base64": image_base64
    }
    
    try:
        # Send enrollment request
        response = requests.post(f"{api_url}/api/students/enroll", json=student_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully enrolled {result['name']} (ID: {result['student_id']})")
            return True
        else:
            print(f"✗ Error enrolling student: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Quick Self-Enrollment")
    print("=" * 60)
    
    # Find the photo in images folder
    images_dir = Path("images")
    photo_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png"))
    
    if not photo_files:
        print("Error: No photos found in images/ folder")
        return
    
    # Use the most recent photo (or first one)
    photo_path = str(photo_files[0])
    print(f"\nFound photo: {photo_path}")
    
    # Student info - you can modify these
    student_id = "STU002"
    name = "Bao Son"
    email = "baoson@example.com"
    
    print(f"\nEnrolling:")
    print(f"  Student ID: {student_id}")
    print(f"  Name: {name}")
    print(f"  Email: {email}")
    print(f"  Photo: {os.path.basename(photo_path)}")
    
    # Check API connection
    api_url = "http://localhost:8000"
    try:
        response = requests.get(f"{api_url}/api/students", timeout=3)
        if response.status_code != 200:
            print(f"\n⚠ Warning: API might not be running (status {response.status_code})")
    except:
        print(f"\n⚠ Warning: Cannot connect to API at {api_url}")
        print("  Make sure the API server is running!")
        return
    
    # Enroll
    print("\n" + "-" * 60)
    success = enroll_student_from_image(photo_path, student_id, name, email, api_url)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Enrollment successful!")
        print("\nYou can now test face recognition with the kiosk app:")
        print("  python3 kiosk_app.py --api http://localhost:8000 --session 1 --camera 0")
    else:
        print("❌ Enrollment failed. Check the error messages above.")
    print("=" * 60)

if __name__ == "__main__":
    main()

