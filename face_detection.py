import cv2
import numpy as np
from pathlib import Path
import os

def load_image(image_path):
    """Load image handling Unicode paths"""
    try:
        with open(image_path, 'rb') as f:
            image_binary = np.asarray(bytearray(f.read()), dtype=np.uint8)
            img = cv2.imdecode(image_binary, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not decode image at {image_path}")
        return img
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def get_cascade_classifier():
    """Load and verify Haar Cascade classifier"""
    try:
        # Try multiple possible locations for the classifier file
        possible_paths = [
            Path(cv2.__file__).parent / 'data' / 'haarcascade_frontalface_default.xml',
            Path('haarcascade_frontalface_default.xml'),
            Path(os.getcwd()) / 'haarcascade_frontalface_default.xml'
        ]
        
        for cascade_path in possible_paths:
            if cascade_path.exists():
                classifier = cv2.CascadeClassifier(str(cascade_path))
                if not classifier.empty():
                    print(f"Using classifier from: {cascade_path}")
                    return classifier
        
        # If no valid classifier found, download it
        print("Downloading face detection model...")
        import urllib.request
        url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
        local_path = Path('haarcascade_frontalface_default.xml')
        urllib.request.urlretrieve(url, local_path)
        
        classifier = cv2.CascadeClassifier(str(local_path))
        if classifier.empty():
            raise ValueError("Downloaded classifier is invalid")
        return classifier
        
    except Exception as e:
        print(f"Error loading classifier: {e}")
        return None

def detect_faces(image):
    """Detect faces in the image using Haar Cascade classifier"""
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load the face cascade classifier
    face_cascade = get_cascade_classifier()
    if face_cascade is None:
        raise ValueError("Could not load face detection classifier")
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    return faces

def draw_faces(image, faces):
    """Draw rectangles around detected faces"""
    output = image.copy()
    for (x, y, w, h) in faces:
        # Draw rectangle around face
        cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Add text showing "Face Detected"
        cv2.putText(output, 'Face Detected', (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return output

def process_image(image_path):
    """Process image for face detection"""
    # Load image
    image = load_image(image_path)
    if image is None:
        return False
    
    # Detect faces
    faces = detect_faces(image)
    print(f"Found {len(faces)} faces!")
    
    # Draw detected faces
    result = draw_faces(image, faces)
    
    # Display result
    cv2.imshow('Face Detection Result', result)
    print("Press any key to close the window.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return True

if __name__ == "__main__":
    # Get the script directory
    script_dir = Path(__file__).parent.resolve()
    image_dir = script_dir / "images"
    
    # Set up image path
    sample_image = "sample_image1.png"
    image_path = image_dir / sample_image
    
    if not image_path.is_file():
        print(f"\nNo image found at: {image_path}")
        print("\nPlease ensure you have:")
        print(f"1. An 'images' folder in {script_dir}")
        print(f"2. An image named '{sample_image}' in the images folder")
    else:
        process_image(image_path)