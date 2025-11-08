import cv2
import requests
import base64
import json
import time
import numpy as np
from datetime import datetime
import os
import argparse
import sys

class AttendanceKiosk:
    def __init__(self, api_base_url="http://localhost:8000", session_id=None, camera_index=0, verbose=False):
        self.api_base_url = api_base_url
        self.session_id = session_id
        self.camera_index = camera_index
        self.verbose = verbose
        self.cap = None
        self.last_recognition_time = 0
        self.recognition_cooldown = 3  # seconds between recognitions
        
    def start_kiosk(self):
        """Start the kiosk application"""
        print("Starting Attendance Kiosk...")
        print(f"API URL: {self.api_base_url}")
        print(f"Camera Index: {self.camera_index}")
        if self.session_id:
            print(f"Session ID: {self.session_id}")
        else:
            print("No session ID specified - Press 's' to select session")
        print("Press 'q' to quit, 's' to select session")
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(self.camera_index)
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
            
            if self.verbose:
                print(f"[VERBOSE] Sending face recognition request to {self.api_base_url}/api/attendance/check-in")
            
            # Send to API
            response = requests.post(
                f"{self.api_base_url}/api/attendance/check-in",
                params={"session_id": self.session_id},
                json={"face_image_base64": image_base64},
                timeout=5
            )
            
            if self.verbose:
                print(f"[VERBOSE] Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    message = f"Welcome {result.get('student_name', 'Unknown')}!"
                    if self.verbose:
                        print(f"[VERBOSE] Recognition successful: {message}")
                    return message
                else:
                    message = result.get("message", "Recognition failed")
                    if self.verbose:
                        print(f"[VERBOSE] Recognition failed: {message}")
                    return message
            else:
                if self.verbose:
                    print(f"[VERBOSE] API returned error status: {response.status_code} - {response.text}")
                return "API Error"
                
        except requests.exceptions.RequestException as e:
            if self.verbose:
                print(f"[VERBOSE] API request failed: {e}")
            return "Connection Error"
        except Exception as e:
            if self.verbose:
                print(f"[VERBOSE] Recognition error: {e}")
            return "Error"
    
    def select_session(self):
        """Allow user to select an active session"""
        try:
            # Get all sessions from API (we'll filter active ones)
            response = requests.get(f"{self.api_base_url}/api/sessions")
            if response.status_code == 200:
                all_sessions = response.json()
                # Filter for active sessions
                active_sessions = [s for s in all_sessions if s.get('is_active', False)]
                
                if active_sessions:
                    print("\nAvailable active sessions:")
                    for i, session in enumerate(active_sessions):
                        print(f"{i+1}. {session['session_name']} (ID: {session['id']})")
                    
                    try:
                        choice = int(input("Select session number: ")) - 1
                        if 0 <= choice < len(active_sessions):
                            self.session_id = active_sessions[choice]['id']
                            print(f"Selected session: {active_sessions[choice]['session_name']}")
                        else:
                            print("Invalid selection")
                    except ValueError:
                        print("Invalid input")
                else:
                    print("No active sessions available")
                    print("\nAll sessions:")
                    for i, session in enumerate(all_sessions):
                        status = "ACTIVE" if session.get('is_active', False) else "INACTIVE"
                        print(f"{i+1}. {session['session_name']} (ID: {session['id']}) - {status}")
                    print("\nNote: You can start a session using start_session.py")
            else:
                print(f"Failed to fetch sessions: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error selecting session: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(
        description="AI Attendance Kiosk - Face recognition attendance system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start kiosk with default settings
  python kiosk_app.py
  
  # Start with custom API URL and camera
  python kiosk_app.py --api http://localhost:8000 --camera 0
  
  # Start with session ID and verbose mode
  python kiosk_app.py --api http://localhost:8000 --session 1 --verbose
  
  # Start with all options
  python kiosk_app.py --api http://localhost:8000 --camera 0 --session 1 --verbose
        """
    )
    
    parser.add_argument(
        '--api',
        type=str,
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera index (default: 0)'
    )
    
    parser.add_argument(
        '--session',
        type=int,
        default=None,
        help='Session ID to use (optional, can be selected later with \'s\' key)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Create kiosk instance
    kiosk = AttendanceKiosk(
        api_base_url=args.api,
        session_id=args.session,
        camera_index=args.camera,
        verbose=args.verbose
    )
    
    try:
        kiosk.start_kiosk()
    except KeyboardInterrupt:
        print("\n\nKiosk stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
