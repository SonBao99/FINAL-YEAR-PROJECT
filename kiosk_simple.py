import cv2
import requests
import base64
import json
import time
import numpy as np
from datetime import datetime
import os

class SimpleAttendanceKiosk:
    def __init__(self, api_base_url="http://localhost:8000", session_id=None):
        self.api_base_url = api_base_url
        self.session_id = session_id
        self.cap = None
        self.students = []
        self.selected_student = None
        
    def start_kiosk(self):
        """Start the kiosk application"""
        print("Starting Simple Attendance Kiosk...")
        print("Press 'q' to quit, 's' to select session, 'l' to list students")
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        # Set webcam properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Load face detection cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load students
        self.load_students()
        
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
            elif key == ord('l'):
                self.list_students()
            elif key == ord('c') and self.selected_student:
                self.check_in_student()
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("Kiosk stopped")
    
    def process_frame(self, frame):
        """Process each frame for face detection"""
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
            cv2.putText(display_frame, "Face Detected", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Show selected student
        if self.selected_student:
            cv2.putText(display_frame, f"Selected: {self.selected_student['name']}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(display_frame, "Press 'c' to check in", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Add instructions
        cv2.putText(display_frame, "Press 'l' to list students, 'c' to check in", (10, display_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return display_frame
    
    def load_students(self):
        """Load students from API"""
        try:
            response = requests.get(f"{self.api_base_url}/api/students")
            if response.status_code == 200:
                self.students = response.json()
                print(f"Loaded {len(self.students)} students")
            else:
                print("Failed to load students")
        except Exception as e:
            print(f"Error loading students: {e}")
    
    def list_students(self):
        """List available students"""
        if not self.students:
            print("No students available")
            return
        
        print("\nAvailable students:")
        for i, student in enumerate(self.students):
            print(f"{i+1}. {student['name']} (ID: {student['student_id']})")
        
        try:
            choice = int(input("Select student number: ")) - 1
            if 0 <= choice < len(self.students):
                self.selected_student = self.students[choice]
                print(f"Selected: {self.selected_student['name']}")
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    def check_in_student(self):
        """Check in the selected student"""
        if not self.selected_student or not self.session_id:
            print("No student selected or no active session")
            return
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/attendance/manual-check-in",
                params={
                    "session_id": self.session_id,
                    "student_id": self.selected_student['student_id']
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✓ {result['message']}")
                    self.selected_student = None  # Clear selection
                else:
                    print(f"✗ {result.get('message', 'Check-in failed')}")
            else:
                print(f"API Error: {response.text}")
                
        except Exception as e:
            print(f"Check-in error: {e}")
    
    def select_session(self):
        """Select an active session"""
        try:
            response = requests.get(f"{self.api_base_url}/api/sessions")
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
                    print("No sessions available")
            else:
                print("Failed to fetch sessions")
        except Exception as e:
            print(f"Error selecting session: {e}")

def main():
    kiosk = SimpleAttendanceKiosk()
    kiosk.start_kiosk()

if __name__ == "__main__":
    main()