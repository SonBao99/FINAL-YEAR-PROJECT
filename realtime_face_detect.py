# Import necessary libraries
import cv2
import dlib
import requests
import os

import time # For FPS calculation

def download_haar_cascade(url, save_path):
    """Downloads a file from a URL if it doesn't exist."""
    if not os.path.exists(save_path):
        print(f"Downloading {save_path}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status() # Raise an exception for HTTP errors
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            print("Please ensure you have an internet connection or manually download the file and place it in the correct path.")
            return False
    return True

def detect_faces_opencv_haar_frame(frame, face_cascade):
    """
    Detects faces in a single frame using OpenCV's Haar Cascade classifier.

    Args:
        frame: The input frame (from webcam).
        face_cascade: The loaded Haar Cascade classifier.

    Returns:
        Frame with detected faces highlighted.
        List of face bounding boxes (x, y, w, h).
    """
    if frame is None:
        return None, []

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    frame_with_detections = frame.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(frame_with_detections, (x, y), (x + w, y + h), (0, 255, 0), 2) # Green

    return frame_with_detections, faces

def detect_faces_dlib_hog_frame(frame, hog_face_detector):
    """
    Detects faces in a single frame using Dlib's HOG-based face detector.

    Args:
        frame: The input frame (from webcam).
        hog_face_detector: The loaded Dlib HOG face detector.

    Returns:
        Frame with detected faces highlighted.
        List of Dlib rectangle objects.
    """
    if frame is None:
        return None, []

    # Dlib HOG detector works best with BGR images directly from OpenCV
    detections = hog_face_detector(frame, 0) # Use 0 for faster processing on live video, or 1 for upsampling for smaller faces

    frame_with_detections = frame.copy()
    for face in detections:
        x, y, r, b = face.left(), face.top(), face.right(), face.bottom()
        cv2.rectangle(frame_with_detections, (x, y), (r, b), (255, 0, 0), 2) # Blue

    return frame_with_detections, detections

# --- Main execution ---
if __name__ == "__main__":
    # --- Configuration ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path for Haar Cascade XML file
    haar_cascade_filename = "haarcascade_frontalface_default.xml"
    haar_cascade_url = f"https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/{haar_cascade_filename}"
    haar_cascade_local_path = os.path.join(script_dir, haar_cascade_filename)

    # --- Download Haar Cascade if necessary ---
    if not download_haar_cascade(haar_cascade_url, haar_cascade_local_path):
        print("Exiting due to Haar Cascade download failure.")
        exit()

    # --- Load Classifiers ---
    face_cascade_opencv = cv2.CascadeClassifier(haar_cascade_local_path)
    if face_cascade_opencv.empty():
        print(f"Error: Could not load Haar Cascade classifier from {haar_cascade_local_path}")
        exit()
    
    hog_face_detector_dlib = dlib.get_frontal_face_detector()

    # --- Initialize Webcam ---
    # 0 is usually the default built-in webcam. If you have multiple, try 1, 2, etc.
    cap = cv2.VideoCapture(0) 
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()
    
    print("Webcam initialized. Press 'q' to quit.")
    print("Displaying two windows: 'OpenCV Haar Real-time' and 'Dlib HOG Real-time'.")

    # --- Variables for FPS calculation ---
    fps_opencv = 0
    fps_dlib = 0
    frame_count_opencv = 0
    frame_count_dlib = 0
    start_time_opencv = time.time()
    start_time_dlib = time.time()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        # --- OpenCV Haar Cascade Detection on the current frame ---
        current_time_opencv = time.time()
        frame_with_opencv_detections, opencv_faces = detect_faces_opencv_haar_frame(frame.copy(), face_cascade_opencv) # Use a copy for independent processing
        
        frame_count_opencv += 1
        if (current_time_opencv - start_time_opencv) >= 1.0: # Calculate FPS every second
            fps_opencv = frame_count_opencv / (current_time_opencv - start_time_opencv)
            frame_count_opencv = 0
            start_time_opencv = current_time_opencv
        
        if frame_with_opencv_detections is not None:
            cv2.putText(frame_with_opencv_detections, f"OpenCV FPS: {fps_opencv:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame_with_opencv_detections, f"Faces: {len(opencv_faces)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('OpenCV Haar Real-time', frame_with_opencv_detections)
        
        # --- Dlib HOG Detection on the current frame ---
        current_time_dlib = time.time()
        frame_with_dlib_detections, dlib_faces = detect_faces_dlib_hog_frame(frame.copy(), hog_face_detector_dlib) # Use a copy

        frame_count_dlib += 1
        if (current_time_dlib - start_time_dlib) >= 1.0: # Calculate FPS every second
            fps_dlib = frame_count_dlib / (current_time_dlib - start_time_dlib)
            frame_count_dlib = 0
            start_time_dlib = current_time_dlib

        if frame_with_dlib_detections is not None:
            cv2.putText(frame_with_dlib_detections, f"Dlib FPS: {fps_dlib:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame_with_dlib_detections, f"Faces: {len(dlib_faces)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.imshow('Dlib HOG Real-time', frame_with_dlib_detections)

        # Check for 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture and destroy windows
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam feed stopped and windows closed.")

