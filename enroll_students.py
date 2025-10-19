import requests
import base64
import cv2
import os
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
            print(f"Successfully enrolled {result['name']} (ID: {result['student_id']})")
            return True
        else:
            print(f"Error enrolling student: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return False

def main():
    """Interactive student enrollment"""
    print("Student Enrollment System")
    print("========================")
    
    # Get student information
    student_id = input("Enter student ID: ")
    name = input("Enter student name: ")
    email = input("Enter student email: ")
    
    # Get image path
    image_path = input("Enter path to student photo: ")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return
    
    # Enroll student
    if enroll_student_from_image(image_path, student_id, name, email):
        print("Student enrolled successfully!")
    else:
        print("Failed to enroll student")

if __name__ == "__main__":
    main()