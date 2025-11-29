import argparse
import logging
import os
import time
from datetime import datetime
from typing import Optional, Dict, Tuple
import base64
import json
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import asyncio
import websockets

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
        
        # Relaxed thresholds for better usability
        self.MOVEMENT_THRESHOLD = 0.01  # Lowered from 0.02 - more sensitive to natural movement
        self.BLINK_THRESHOLD = 0.25
        self.MIN_FRAMES_FOR_LIVE = 5  # Reduced from 10 - faster initial check
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
        elif liveness_score >= 1:  # Changed from >= 2 to >= 1 - more lenient
            # If depth is detected (which is usually always true for real faces),
            # consider it LIVE even without movement/blink
            # This makes the system more user-friendly while still checking depth
            if has_depth:
                status = "LIVE"
            elif liveness_score >= 2:
                status = "LIVE"
            else:
                status = "FAKE"
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
    def __init__(self, api_base_url: str = "http://localhost:8000", session_id: Optional[str] = None,
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
        # Track recent liveness status for smoother recognition
        self.recent_liveness_history = deque(maxlen=10)  # Last 10 frames
        self.liveness_grace_period = 5  # Allow recognition if LIVE in last 5 frames
        # Track recognized student info for persistent display (multi-face support)
        # Key: face_id (tuple of bbox coordinates), Value: student info dict
        self.recognized_students: Dict[Tuple[int, int, int, int], Dict] = {}
        self.face_recognition_times: Dict[Tuple[int, int, int, int], float] = {}
        self.face_recognition_lock = threading.Lock()
        # Auto-refresh session more frequently to detect web changes
        self.last_session_check = 0.0
        self.session_check_interval = 5.0  # seconds - check every 5 seconds for web changes
        self.cached_session_name = None  # Cache session name to avoid API calls every frame
        self.cached_session_status = None  # Cache session status (active/inactive)
        # Multi-face recognition settings
        self.max_concurrent_faces = 5  # Maximum faces to process simultaneously
        self.face_recognition_executor = ThreadPoolExecutor(max_workers=self.max_concurrent_faces)
        # Video streaming settings
        self.stream_video = True  # Enable video streaming to web dashboard
        self.video_stream_ws = None  # WebSocket connection for video streaming
        self.video_stream_interval = 0.1  # Send frame every 100ms (10 FPS)
        self.last_frame_sent = 0.0
        self.video_stream_thread = None
        self.video_stream_running = False
        self.video_stream_loop = None
        # Stats tracking for real-time display
        self.stats = {
            "total_frames": 0,
            "faces_detected": 0,
            "recognition_attempts": 0,
            "recognition_success": 0,
            "recognition_failed": 0,
            "liveness_checks": 0,
            "liveness_live": 0,
            "liveness_fake": 0,
            "current_faces": 0,
            "current_liveness_status": "CHECKING",
            "session_name": None,
            "last_update": time.time()
        }
        self.stats_update_interval = 0.5  # Update stats every 500ms
        self.last_stats_sent = 0.0

    def get_active_session(self):
        """Automatically fetch the current active session from the API"""
        try:
            response = requests.get(f"{self.api_base_url}/api/sessions", timeout=3)
            if response.status_code == 200:
                all_sessions = response.json()
                # Find the first active session
                active_sessions = [s for s in all_sessions if s.get('is_active', False)]
                
                if active_sessions:
                    # Return the first active session (most recent if sorted)
                    return active_sessions[0]
                else:
                    if self.verbose:
                        logging.debug("No active sessions found")
                    return None
            else:
                if self.verbose:
                    logging.warning(f"Failed to fetch sessions: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            if self.verbose:
                logging.warning(f"Error fetching active session: {e}")
            return None
        except Exception as e:
            if self.verbose:
                logging.error(f"Unexpected error fetching active session: {e}")
            return None

    def auto_select_active_session(self):
        """Automatically select the active session if available"""
        active_session = self.get_active_session()
        if active_session:
            # Update session if it changed or if we don't have one
            if self.session_id != active_session['id']:
                old_session_id = self.session_id
                self.session_id = active_session['id']
                self.cached_session_name = active_session['session_name']
                self.cached_session_status = active_session.get('is_active', False)
                if self.verbose:
                    logging.info(f"Session updated: {old_session_id} -> {active_session['id']} ({active_session['session_name']})")
            else:
                # Update cached info
                self.cached_session_name = active_session['session_name']
                self.cached_session_status = active_session.get('is_active', False)
            return True
        else:
            # Clear session if no active session found
            if self.session_id:
                if self.verbose:
                    logging.info(f"No active session found - clearing session {self.session_id}")
                self.session_id = None
            self.cached_session_name = None
            self.cached_session_status = None
            if self.verbose:
                logging.debug("No active session found for auto-selection")
            return False

    def start_kiosk(self):
        """Start the kiosk application"""
        logging.info("Starting Attendance Kiosk...")
        if self.verbose:
            print("Starting Attendance Kiosk...")
            print(f"API URL: {self.api_base_url}")
            print(f"Camera Index: {self.camera_index}")
        
        # Auto-select active session if not manually specified
        if not self.session_id:
            print("Auto-detecting active session...")
            if self.auto_select_active_session():
                active_session = self.get_active_session()
                print(f"✓ Auto-selected session: {active_session['session_name']} (ID: {self.session_id})")
            else:
                print("⚠ No active session found - Press 's' to select session manually")
        else:
            print(f"Using manually specified session ID: {self.session_id}")
        
        if self.verbose:
            if self.session_id:
                print(f"Session ID: {self.session_id}")
            else:
                print("No session ID specified - Press 's' to select session")
        print("Press 'q' to quit, 's' to select session, 'r' to refresh/auto-detect session, 't' to toggle snapshots")
        
        # Start video streaming to web dashboard
        if self.stream_video:
            self.start_video_streaming()
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logging.error("Error: Could not open webcam (index=%s)", self.camera_index)
            return

        # Allow camera to initialize
        import time
        time.sleep(0.5)
        
        # Try reading a test frame to ensure camera is ready
        for _ in range(5):
            ret, _ = self.cap.read()
            if ret:
                break
            time.sleep(0.1)
        else:
            logging.warning("Camera opened but initial frame read failed. Continuing anyway...")

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
        frame_count = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logging.warning("Could not read frame (attempt %d), retrying...", frame_count)
                frame_count += 1
                if frame_count > 10:
                    logging.error("Failed to read frames after 10 attempts. Stopping.")
                    break
                time.sleep(0.1)
                continue
            
            frame_count = 0  # Reset counter on successful read

            # Process frame
            try:
                processed_frame = self.process_frame(frame)
            except Exception as e:
                logging.error("Error processing frame: %s", e)
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                continue

            # Display frame
            cv2.imshow('Attendance Kiosk', processed_frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.select_session()
            elif key == ord('r'):
                # Refresh/auto-detect active session
                print("\nRefreshing active session...")
                if self.auto_select_active_session():
                    active_session = self.get_active_session()
                    print(f"✓ Auto-selected session: {active_session['session_name']} (ID: {self.session_id})")
                else:
                    print("⚠ No active session found - Press 's' to select manually")
                    # Fall back to manual selection
                    self.select_session(refresh=True)
            elif key == ord('t'):
                # toggle snapshot saving
                self.save_snapshots = not self.save_snapshots
                if self.save_snapshots and not self.snapshot_dir:
                    self.snapshot_dir = os.path.join(os.getcwd(), "kiosk_snapshots")
                print(f"Save snapshots: {self.save_snapshots}")

        # Cleanup
        self.stop_video_streaming()
        self.face_recognition_executor.shutdown(wait=True)
        self.cap.release()
        cv2.destroyAllWindows()
        print("Kiosk stopped")

    def process_frame(self, frame):
        """Process each frame for face detection and recognition"""
        # Create a copy for display
        display_frame = frame.copy()

        # Auto-refresh session periodically to detect web changes
        current_time = time.time()
        if current_time - self.last_session_check > self.session_check_interval:
            self.last_session_check = current_time
            # Always check for active session to detect web changes
            active_session = self.get_active_session()
            if active_session:
                # Update if session changed or if we don't have one
                if not self.session_id or self.session_id != active_session['id']:
                    self.auto_select_active_session()
                else:
                    # Update cached info for current session
                    self.cached_session_name = active_session['session_name']
                    self.cached_session_status = active_session.get('is_active', False)
            else:
                # No active session - clear if we had one
                if self.session_id:
                    self.session_id = None
                    self.cached_session_name = None
                    self.cached_session_status = None

        # Add session info with status
        if self.session_id:
            session_name = self.cached_session_name or f"Session {self.session_id}"
            # Show "In Progress" if session is active
            if self.cached_session_status:
                session_text = f"Session: {session_name} [IN PROGRESS]"
                session_color = (0, 255, 0)  # Green
            else:
                session_text = f"Session: {session_name}"
                session_color = (255, 255, 0)  # Yellow (selected but not active)
            cv2.putText(display_frame, session_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, session_color, 2)
        else:
            cv2.putText(display_frame, "No session - Auto-detecting...", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        # Limit to max_concurrent_faces for multi-face processing
        faces = faces[:self.max_concurrent_faces]
        
        current_time = time.time()
        
        # Track current face IDs
        current_face_ids = {tuple(face) for face in faces}
        
        # Update stats - only count newly detected faces (not already tracked)
        with self.face_recognition_lock:
            existing_face_ids = set(self.recognized_students.keys())
            new_faces = current_face_ids - existing_face_ids
            if new_faces:
                self.stats["faces_detected"] += len(new_faces)
        
        # Clean up old recognized faces that are no longer detected
        with self.face_recognition_lock:
            faces_to_remove = [face_id for face_id in self.recognized_students.keys() 
                             if face_id not in current_face_ids]
            for face_id in faces_to_remove:
                # Remove if face hasn't been seen for more than 2 seconds
                if current_time - self.face_recognition_times.get(face_id, 0) > 2.0:
                    self.recognized_students.pop(face_id, None)
                    self.face_recognition_times.pop(face_id, None)

        # Detect liveness on full frame
        liveness_status, liveness_metadata = self.liveness_detector.detect_liveness(frame)
        self.current_liveness_status = liveness_status
        self.current_liveness_metadata = liveness_metadata
        
        # Update liveness stats
        self.stats["liveness_checks"] += 1
        if liveness_status == "LIVE":
            self.stats["liveness_live"] += 1
        elif liveness_status == "FAKE":
            self.stats["liveness_fake"] += 1
        
        # Track recent liveness for smoother recognition
        self.recent_liveness_history.append(liveness_status == "LIVE")
        
        # Consider "effectively LIVE" if current is LIVE or was LIVE recently
        was_recently_live = sum(self.recent_liveness_history) >= 1
        effectively_live = (liveness_status == "LIVE") or was_recently_live
        
        # Process faces for recognition (multi-face support)
        if effectively_live and self.session_id and len(faces) > 0:
            self.process_multiple_faces(frame, faces, current_time)
        
        # Draw rectangles around detected faces and display recognition info
        for (x, y, w, h) in faces:
            # Color based on effective liveness status (for smoother UX)
            if effectively_live:
                face_color = (0, 255, 0)  # Green
            elif liveness_status == "FAKE":
                face_color = (0, 0, 255)  # Red
            else:
                face_color = (0, 255, 255)  # Yellow (checking)
            
            face_id = (x, y, w, h)
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), face_color, 2)

            # Display recognized student info on green box if available (multi-face support)
            if effectively_live:
                # Draw text area background (semi-transparent black box at top of face box)
                text_box_height = 70
                overlay = display_frame.copy()
                cv2.rectangle(overlay, (x, y), (x + w, y + text_box_height), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)
                
                # Check if this face has been recognized
                with self.face_recognition_lock:
                    recognized_info = self.recognized_students.get(face_id)
                
                if recognized_info:
                    student_name = recognized_info.get("name", "Unknown")
                    student_id = recognized_info.get("student_id", "N/A")
                    confidence = recognized_info.get("confidence", 0.0)
                    status_msg = recognized_info.get("status_message", "")
                    
                    # Display name and ID on the green box
                    name_text = f"{student_name}"
                    if status_msg and "already checked in" in status_msg.lower():
                        name_text += " (Already checked in)"
                    elif status_msg:
                        name_text += f" ({status_msg[:15]})"
                    
                    id_text = f"ID: {student_id}"
                    confidence_text = f"Conf: {confidence*100:.1f}%"
                    
                    # Calculate text position (inside the box, at the top)
                    text_y = y + 25
                    text_y2 = y + 45
                    text_y3 = y + 65
                    
                    # Draw text with outline for better visibility
                    cv2.putText(display_frame, name_text, (x + 5, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)  # Black outline
                    cv2.putText(display_frame, name_text, (x + 5, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)  # White text
                    
                    cv2.putText(display_frame, id_text, (x + 5, text_y2),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Black outline
                    cv2.putText(display_frame, id_text, (x + 5, text_y2),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 255, 200), 1)  # Light green text
                    
                    cv2.putText(display_frame, confidence_text, (x + 5, text_y3),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)  # Black outline
                    cv2.putText(display_frame, confidence_text, (x + 5, text_y3),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 255, 150), 1)  # Green text
                elif self.session_id:
                    # Show "Recognizing..." when live but not yet recognized
                    status_text = "Recognizing..."
                    status_color = (255, 255, 0)  # Yellow
                    
                    cv2.putText(display_frame, status_text, (x + 5, y + 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)  # Black outline
                    cv2.putText(display_frame, status_text, (x + 5, y + 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)  # Yellow text
                else:
                    # Show "No session" when no session selected
                    cv2.putText(display_frame, "No session", (x + 5, y + 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)  # Black outline
                    cv2.putText(display_frame, "No session", (x + 5, y + 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # White text

        # Draw liveness status (show effective status)
        display_status = "LIVE" if effectively_live else liveness_status
        liveness_color = (0, 255, 0) if display_status == "LIVE" else (0, 0, 255) if display_status == "FAKE" else (0, 255, 255)
        status_text = f"Status: {display_status}"
        if effectively_live and liveness_status != "LIVE":
            status_text += " (recent)"
        cv2.putText(display_frame, status_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, liveness_color, 2)
        
        # Add instructions
        cv2.putText(display_frame, "Look at the camera for attendance", (10, display_frame.shape[0] - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Update stats
        self.stats["total_frames"] += 1
        self.stats["current_faces"] = len(faces)
        self.stats["current_liveness_status"] = liveness_status
        self.stats["session_name"] = self.cached_session_name or f"Session {self.session_id}" if self.session_id else "No Session"
        self.stats["last_update"] = time.time()
        
        # Send frame to web dashboard if streaming is enabled
        if self.stream_video and self.video_stream_running:
            current_time_stream = time.time()
            if current_time_stream - self.last_frame_sent >= self.video_stream_interval:
                if self.video_stream_ws:
                    self.send_video_frame(display_frame)
                self.last_frame_sent = current_time_stream
            
            # Send stats update periodically
            if current_time_stream - self.last_stats_sent >= self.stats_update_interval:
                if self.video_stream_ws:
                    self.send_stats_update()
                self.last_stats_sent = current_time_stream

        return display_frame

    def process_multiple_faces(self, frame, faces, current_time):
        """Process multiple faces simultaneously for recognition"""
        if not self.session_id:
            return
        
        # Check cooldown for each face individually
        faces_to_process = []
        for (x, y, w, h) in faces:
            face_id = (x, y, w, h)
            last_recognition_time = self.face_recognition_times.get(face_id, 0)
            
            # Process if enough time has passed since last recognition for this face
            if current_time - last_recognition_time > self.recognition_cooldown:
                # Extract face region (expand slightly to include features)
                pad = int(0.15 * max(w, h))
                x0 = max(0, x - pad)
                y0 = max(0, y - pad)
                x1 = min(frame.shape[1], x + w + pad)
                y1 = min(frame.shape[0], y + h + pad)
                face_region = frame[y0:y1, x0:x1]
                
                faces_to_process.append((face_id, face_region))
        
        if not faces_to_process:
            return
        
        # Process faces in parallel using thread pool
        futures = {}
        for face_id, face_region in faces_to_process:
            self.stats["recognition_attempts"] += 1
            future = self.face_recognition_executor.submit(self.recognize_face, face_region)
            futures[future] = face_id
        
        # Process results as they complete
        for future in as_completed(futures):
            face_id = futures[future]
            try:
                result, metadata = future.result()
                
                if self.verbose:
                    logging.debug(f"Face {face_id}: result={result}, success={metadata.get('success') if metadata else False}")
                
                with self.face_recognition_lock:
                    # Update recognition time
                    self.face_recognition_times[face_id] = current_time
                    
                    if result and metadata:
                        # Check if face was recognized (has student_name and student_id)
                        is_recognized = metadata.get("student_name") and metadata.get("student_id")
                        
                        if metadata.get("success") == True:
                            # Store recognized student info for this face
                            self.recognized_students[face_id] = {
                                "name": metadata.get("student_name", "Unknown"),
                                "student_id": metadata.get("student_id", "N/A"),
                                "confidence": metadata.get("confidence", 0.0),
                                "status_message": ""
                            }
                            # Count as recognition success (face recognized AND check-in succeeded)
                            self.stats["recognition_success"] += 1
                            
                            if self.verbose:
                                logging.info(f"✓ Face {face_id} recognized: {self.recognized_students[face_id]['name']} "
                                           f"(ID: {self.recognized_students[face_id]['student_id']})")
                            
                            # Save snapshot if enabled
                            if self.save_snapshots:
                                # Extract face region again for snapshot
                                x, y, w, h = face_id
                                pad = int(0.15 * max(w, h))
                                x0 = max(0, x - pad)
                                y0 = max(0, y - pad)
                                x1 = min(frame.shape[1], x + w + pad)
                                y1 = min(frame.shape[0], y + h + pad)
                                face_region = frame[y0:y1, x0:x1]
                                label = metadata.get("student_name")
                                self.save_snapshot(face_region, label)
                                
                        elif is_recognized:
                            # Face recognized but check-in failed (e.g., already checked in)
                            # Still count as recognition success since the face was recognized
                            self.recognized_students[face_id] = {
                                "name": metadata.get("student_name", "Unknown"),
                                "student_id": metadata.get("student_id", "N/A"),
                                "confidence": metadata.get("confidence", 0.0),
                                "status_message": metadata.get("message", "")
                            }
                            # Count as recognition success (face was recognized, even if check-in failed)
                            self.stats["recognition_success"] += 1
                            
                            if self.verbose:
                                logging.info(f"✓ Face {face_id} recognized but check-in failed: "
                                           f"{self.recognized_students[face_id]['name']} - {metadata.get('message')}")
                        else:
                            # Recognition failed - remove from recognized list
                            self.recognized_students.pop(face_id, None)
                            # Count as recognition failure
                            self.stats["recognition_failed"] += 1
                            
                            if self.verbose:
                                logging.debug(f"✗ Face {face_id} recognition failed: "
                                            f"{metadata.get('message', 'Unknown error') if metadata else 'No metadata'}")
                    else:
                        # No result - remove from recognized list
                        self.recognized_students.pop(face_id, None)
                        # Count as recognition failure
                        self.stats["recognition_failed"] += 1
                        
            except Exception as e:
                logging.error(f"Error processing face {face_id}: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                with self.face_recognition_lock:
                    self.recognized_students.pop(face_id, None)

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
                error_msg = "Connection Error - API not responding"
                logging.error(error_msg)
                metadata["error_message"] = error_msg
                return ("Connection Error", metadata)
            if response.status_code == 200:
                result = response.json()
                metadata = result
                if self.verbose:
                    logging.debug("API Response: %s", result)
                if result.get("success"):
                    message = f"Welcome {result.get('student_name', 'Unknown')}!"
                    if self.verbose:
                        logging.info("Recognition successful: %s (ID: %s, Confidence: %s)", 
                                   message, result.get('student_id'), result.get('confidence'))
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

    def save_snapshot(self, face_image, label: Optional[str] = None) -> None:
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

    def start_video_streaming(self):
        """Start video streaming thread to send frames to web dashboard"""
        if self.video_stream_running:
            return
        
        self.video_stream_running = True
        self.video_stream_thread = threading.Thread(target=self._video_stream_loop, daemon=True)
        self.video_stream_thread.start()
        if self.verbose:
            logging.info("Video streaming started")

    def stop_video_streaming(self):
        """Stop video streaming"""
        self.video_stream_running = False
        if self.video_stream_loop:
            try:
                # Schedule close in the event loop
                if self.video_stream_loop.is_running():
                    asyncio.run_coroutine_threadsafe(self._close_websocket(), self.video_stream_loop)
                else:
                    # If loop is not running, create a new one to close the connection
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._close_websocket())
                    loop.close()
            except Exception as e:
                if self.verbose:
                    logging.debug(f"Error closing WebSocket: {e}")
        if self.video_stream_thread:
            self.video_stream_thread.join(timeout=2)
        if self.verbose:
            logging.info("Video streaming stopped")

    async def _close_websocket(self):
        """Close WebSocket connection"""
        if self.video_stream_ws:
            try:
                # Send a close message to notify the server
                await self.video_stream_ws.close()
            except Exception as e:
                if self.verbose:
                    logging.debug(f"Error closing WebSocket: {e}")
            finally:
                self.video_stream_ws = None

    def _video_stream_loop(self):
        """Background thread loop for video streaming"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.video_stream_loop = loop
        try:
            loop.run_until_complete(self._connect_and_stream())
        except Exception as e:
            if self.verbose:
                logging.error(f"Video stream error: {e}")
        finally:
            loop.close()
            self.video_stream_loop = None

    async def _connect_and_stream(self):
        """Connect to video stream WebSocket and keep connection alive"""
        ws_url = self.api_base_url.replace("http://", "ws://").replace("https://", "wss://") + "/ws/video-stream"
        print(f"Attempting to connect to video stream at: {ws_url}")
        while self.video_stream_running:
            try:
                async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as websocket:
                    self.video_stream_ws = websocket
                    print("✓ Connected to video stream WebSocket")
                    if self.verbose:
                        logging.info("Connected to video stream WebSocket")
                    # Keep connection alive - send ping periodically
                    while self.video_stream_running:
                        try:
                            await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        except asyncio.TimeoutError:
                            pass  # Keep connection alive
                        except websockets.exceptions.ConnectionClosed as e:
                            print(f"WebSocket connection closed: {e}")
                            break
            except websockets.exceptions.InvalidURI as e:
                print(f"✗ Invalid WebSocket URI: {e}")
                if self.video_stream_running:
                    await asyncio.sleep(5)  # Retry after 5 seconds
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"✗ WebSocket connection closed error: {e}")
                if self.video_stream_running:
                    await asyncio.sleep(2)  # Retry after 2 seconds
            except Exception as e:
                print(f"✗ Video stream connection error: {e}")
                if self.verbose:
                    logging.warning(f"Video stream connection error: {e}")
                    import traceback
                    traceback.print_exc()
                if self.video_stream_running:
                    await asyncio.sleep(2)  # Retry after 2 seconds
            finally:
                self.video_stream_ws = None
                if self.video_stream_running:
                    print("Reconnecting to video stream...")

    def send_video_frame(self, frame):
        """Send a video frame to the web dashboard via WebSocket"""
        if not self.video_stream_ws or not self.video_stream_loop:
            return
        
        try:
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send frame asynchronously
            message = json.dumps({
                "type": "video_frame",
                "frame": frame_base64
            })
            
            # Use asyncio to send in the streaming thread's event loop
            if self.video_stream_loop and self.video_stream_loop.is_running():
                asyncio.run_coroutine_threadsafe(self._send_frame_async(message), self.video_stream_loop)
        except Exception as e:
            if self.verbose:
                logging.debug(f"Error sending video frame: {e}")

    async def _send_frame_async(self, message):
        """Async helper to send frame"""
        try:
            if self.video_stream_ws:
                await self.video_stream_ws.send(message)
        except Exception as e:
            if self.verbose:
                logging.debug(f"Error in async send: {e}")
            self.video_stream_ws = None

    def send_stats_update(self):
        """Send stats update to web dashboard via WebSocket"""
        if not self.video_stream_ws or not self.video_stream_loop:
            return
        
        try:
            message = json.dumps({
                "type": "stats_update",
                "stats": self.stats.copy()
            })
            
            # Use asyncio to send in the streaming thread's event loop
            if self.video_stream_loop and self.video_stream_loop.is_running():
                asyncio.run_coroutine_threadsafe(self._send_frame_async(message), self.video_stream_loop)
        except Exception as e:
            if self.verbose:
                logging.debug(f"Error sending stats update: {e}")

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
                            self.cached_session_name = active_sessions[choice]['session_name']
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
