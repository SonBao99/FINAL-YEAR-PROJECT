"""
Liveness Detection Test using MediaPipe
Detects if a face is LIVE (real person) or FAKE (photo/video)
"""
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

class LivenessDetector:
    def __init__(self):
        """Initialize MediaPipe Face Mesh for liveness detection"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks (left and right eye)
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Face position history for movement detection
        self.face_positions = deque(maxlen=10)
        self.blink_history = deque(maxlen=5)
        
        # Thresholds
        self.MOVEMENT_THRESHOLD = 0.02  # Minimum face position change
        self.BLINK_THRESHOLD = 0.25  # Eye aspect ratio threshold for blink
        self.MIN_FRAMES_FOR_LIVE = 10  # Minimum frames to determine liveness
        
        self.frame_count = 0
        
    def calculate_eye_aspect_ratio(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        eye_points = np.array([(landmarks[i].x, landmarks[i].y) for i in eye_indices])
        
        # Calculate distances
        vertical_1 = np.linalg.norm(eye_points[1] - eye_points[7])
        vertical_2 = np.linalg.norm(eye_points[2] - eye_points[6])
        horizontal = np.linalg.norm(eye_points[0] - eye_points[4])
        
        # Calculate EAR
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear
    
    def detect_movement(self, landmarks):
        """Detect if face has moved (indicates live person)"""
        if len(landmarks) == 0:
            return False
        
        # Use nose tip position as reference (landmark 4)
        nose_tip = np.array([landmarks[4].x, landmarks[4].y])
        self.face_positions.append(nose_tip)
        
        if len(self.face_positions) < 2:
            return False
        
        # Calculate movement variance
        positions_array = np.array(list(self.face_positions))
        movement = np.std(positions_array, axis=0)
        total_movement = np.sum(movement)
        
        return total_movement > self.MOVEMENT_THRESHOLD
    
    def detect_blink(self, landmarks):
        """Detect if person is blinking"""
        left_ear = self.calculate_eye_aspect_ratio(landmarks, self.LEFT_EYE_INDICES)
        right_ear = self.calculate_eye_aspect_ratio(landmarks, self.RIGHT_EYE_INDICES)
        
        # Average EAR
        avg_ear = (left_ear + right_ear) / 2.0
        self.blink_history.append(avg_ear)
        
        if len(self.blink_history) < 3:
            return False
        
        # Check if there's a significant drop (blink)
        recent_ears = list(self.blink_history)
        if len(recent_ears) >= 3:
            # Check for blink pattern (drop then rise)
            if recent_ears[-2] < self.BLINK_THRESHOLD and recent_ears[-1] > self.BLINK_THRESHOLD:
                return True
        
        return False
    
    def detect_liveness(self, frame):
        """Detect if face is LIVE or FAKE"""
        self.frame_count += 1
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return "NO_FACE", {}
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Check for movement
        has_movement = self.detect_movement(landmarks)
        
        # Check for blink
        has_blink = self.detect_blink(landmarks)
        
        # Calculate 3D depth (using face mesh depth variation)
        # Real faces have depth variation, photos are flat
        z_coords = [lm.z for lm in landmarks]
        depth_variance = np.var(z_coords)
        has_depth = depth_variance > 0.0001  # Threshold for 3D structure
        
        # Determine liveness
        liveness_score = 0
        if has_movement:
            liveness_score += 1
        if has_blink:
            liveness_score += 1
        if has_depth:
            liveness_score += 1
        
        # Need minimum frames to make decision
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

def main():
    """Main function to test liveness detection"""
    print("=" * 50)
    print("Liveness Detection Test")
    print("=" * 50)
    print("\nInstructions:")
    print("  - Point camera at a REAL face: Should show 'LIVE'")
    print("  - Point camera at a PHOTO: Should show 'FAKE'")
    print("  - Press 'q' to quit")
    print("-" * 50)
    
    # Initialize detector
    detector = LivenessDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open camera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n[INFO] Starting camera...")
    print("[INFO] Look at the camera and wait for liveness detection...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Could not read frame")
            break
        
        # Detect liveness
        status, metadata = detector.detect_liveness(frame)
        
        # Draw status on frame
        color = (0, 255, 0) if status == "LIVE" else (0, 0, 255) if status == "FAKE" else (0, 255, 255)
        cv2.putText(frame, f"Status: {status}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw metadata
        y_offset = 60
        cv2.putText(frame, f"Movement: {metadata.get('has_movement', False)}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset += 25
        cv2.putText(frame, f"Blink: {metadata.get('has_blink', False)}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset += 25
        cv2.putText(frame, f"Depth: {metadata.get('has_depth', False)}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset += 25
        cv2.putText(frame, f"Score: {metadata.get('liveness_score', 0)}/3", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Print to console
        if status != "CHECKING":
            print(f"\r[{status}] Movement: {metadata.get('has_movement', False)}, "
                  f"Blink: {metadata.get('has_blink', False)}, "
                  f"Depth: {metadata.get('has_depth', False)}", end="", flush=True)
        
        # Display frame
        cv2.imshow('Liveness Detection Test', frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\n\n[INFO] Test completed")

if __name__ == "__main__":
    main()


