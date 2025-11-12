import argparse
import logging
import os
import time
from datetime import datetime
import base64
import json
from collections import deque

import cv2
import numpy as np
import requests
import sys
import mediapipe as mp


class LivenessDetector:
    """Liveness detection using MediaPipe Face Mesh"""
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        self.face_positions = deque(maxlen=10)
        self.blink_history = deque(maxlen=5)
        
        self.MOVEMENT_THRESHOLD = 0.02
        self.BLINK_THRESHOLD = 0.25
        self.MIN_FRAMES_FOR_LIVE = 10
        self.frame_count = 0
        
    def calculate_eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio for blink detection"""
        eye_points = np.array([(landmarks[i].x, landmarks[i].y) for i in eye_indices])
        vertical_1 = np.linalg.norm(eye_points[1] - eye_points[7])
        vertical_2 = np.linalg.norm(eye_points[2] - eye_points[6])
        horizontal = np.linalg.norm(eye_points[0] - eye_points[4])
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal) if horizontal > 0 else 0
        return ear
    
    def detect_movement(self, landmarks):
        """Detect face movement"""
        if len(landmarks) == 0:
            return False
        nose_tip = np.array([landmarks[4].x, landmarks[4].y])
        self.face_positions.append(nose_tip)
        if len(self.face_positions) < 2:
            return False
        positions_array = np.array(list(self.face_positions))
        movement = np.std(positions_array, axis=0)
        return np.sum(movement) > self.MOVEMENT_THRESHOLD
    
    def detect_blink(self, landmarks):
        """Detect blinking"""
        left_ear = self.calculate_eye_aspect_ratio(landmarks, self.LEFT_EYE_INDICES)
        right_ear = self.calculate_eye_aspect_ratio(landmarks, self.RIGHT_EYE_INDICES)
        avg_ear = (left_ear + right_ear) / 2.0
        self.blink_history.append(avg_ear)
        if len(self.blink_history) < 3:
            return False
        recent_ears = list(self.blink_history)
        if len(recent_ears) >= 3:
            if recent_ears[-2] < self.BLINK_THRESHOLD and recent_ears[-1] > self.BLINK_THRESHOLD:
                return True
        return False
    
    def detect_liveness(self, frame):
        """Detect if face is LIVE or FAKE"""
        self.frame_count += 1
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return "NO_FACE", {}
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        has_movement = self.detect_movement(landmarks)
        has_blink = self.detect_blink(landmarks)
        
        z_coords = [lm.z for lm in landmarks]
        depth_variance = np.var(z_coords)
        has_depth = depth_variance > 0.0001
        
        liveness_score = sum([has_movement, has_blink, has_depth])
        
        if self.frame_count < self.MIN_FRAMES_FOR_LIVE:
            status = "CHECKING"
        elif liveness_score >= 2:
            status = "LIVE"
        else:
            status = "FAKE"
        
        metadata = {
            "has_movement": has_movement,
            "has_blink": has_blink,
            "has_depth": has_depth,
            "liveness_score": liveness_score,
            "frame_count": self.frame_count
        }
        
        return status, metadata


class AttendanceKiosk:
    def __init__(self, api_base_url: str = "http://localhost:8000", session_id: str | None = None,
                 camera_index: int = 0, recognition_cooldown: float = 3.0, save_snapshots: bool = False,
                 verbose: bool = False):
        self.api_base_url = api_base_url
        self.session_id = session_id
        self.camera_index = camera_index
        self.verbose = verbose
        self.cap = None
        self.camera_index = camera_index
        self.last_recognition_time = 0.0
        self.recognition_cooldown = recognition_cooldown  # seconds between recognitions
        self.save_snapshots = save_snapshots
        self.snapshot_dir = os.path.join(os.getcwd(), "kiosk_snapshots") if save_snapshots else None
        self.last_status_message = ""
        self.last_status_time = 0.0
        # Initialize liveness detector
        self.liveness_detector = LivenessDetector()
        self.current_liveness_status = "CHECKING"
        self.current_liveness_metadata = {}

    def start_kiosk(self):
        """Start the kiosk application"""
        logging.info("Starting Attendance Kiosk...")
        if self.verbose:
            print("Starting Attendance Kiosk...")
            print(f"API URL: {self.api_base_url}")
            print(f"Camera Index: {self.camera_index}")
            if self.session_id:
                print(f"Session ID: {self.session_id}")
            else:
                print("No session ID specified - Press 's' to select session")
        print("Press 'q' to quit, 's' to select session, 'r' to refresh sessions, 't' to toggle snapshots")
        # Initialize webcam
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logging.error("Error: Could not open webcam (index=%s)", self.camera_index)
            return

        # Set webcam properties for better face detection
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # Load face detection cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            logging.error("Failed to load face cascade at %s", cascade_path)
            return

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
            elif key == ord('r'):
                # refresh sessions
                self.select_session(refresh=True)
            elif key == ord('t'):
                # toggle snapshot saving
                self.save_snapshots = not self.save_snapshots
                if self.save_snapshots and not self.snapshot_dir:
                    self.snapshot_dir = os.path.join(os.getcwd(), "kiosk_snapshots")
                print(f"Save snapshots: {self.save_snapshots}")

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

        # Detect liveness on full frame
        liveness_status, liveness_metadata = self.liveness_detector.detect_liveness(frame)
        self.current_liveness_status = liveness_status
        self.current_liveness_metadata = liveness_metadata
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            # Color based on liveness status
            if liveness_status == "LIVE":
                face_color = (0, 255, 0)  # Green
            elif liveness_status == "FAKE":
                face_color = (0, 0, 255)  # Red
            else:
                face_color = (0, 255, 255)  # Yellow (checking)
            
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), face_color, 2)

            # Check if we should attempt recognition
            current_time = time.time()
            if (self.session_id and
                    current_time - self.last_recognition_time > self.recognition_cooldown):

                # Only proceed if face is LIVE
                if liveness_status == "LIVE":
                    # Extract face region (expand slightly to include features)
                    pad = int(0.15 * max(w, h))
                    x0 = max(0, x - pad)
                    y0 = max(0, y - pad)
                    x1 = min(frame.shape[1], x + w + pad)
                    y1 = min(frame.shape[0], y + h + pad)
                    face_region = frame[y0:y1, x0:x1]

                    # Attempt face recognition
                    result, metadata = self.recognize_face(face_region)

                    if result:
                        # Draw recognition result
                        cv2.putText(display_frame, result, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        self.last_recognition_time = current_time
                        self.last_status_message = result
                        self.last_status_time = current_time
                        # optionally save snapshot
                        if self.save_snapshots and face_region is not None:
                            label = metadata.get("student_name") if metadata else None
                            self.save_snapshot(face_region, label)
                elif liveness_status == "FAKE":
                    # Show that check-in is blocked due to fake face
                    if self.verbose:
                        logging.info("Check-in blocked: Face detected as FAKE")
                    self.last_status_message = "Check-in blocked: FAKE face detected"
                    self.last_status_time = current_time

        # Draw liveness status
        liveness_color = (0, 255, 0) if liveness_status == "LIVE" else (0, 0, 255) if liveness_status == "FAKE" else (0, 255, 255)
        cv2.putText(display_frame, f"Status: {liveness_status}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, liveness_color, 2)
        
        # Add instructions
        cv2.putText(display_frame, "Look at the camera for attendance", (10, display_frame.shape[0] - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Draw last status message briefly
        if self.last_status_message and time.time() - self.last_status_time < 5:
            cv2.putText(display_frame, f"{self.last_status_message}", (10, display_frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        return display_frame

    def recognize_face(self, face_image):
        """Send face image to API for recognition.

        Returns a tuple (message_or_None, metadata_dict).
        """
        metadata = {}
        try:
            # Encode image to base64
            _, buffer = cv2.imencode('.jpg', face_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            if self.verbose:
                logging.debug("Sending face recognition request to %s/api/attendance/check-in", self.api_base_url)

            payload = {
                "session_id": self.session_id,
                "face_image_base64": image_base64
            }

            # Send to API with simple retry
            attempts = 2
            response = None
            for attempt in range(attempts):
                try:
                    response = requests.post(
                        f"{self.api_base_url}/api/attendance/check-in",
                        json=payload,
                        timeout=5
                    )
                    if self.verbose:
                        logging.debug("Response status: %s", response.status_code)
                    break
                except requests.exceptions.RequestException as e:
                    logging.warning("Recognition request failed (attempt %d): %s", attempt + 1, e)
                    response = None
                    time.sleep(0.5)

            if response is None:
                return ("Connection Error", metadata)
            if response.status_code == 200:
                result = response.json()
                metadata = result
                if result.get("success"):
                    message = f"Welcome {result.get('student_name', 'Unknown')}!"
                    if self.verbose:
                        logging.debug("Recognition successful: %s", message)
                    return (message, metadata)
                else:
                    message = result.get("message", "Recognition failed")
                    if self.verbose:
                        logging.debug("Recognition failed: %s", message)
                    return (message, metadata)
            else:
                error_msg = f"API returned error status: {response.status_code} - {response.text}"
                logging.error(error_msg)
                if self.verbose:
                    logging.debug(error_msg)
                return ("API Error", metadata)

        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {e}"
            logging.warning(error_msg)
            if self.verbose:
                logging.debug(error_msg)
            return ("Connection Error", metadata)
        except Exception as e:
            error_msg = f"Unexpected recognition error: {e}"
            logging.exception(error_msg)
            if self.verbose:
                logging.debug(error_msg)
            return ("Error", metadata)

    def save_snapshot(self, face_image, label: str | None = None) -> None:
        """Save a cropped face snapshot for debugging/audit."""
        if not self.save_snapshots:
            return
        try:
            if not self.snapshot_dir:
                self.snapshot_dir = os.path.join(os.getcwd(), "kiosk_snapshots")
            os.makedirs(self.snapshot_dir, exist_ok=True)
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            safe_label = label.replace(" ", "_") if label else "unknown"
            filename = f"{ts}_{safe_label}.jpg"
            path = os.path.join(self.snapshot_dir, filename)
            cv2.imwrite(path, face_image)
            logging.info("Saved snapshot %s", path)
        except Exception:
            logging.exception("Failed to save snapshot")

    def select_session(self, refresh: bool = False):
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
  python kiosk_app.py --api http://localhost:8000 --camera 0 --session 1 --verbose --cooldown 5.0 --snapshots
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
        type=str,
        default=None,
        help='Session ID to use (optional, can be selected later with \'s\' key)'
    )
    
    parser.add_argument(
        '--cooldown',
        type=float,
        default=3.0,
        help='Recognition cooldown in seconds (default: 3.0)'
    )
    
    parser.add_argument(
        '--snapshots',
        action='store_true',
        help='Save face snapshots to ./kiosk_snapshots'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    
    # Create kiosk instance
    kiosk = AttendanceKiosk(
        api_base_url=args.api,
        session_id=args.session,
        camera_index=args.camera,
        recognition_cooldown=args.cooldown,
        save_snapshots=args.snapshots,
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
