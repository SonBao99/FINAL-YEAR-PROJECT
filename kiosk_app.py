import cv2
import requests
import base64
import json
import time
import numpy as np
from datetime import datetime
import os

class AttendanceKiosk:
    def __init__(self, api_base_url="http://localhost:8000", session_id=None):
        self.api_base_url = api_base_url
        self.session_id = session_id
        self.cap = None
        self.last_recognition_time = 0
        self.recognition_cooldown = 3  # seconds between recognitions
        
    def start_kiosk(self):
        """Start the kiosk application"""
        print("Starting Attendance Kiosk...")
        print("Press 'q' to quit, 's' to select session")
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Set webcam properties for better face detection
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Load face detection cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Main loop
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Process frame
            processed_frame = self.process_frame(frame)
            
            # Display frame
            cv2.imshow('Attendance Kiosk', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.select_session()
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("Kiosk stopped")
    
    def process_frame(self, frame):
        """Process each frame for face detection and recognition"""
        # Create a copy for display
        display_frame = frame.copy()
        
        # Add session info
        if self.session_id:
            cv2.putText(display_frame, f"Session ID: {self.session_id}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame, "No session selected - Press 's'", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Check if we should attempt recognition
            current_time = time.time()
            if (self.session_id and 
                current_time - self.last_recognition_time > self.recognition_cooldown):
                
                # Extract face region
                face_region = frame[y:y+h, x:x+w]
                
                # Attempt face recognition
                result = self.recognize_face(face_region)
                
                if result:
                    # Draw recognition result
                    cv2.putText(display_frame, result, (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    self.last_recognition_time = current_time
        
        # Add instructions
        cv2.putText(display_frame, "Look at the camera for attendance", (10, display_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return display_frame
    
    def recognize_face(self, face_image):
        """Send face image to API for recognition"""
        try:
            # Encode image to base64
            _, buffer = cv2.imencode('.jpg', face_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send to API
            response = requests.post(
                f"{self.api_base_url}/api/attendance/check-in",
                params={"session_id": self.session_id},
                json={"face_image_base64": image_base64},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return f"Welcome {result.get('student_name', 'Unknown')}!"
                else:
                    return result.get("message", "Recognition failed")
            else:
                return "API Error"
                
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return "Connection Error"
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Error"
    
    def select_session(self):
        """Allow user to select an active session"""
        try:
            # Get active sessions from API
            response = requests.get(f"{self.api_base_url}/api/sessions/active")
            if response.status_code == 200:
                sessions = response.json()
                if sessions:
                    print("\nAvailable sessions:")
                    for i, session in enumerate(sessions):
                        print(f"{i+1}. {session['session_name']} (ID: {session['id']})")
                    
                    try:
                        choice = int(input("Select session number: ")) - 1
                        if 0 <= choice < len(sessions):
                            self.session_id = sessions[choice]['id']
                            print(f"Selected session: {sessions[choice]['session_name']}")
                        else:
                            print("Invalid selection")
                    except ValueError:
                        print("Invalid input")
                else:
                    print("No active sessions available")
            else:
                print("Failed to fetch sessions")
        except Exception as e:
            print(f"Error selecting session: {e}")

def main():
    kiosk = AttendanceKiosk()
    kiosk.start_kiosk()

if __name__ == "__main__":
    main()
```

```
