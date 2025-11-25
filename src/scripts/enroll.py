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
            print(f"✓ Successfully enrolled {result['name']} (ID: {result['student_id']}) from {os.path.basename(image_path)}")
            return True
        else:
            print(f"✗ Error enrolling student from {os.path.basename(image_path)}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed for {os.path.basename(image_path)}: {e}")
        return False

def main():
    """Enroll a student with 3-5 images"""
    print("=" * 50)
    print("Student Enrollment System - Multiple Images")
    print("=" * 50)
    
    # Get student information
    student_id = input("\nEnter student ID: ").strip()
    name = input("Enter student name: ").strip()
    email = input("Enter student email: ").strip()
    
    # Get image paths
    print("\nEnter paths to 3-5 images of the student (one per line, or comma-separated):")
    print("You can also enter a directory path to use all images in that directory.")
    image_input = input("Image paths: ").strip()
    
    image_paths = []
    
    # Check if it's a directory
    if os.path.isdir(image_input):
        # Get all image files from directory
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        for ext in image_extensions:
            image_paths.extend(Path(image_input).glob(f'*{ext}'))
            image_paths.extend(Path(image_input).glob(f'*{ext.upper()}'))
        image_paths = [str(p) for p in image_paths[:5]]  # Limit to 5 images
        print(f"\nFound {len(image_paths)} images in directory")
    else:
        # Parse comma-separated or newline-separated paths
        if ',' in image_input:
            image_paths = [p.strip() for p in image_input.split(',')]
        else:
            # Single path or ask for more
            image_paths = [image_input]
            print("\nEnter additional image paths (press Enter after each, empty line to finish):")
            while len(image_paths) < 5:
                additional = input(f"Image {len(image_paths) + 1}: ").strip()
                if not additional:
                    break
                image_paths.append(additional)
    
    # Validate image paths
    valid_paths = []
    for path in image_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"Warning: Image not found: {path}")
    
    if len(valid_paths) < 3:
        print(f"\nError: Need at least 3 valid images, but only found {len(valid_paths)}")
        return
    
    if len(valid_paths) > 5:
        print(f"\nWarning: More than 5 images provided. Using first 5.")
        valid_paths = valid_paths[:5]
    
    print(f"\nEnrolling student with {len(valid_paths)} images...")
    print("-" * 50)
    
    # Get API URL (optional)
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    # Enroll with each image
    success_count = 0
    for i, image_path in enumerate(valid_paths, 1):
        print(f"\n[{i}/{len(valid_paths)}] Processing: {os.path.basename(image_path)}")
        if enroll_student_from_image(image_path, student_id, name, email, api_url):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Enrollment complete: {success_count}/{len(valid_paths)} images processed successfully")
    print("=" * 50)
    
    if success_count > 0:
        print(f"\n✓ Student {name} (ID: {student_id}) enrolled successfully!")
    else:
        print(f"\n✗ Failed to enroll student. Please check your images and API connection.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nEnrollment cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

