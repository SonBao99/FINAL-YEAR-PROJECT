# Screenshot Placement Guide for Final Report
## AI-Driven Facial Recognition Attendance System

This document provides exact specifications for all screenshots to be included in the final report, including precise code line numbers and detailed explanations.

---

## 📋 TABLE OF CONTENTS

- [Section 2: Introduction](#section-2-introduction)
- [Section 4: Requirement Analysis](#section-4-requirement-analysis)
- [Section 5: Software Design](#section-5-software-design)
- [Section 6: Software Implementation](#section-6-software-implementation)
- [Section 7: Evaluation and Conclusion](#section-7-evaluation-and-conclusion)
- [Section 8: Appendix](#section-8-appendix)

---

## Section 2: Introduction

### Screenshot 2.1: System Overview Dashboard
**Type:** UI Screenshot  
**Location:** Browser - `http://localhost:8000`  
**What to Capture:**
- Dashboard tab active
- Statistics cards showing Total Students, Present, Absent, Attendance Rate
- Attendance records list visible
- Sidebar navigation visible

**Caption:** "Figure 2.1: Main dashboard interface showing real-time attendance statistics and records"

**Explanation:** This screenshot provides a visual introduction to the system, demonstrating the automated attendance tracking solution. The dashboard displays key metrics including total enrolled students, present/absent counts, and attendance rate percentage. The interface showcases the system's ability to transform raw biometric data into actionable insights for academic staff.

---

## Section 4: Requirement Analysis

### Screenshot 4.1: Enrollment Interface
**Type:** UI Screenshot  
**Location:** Browser - Students tab → Click "Enroll Student"  
**What to Capture:**
- Enrollment modal/form visible
- Student ID, Name, Email input fields
- Photo upload area
- Submit and Cancel buttons

**Caption:** "Figure 4.1: Student enrollment interface demonstrating the Enrollment domain functional requirement"

**Explanation:** This screenshot illustrates the Enrollment domain requirement (Section 4.2), showing the administrative interface that facilitates student registration through multiple reference image capture. The interface supports the functional requirement of generating and storing 128-dimensional embedding vectors for each student.

### Screenshot 4.2: Kiosk Verification Interface
**Type:** UI Screenshot  
**Location:** Kiosk window showing liveness detection  
**What to Capture:**
- Kiosk window with camera feed
- Green bounding box around face (LIVE status)
- Status text: "Status: LIVE"
- Session ID displayed

**Caption:** "Figure 4.2: Kiosk verification interface demonstrating dual-verification protocol (liveness + recognition)"

**Explanation:** This screenshot demonstrates the Verification domain requirement (Section 4.2), showing the strict dual-verification protocol. The system performs liveness assessment using depth estimation and blink detection before triggering the computationally intensive recognition phase, meeting the requirement of sequential processing to prevent resource exhaustion.

---

## Section 5: Software Design

### Screenshot 5.1: Project Structure
**Type:** Code/Structure Screenshot  
**Location:** Terminal or File Explorer  
**What to Capture:**
```
FINAL-YEAR-PROJECT/
├── src/
│   ├── api/
│   ├── database/
│   ├── models/
│   └── scripts/
├── tests/
├── assets/
└── requirements.txt
```

**Caption:** "Figure 5.1: Project directory structure demonstrating modular architecture"

**Explanation:** This screenshot illustrates the Service-Oriented Architecture (SOA) design principle (Section 5.1), showing the separation of concerns between API layer, database layer, models, and utility scripts. The modular structure enables independent scaling and maintenance of system components.

### Screenshot 5.2: FastAPI Application Setup
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 1-35  
**What to Capture:**
```python
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
...
app = FastAPI(title="Face Recognition Attendance System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    ...
)

# WebSocket manager for real-time updates
manager = ConnectionManager()
```

**Caption:** "Figure 5.2: FastAPI application initialization with CORS middleware and WebSocket manager"

**Explanation:** This code screenshot demonstrates the Application Layer architecture (Section 5.1.2). FastAPI's asynchronous framework enables handling thousands of concurrent connections. The CORS middleware allows cross-origin requests for the web dashboard, while the ConnectionManager handles WebSocket connections for real-time updates. This design supports the scalability requirement (Section 4.3.4).

### Screenshot 5.3: Database Models - Student Entity
**Type:** Code Screenshot  
**File:** `src/models/models.py`  
**Lines:** 9-22  
**What to Capture:**
```python
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    face_encoding = Column(Text)  # JSON string of face encoding
    photo_path = Column(String(255))  # Path to enrollment photo
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="student")
```

**Caption:** "Figure 5.3: Student entity model demonstrating biometric data storage design"

**Explanation:** This code screenshot illustrates the database schema design (Section 5.3). Critically, the `face_encoding` field stores a 128-dimensional embedding vector as JSON (not raw images), aligning with security requirements (Section 4.3.3). The relationship to `AttendanceRecord` ensures referential integrity. This design follows Third Normal Form (3NF) normalization principles.

### Screenshot 5.4: Database Models - Session and AttendanceRecord
**Type:** Code Screenshot  
**File:** `src/models/models.py`  
**Lines:** 38-72  
**What to Capture:**
```python
class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    session_name = Column(String(200), nullable=False)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    is_active = Column(Boolean, default=False)
    ...

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    check_in_time = Column(DateTime, nullable=False)
    confidence_score = Column(Float)  # Face recognition confidence
    status = Column(String(20), default="present")
    ...
```

**Caption:** "Figure 5.4: Session and AttendanceRecord entities demonstrating temporal modeling and audit trail"

**Explanation:** This code screenshot shows the temporal dimension modeling (Section 5.3). The `Session` entity includes both scheduled and actual timestamps, enabling analysis of session duration. The `is_active` flag implements a "Soft Lock" mechanism preventing check-ins for closed sessions. The `AttendanceRecord` entity stores `confidence_score` (Euclidean distance converted to confidence), providing an audit trail for dispute resolution as mentioned in Section 5.3.

### Screenshot 5.5: Database Connection Configuration
**Type:** Code Screenshot  
**File:** `src/database/database.py`  
**Lines:** 1-44 (full file)  
**What to Capture:**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

if DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres"):
    # PostgreSQL settings (production)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, ...)
else:
    # SQLite settings (development)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Caption:** "Figure 5.5: Database connection abstraction supporting SQLite (development) and PostgreSQL (production)"

**Explanation:** This code screenshot demonstrates the database abstraction layer (Section 5.1.3). SQLAlchemy ORM provides flexibility to operate on SQLite during development (zero-configuration) while remaining deployment-ready for PostgreSQL in production. The `get_db()` function is a FastAPI dependency that provides database sessions with automatic cleanup, ensuring proper resource management.

---

## Section 6: Software Implementation

### Screenshot 6.1: Development Environment - Requirements
**Type:** Code Screenshot  
**File:** `requirements.txt`  
**Lines:** 1-22 (full file)  
**What to Capture:**
```
numpy>=1.24.0
opencv-python>=4.8.0
face-recognition>=1.3.0
fastapi>=0.104.0
mediapipe>=0.10.0
sqlalchemy>=2.0.0
websockets>=12.0
...
```

**Caption:** "Figure 6.1: Python dependencies demonstrating the software stack (Section 6.1.2)"

**Explanation:** This screenshot shows the complete software stack used in development (Section 6.1.2). Key libraries include OpenCV for computer vision, face-recognition (dlib wrapper) for face encoding, Mediapipe for liveness detection, FastAPI for the asynchronous web framework, and SQLAlchemy for database ORM. All dependencies are version-pinned for reproducibility.

### Screenshot 6.2: LivenessDetector Class Initialization
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 18-41  
**What to Capture:**
```python
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
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, ...]
        self.RIGHT_EYE_INDICES = [362, 382, 381, ...]
        
        # Thresholds
        self.MOVEMENT_THRESHOLD = 0.01
        self.BLINK_THRESHOLD = 0.25
        self.MIN_FRAMES_FOR_LIVE = 5
```

**Caption:** "Figure 6.2: LivenessDetector class initialization with MediaPipe Face Mesh and threshold configuration"

**Explanation:** This code screenshot demonstrates the critical liveness detection implementation (Section 6.2.1). MediaPipe Face Mesh provides 468-point 3D face mesh tracking. The eye landmark indices are predefined for blink detection. Thresholds are tuned for usability: `MOVEMENT_THRESHOLD = 0.01` (sensitive to natural movement), `BLINK_THRESHOLD = 0.25` (EAR threshold), and `MIN_FRAMES_FOR_LIVE = 5` (minimum frames before determining liveness). This implements the "Liveness First" policy mentioned in Section 6.2.1.

### Screenshot 6.3: Eye Aspect Ratio Calculation
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 43-50  
**What to Capture:**
```python
def calculate_eye_aspect_ratio(self, landmarks, eye_indices):
    """Calculate Eye Aspect Ratio for blink detection"""
    eye_points = np.array([(landmarks[i].x, landmarks[i].y) for i in eye_indices])
    vertical_1 = np.linalg.norm(eye_points[1] - eye_points[7])
    vertical_2 = np.linalg.norm(eye_points[2] - eye_points[6])
    horizontal = np.linalg.norm(eye_points[0] - eye_points[4])
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal) if horizontal > 0 else 0
    return ear
```

**Caption:** "Figure 6.3: Eye Aspect Ratio (EAR) calculation algorithm for blink detection"

**Explanation:** This code screenshot shows the mathematical foundation of blink detection (Section 6.2.1, Blink Detection). EAR measures eye openness by calculating the ratio of vertical distances (between upper and lower eyelids) to horizontal distance (eye width). When the eye closes, EAR decreases; when it opens, EAR increases. This enables detection of natural biological motion absent in static photos.

### Screenshot 6.4: Blink Detection Logic
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 64-76  
**What to Capture:**
```python
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
            return True  # Blink detected
    return False
```

**Caption:** "Figure 6.4: Blink detection algorithm using temporal EAR analysis"

**Explanation:** This code screenshot demonstrates the dynamic anti-spoofing mechanism (Section 6.2.1). The algorithm calculates EAR for both eyes and maintains a history buffer. A blink is detected when EAR drops below 0.25 (eye closing) and then rises above it (eye opening). The temporal analysis (comparing recent frames) distinguishes natural blinks from static photos, which cannot exhibit this temporal pattern.

### Screenshot 6.5: Depth Detection Algorithm
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 92-94  
**What to Capture:**
```python
z_coords = [lm.z for lm in landmarks]
depth_variance = np.var(z_coords)
has_depth = depth_variance > 0.0001
```

**Caption:** "Figure 6.5: 3D depth variance calculation for static anti-spoofing"

**Explanation:** This code screenshot shows the geometric analysis approach (Section 6.2.1, 3D Depth Analysis). MediaPipe provides z-coordinates (depth) for each of the 468 landmarks. Real faces have significant depth variance (nose protrudes, cheeks recede), while 2D photos on screens are geometrically flat (variance near zero). The threshold `0.0001` distinguishes real 3D faces from flat 2D representations, implementing the primary filter against presentation attacks.

### Screenshot 6.6: Main Liveness Detection Logic
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 78-121  
**What to Capture:**
```python
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
    elif liveness_score >= 1:
        if has_depth:
            status = "LIVE"
        elif liveness_score >= 2:
            status = "LIVE"
        else:
            status = "FAKE"
    else:
        status = "FAKE"
    
    return status, metadata
```

**Caption:** "Figure 6.6: Multi-modal liveness detection combining depth, blink, and movement analysis"

**Explanation:** This code screenshot demonstrates the complete liveness detection algorithm (Section 6.2.1). The system combines three heuristics: depth analysis (static anti-spoofing), blink detection (dynamic anti-spoofing), and movement analysis. The `liveness_score` sums these checks. If depth is detected (usually always true for real faces), the status is "LIVE" even without movement/blink, making the system user-friendly while maintaining security. The `MIN_FRAMES_FOR_LIVE = 5` requirement ensures consistent detection across frames before determining liveness.

### Screenshot 6.7: Movement Detection Algorithm
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 52-62  
**What to Capture:**
```python
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
```

**Caption:** "Figure 6.7: Micro-movement detection using nose tip position variance"

**Explanation:** This code screenshot shows the movement analysis heuristic (Section 6.2.1). The system tracks the nose tip position (landmark index 4) over a temporal window (deque with maxlen=10). The standard deviation of positions measures natural, involuntary micro-movements. Static photos held against a wall lack this movement, while live humans exhibit subtle motion even when attempting to remain still. The threshold `0.01` is tuned to detect these micro-movements.

### Screenshot 6.8: Spoof Detection Blocking Logic
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 310-315  
**What to Capture:**
```python
elif liveness_status == "FAKE":
    # Show that check-in is blocked due to fake face
    if self.verbose:
        logging.info("Check-in blocked: Face detected as FAKE")
    self.last_status_message = "Check-in blocked: FAKE face detected"
    self.last_status_time = current_time
```

**Caption:** "Figure 6.8: Spoof detection feedback loop preventing API calls for fake faces"

**Explanation:** This code screenshot demonstrates the security feedback loop (Section 6.2.2). When a spoof is detected, the kiosk enters a "Blocked" state. The visual cue (red bounding box) and status message inform the user. Critically, the `effectively_live` flag (line 287) prevents the `requests.post()` call to the API, ensuring fraudulent data never reaches the server or database. This implements the security requirement mentioned in Section 6.2.2.

### Screenshot 6.9: Kiosk Frame Processing - Liveness Integration
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 257-267  
**What to Capture:**
```python
# Detect liveness on full frame
liveness_status, liveness_metadata = self.liveness_detector.detect_liveness(frame)
self.current_liveness_status = liveness_status
self.current_liveness_metadata = liveness_metadata

# Track recent liveness for smoother recognition
self.recent_liveness_history.append(liveness_status == "LIVE")

# Consider "effectively LIVE" if current is LIVE or was LIVE recently
was_recently_live = sum(self.recent_liveness_history) >= 1
effectively_live = (liveness_status == "LIVE") or was_recently_live
```

**Caption:** "Figure 6.9: Liveness status tracking with grace period for smoother user experience"

**Explanation:** This code screenshot shows the integration of liveness detection into the frame processing pipeline (Section 6.2). The system maintains a history buffer (`recent_liveness_history`) to allow recognition if the face was LIVE in recent frames, even if the current frame shows "CHECKING". This grace period (5 frames) provides a smoother user experience while maintaining security, as the liveness check must pass at some point in the recent history.

### Screenshot 6.10: Kiosk Frame Processing - Recognition Gate
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 281-287  
**What to Capture:**
```python
# Check if we should attempt recognition
current_time = time.time()
if (self.session_id and
        current_time - self.last_recognition_time > self.recognition_cooldown):

    # Proceed if face is LIVE or was recently LIVE (smoother experience)
    if effectively_live:
        # Extract face region and attempt recognition
        ...
```

**Caption:** "Figure 6.10: Recognition gate ensuring liveness confirmation before API call"

**Explanation:** This code screenshot demonstrates the "Liveness First" policy (Section 6.2.1). Recognition is only attempted if `effectively_live` is True, ensuring no API calls are made for fake faces. The cooldown period (`recognition_cooldown = 3.0` seconds) prevents excessive API requests. This sequential processing prevents system resource exhaustion from invalid attempts, meeting the functional requirement in Section 4.2.

### Screenshot 6.11: Student Enrollment - Face Encoding
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 118-173  
**What to Capture:**
```python
@app.post("/api/students/enroll", response_model=StudentResponse)
async def enroll_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Enroll a new student with face encoding"""
    
    # Decode base64 image
    image_data = base64.b64decode(student.photo_base64)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Find face encodings
    face_encodings = face_recognition.face_encodings(rgb_image)
    if not face_encodings:
        raise HTTPException(status_code=400, detail="No face detected")
    
    # Use the first face encoding
    face_encoding = face_encodings[0]
    
    # Create student record
    db_student = Student(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        face_encoding=json.dumps(face_encoding.tolist()),
        photo_path=str(photo_path)
    )
    
    db.add(db_student)
    db.commit()
```

**Caption:** "Figure 6.11: Student enrollment endpoint generating 128-dimensional face embedding"

**Explanation:** This code screenshot demonstrates Objective 1 (Section 2.3.1) - the computer vision pipeline. The enrollment endpoint decodes the base64 image, converts BGR to RGB for face_recognition library, and generates a 128-dimensional embedding using dlib's ResNet-based model (wrapped by face_recognition). The encoding is stored as JSON string, not raw images, meeting security requirements (Section 4.3.3). This vector-based approach ensures resilience to daily appearance variations.

### Screenshot 6.12: Face Recognition Matching Algorithm
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 341-357  
**What to Capture:**
```python
# Get all enrolled students
students = db.query(Student).filter(Student.is_active == True).all()

best_match = None
best_distance = float('inf')

for student in students:
    if student.face_encoding:
        stored_encoding = np.array(json.loads(student.face_encoding))
        
        # Compare face encodings using Euclidean distance
        distances = face_recognition.face_distance([stored_encoding], face_encodings[0])
        distance = distances[0]
        
        if distance < best_distance and distance < 0.6:  # Threshold
            best_distance = distance
            best_match = student
```

**Caption:** "Figure 6.12: Face recognition matching algorithm using Euclidean distance comparison"

**Explanation:** This code screenshot shows the recognition algorithm (Section 6.2). The system compares the detected face encoding against all enrolled students using Euclidean distance. The best match (lowest distance) below the 0.6 threshold is selected. This threshold balances accuracy and usability - lower values increase security but may cause false rejections. The algorithm iterates through all students, making it O(n) complexity where n is the number of enrolled students.

### Screenshot 6.13: Confidence Score Calculation
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 369-376  
**What to Capture:**
```python
# Create attendance record
attendance_record = AttendanceRecord(
    student_id=best_match.id,
    session_id=request.session_id,
    check_in_time=datetime.utcnow(),
    confidence_score=1 - best_distance,  # Convert distance to confidence
    status="present"
)

db.add(attendance_record)
db.commit()
```

**Caption:** "Figure 6.13: Attendance record creation with confidence score calculation"

**Explanation:** This code screenshot demonstrates the confidence score calculation (Section 5.3). The Euclidean distance is converted to confidence using `confidence = 1 - distance`. For example, distance 0.2 → 80% confidence, distance 0.4 → 60% confidence. This score is stored in the database, providing an audit trail for dispute resolution. The confidence score allows administrators to review the certainty of automated decisions in borderline cases.

### Screenshot 6.14: WebSocket Manager Class
**Type:** Code Screenshot  
**File:** `src/api/websocket_manager.py`  
**Lines:** 1-29 (full file)  
**What to Capture:**
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: int):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    async def broadcast_to_session(self, session_id: int, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    self.active_connections[session_id].remove(connection)
```

**Caption:** "Figure 6.14: WebSocket connection manager for real-time attendance updates"

**Explanation:** This code screenshot demonstrates the WebSocket implementation (Section 3.4.3). The ConnectionManager maintains a dictionary mapping session_id to lists of WebSocket connections, allowing multiple dashboards to connect to the same session. The `broadcast_to_session` method sends JSON messages to all connected clients, enabling real-time updates. Broken connections are automatically removed, ensuring system reliability.

### Screenshot 6.15: WebSocket Endpoint Definition
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 300-309  
**What to Capture:**
```python
# WebSocket endpoint for real-time attendance updates
@app.websocket("/ws/attendance/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
```

**Caption:** "Figure 6.15: WebSocket endpoint using RFC 6455 standard protocol"

**Explanation:** This code screenshot shows the WebSocket endpoint implementation (Section 3.4.3). FastAPI's WebSocket support uses the standard RFC 6455 protocol (not Socket.IO). The endpoint accepts connections per session_id, maintains the connection in a while loop, and handles disconnections gracefully. This enables real-time bidirectional communication for the dashboard's live feed feature.

### Screenshot 6.16: WebSocket Broadcast on Check-In
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 381-388  
**What to Capture:**
```python
# Notify web dashboard via WebSocket
await manager.broadcast_to_session(request.session_id, {
    "type": "attendance_update",
    "student_name": best_match.name,
    "student_id": best_match.student_id,
    "check_in_time": attendance_record.check_in_time.isoformat(),
    "confidence": attendance_record.confidence_score
})
```

**Caption:** "Figure 6.16: WebSocket broadcast triggering real-time dashboard updates"

**Explanation:** This code screenshot demonstrates the real-time update mechanism (Section 3.4.3). After successful check-in, the system broadcasts an attendance_update message to all connected dashboards. The message includes student information, check-in time, and confidence score. This enables the "live feed" feature where lecturer views update instantly when a student checks in, providing immediate feedback and situational awareness.

### Screenshot 6.17: Frontend WebSocket Client Setup
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1981-2051  
**What to Capture:**
```javascript
function setupWebSocket() {
    const wsUrl = `ws://localhost:8000/ws/attendance/${currentSessionId}`;
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
        updateConnectionStatus('Connected', 'success');
        showInfo('WebSocket connected - receiving live updates');
    };
    
    websocket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'attendance_update') {
            loadAttendanceRecords();  // Refresh attendance list
            showDesktopNotification(`${msg.student_name} checked in`);
        }
    };
    
    websocket.onclose = () => {
        reconnectWebSocket();  // Auto-reconnect with exponential backoff
    };
}
```

**Caption:** "Figure 6.17: Frontend WebSocket client with auto-reconnection logic"

**Explanation:** This code screenshot shows the frontend WebSocket implementation (Section 3.4.3). The client uses the native browser WebSocket API (RFC 6455). On message receipt, it refreshes the attendance list and shows desktop notifications. The auto-reconnection with exponential backoff (up to 5 attempts) ensures reliability. This implements the real-time communication requirement mentioned in Section 4.2 (Administration domain).

### Screenshot 6.18: Kiosk API Communication
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 337-401  
**What to Capture:**
```python
def recognize_face(self, face_image):
    """Send face image to API for recognition"""
    # Encode image to base64
    _, buffer = cv2.imencode('.jpg', face_image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    payload = {
        "session_id": self.session_id,
        "face_image_base64": image_base64
    }
    
    # Send to API with retry
    response = requests.post(
        f"{self.api_base_url}/api/attendance/check-in",
        json=payload,
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return (f"Welcome {result.get('student_name')}!", result)
```

**Caption:** "Figure 6.18: Kiosk API communication with base64 image encoding and retry logic"

**Explanation:** This code screenshot demonstrates the client-server communication (Section 5.1.2). The kiosk encodes the face image to base64 for JSON transport, includes the session_id, and sends a POST request to the check-in endpoint. The retry logic (2 attempts) handles transient network failures. This implements Objective 3 (Section 2.3.3) - the scalable client-server architecture where the kiosk performs liveness detection at the edge, and only valid requests are sent to the server.

### Screenshot 6.19: Unit Test Suite
**Type:** Code Screenshot  
**File:** `tests/test_attendance.py`  
**Lines:** 1-97 (full file)  
**What to Capture:**
```python
class TestAttendanceTracker(unittest.TestCase):
    def setUp(self):
        self.class_roster = ["student_01", "student_02", ...]
        self.tracker = AttendanceTracker(self.class_roster)
    
    def test_initialization(self):
        self.assertEqual(len(self.tracker.get_attendance_list()), 0)
    
    def test_mark_present(self):
        self.tracker.mark_present("student_02")
        self.assertIn("student_02", self.tracker.get_attendance_list())
    
    def test_idempotency_of_marking_present(self):
        # Tests duplicate marking doesn't create duplicates
        ...
```

**Caption:** "Figure 6.19: Unit test suite demonstrating testing methodology (Section 6.3.1)"

**Explanation:** This code screenshot shows the unit testing approach (Section 6.3.1). The test suite uses Python's unittest framework with 21 test cases. Tests are fast and isolated, testing the AttendanceTracker class logic in-memory without database or file I/O. This validates core logic including initialization, marking present, handling duplicates, and edge cases. The suite achieves 100% pass rate, ensuring reliability of the attendance calculation engine.

### Screenshot 6.20: Session Management Endpoints
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 208-244  
**What to Capture:**
```python
@app.post("/api/sessions")
async def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new attendance session"""
    db_session = Session(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@app.get("/api/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(Session).all()
    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "course_name": s.course.course_name if s.course else None,
            "session_name": s.session_name,
            "scheduled_start": s.scheduled_start.isoformat(),
            "is_active": s.is_active
        })
    return result
```

**Caption:** "Figure 6.20: Session management API endpoints for creating and listing attendance sessions"

**Explanation:** This code screenshot demonstrates the session management functionality (Section 4.2, Administration domain). The POST endpoint creates new sessions with course linkage, while the GET endpoint retrieves all sessions with course information. This supports the functional requirement of scheduling and managing attendance sessions, enabling lecturers to prepare sessions before class starts.

### Screenshot 6.21: Manual Check-In Endpoint
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 403-464  
**What to Capture:**
```python
@app.post("/api/attendance/manual-check-in")
async def manual_check_in(
    request: ManualCheckInRequest,
    db: Session = Depends(get_db)
):
    """Manually add attendance record"""
    session = db.query(Session).filter(Session.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    student = db.query(Student).filter(Student.student_id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already checked in
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student.id,
        AttendanceRecord.session_id == request.session_id
    ).first()
    
    if existing_record:
        raise HTTPException(status_code=400, detail="Student already checked in")
    
    # Create attendance record and broadcast WebSocket update
    attendance_record = AttendanceRecord(...)
    await manager.broadcast_to_session(request.session_id, {...})
```

**Caption:** "Figure 6.21: Manual check-in endpoint with duplicate prevention and WebSocket notification"

**Explanation:** This code screenshot shows the manual check-in functionality (Section 4.2, Administration domain). The endpoint allows lecturers to manually add attendance records for edge cases (e.g., camera failure, student forgot to check in). It includes validation (session exists, student exists, no duplicates), creates the attendance record, and broadcasts a WebSocket update to keep dashboards synchronized. This supports the requirement for administrative override capabilities.

### Screenshot 6.22: Kiosk Initialization and Camera Setup
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 148-190  
**What to Capture:**
```python
def start_kiosk(self):
    """Start the kiosk application"""
    logging.info("Starting Attendance Kiosk...")
    print(f"API URL: {self.api_base_url}")
    print(f"Camera Index: {self.camera_index}")
    
    # Initialize webcam
    self.cap = cv2.VideoCapture(self.camera_index)
    if not self.cap.isOpened():
        logging.error("Error: Could not open webcam")
        return
    
    # Set webcam properties for better face detection
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    self.cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Load face detection cascade
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    self.face_cascade = cv2.CascadeClassifier(cascade_path)
```

**Caption:** "Figure 6.22: Kiosk initialization with camera configuration and face detection cascade loading"

**Explanation:** This code screenshot demonstrates the kiosk startup sequence (Section 6.1.1). The initialization includes camera opening, property configuration (640x480 resolution, 30 FPS), and loading the Haar Cascade classifier for face detection. The error handling ensures graceful failure if hardware is unavailable. This supports the hardware specification requirement (Section 6.1.1) - compatibility with standard USB webcams.

### Screenshot 6.23: Chart.js Implementation - Attendance Visualization
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 810-833  
**What to Capture:**
```javascript
// Initialize Chart.js for attendance visualization
const ctx = document.getElementById('attendanceChart').getContext('2d');
const attendanceChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Present', 'Absent'],
        datasets: [{
            data: [presentCount, absentCount],
            backgroundColor: ['#4CAF50', '#F44336'],
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'bottom' },
            tooltip: { enabled: true }
        }
    }
});
```

**Caption:** "Figure 6.23: Chart.js implementation for real-time attendance visualization"

**Explanation:** This code screenshot shows the Chart.js integration (Section 5.2.2, Analytics Module). The doughnut chart visualizes present vs. absent ratios, updating dynamically when attendance records change. Chart.js v4.4.0 provides vector-based rendering for crisp visuals. This implements Objective 4 (Section 2.3.4) - the comprehensive management dashboard with data visualization capabilities.

### Screenshot 6.24: Polling Fallback Mechanism
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 3129-3136  
**What to Capture:**
```javascript
// Auto-refresh every 30 seconds
setInterval(() => {
    if (currentSessionId) {
        loadAttendanceRecords();
    }
    checkApiConnection();
}, 30000);
```

**Caption:** "Figure 6.24: Polling fallback mechanism ensuring data freshness when WebSocket fails"

**Explanation:** This code screenshot demonstrates the reliability mechanism (Section 3.4.3). While WebSocket provides real-time updates, the 30-second polling interval ensures data freshness if WebSocket connection fails. This dual-strategy approach (WebSocket + polling) meets the non-functional requirement of reliability (Section 4.3.2), ensuring the dashboard always displays current attendance data even under network instability.

### Screenshot 6.25: Error Handling in Face Recognition
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 312-340  
**What to Capture:**
```python
@app.post("/api/attendance/check-in")
async def check_in_student(request: CheckInRequest, db: Session = Depends(get_db)):
    try:
        # Validate session
        session = db.query(Session).filter(Session.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if not session.is_active:
            raise HTTPException(status_code=400, detail="Session is not active")
        
        # Decode and process image
        image_data = base64.b64decode(request.face_image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error processing check-in: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

**Caption:** "Figure 6.25: Comprehensive error handling in check-in endpoint with validation and logging"

**Explanation:** This code screenshot demonstrates robust error handling (Section 4.3.2, Reliability). The endpoint validates session existence and active status, decodes base64 image data, and handles various failure modes (invalid image, no face detected, network errors). HTTPException is re-raised for client errors, while unexpected exceptions are logged and returned as 500 errors. This ensures system reliability and provides meaningful error messages to clients.

### Screenshot 6.26: Database Session Dependency Injection
**Type:** Code Screenshot  
**File:** `src/database/database.py`  
**Lines:** 30-44  
**What to Capture:**
```python
def get_db():
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in FastAPI endpoints:
@app.get("/api/students")
async def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students
```

**Caption:** "Figure 6.26: Database session dependency injection pattern using FastAPI Depends"

**Explanation:** This code screenshot demonstrates the dependency injection pattern (Section 5.1.2). FastAPI's `Depends(get_db)` automatically manages database session lifecycle - creating a session at request start, yielding it to the endpoint, and closing it in the finally block. This ensures proper resource cleanup and prevents connection leaks, supporting the scalability requirement (Section 4.3.4).

### Screenshot 6.27: WebSocket Reconnection Logic
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2053-2070  
**What to Capture:**
```javascript
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

function reconnectWebSocket() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        updateConnectionStatus('Disconnected', 'error');
        showError('WebSocket connection failed. Using polling fallback.');
        return;
    }
    
    reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts - 1), 30000);
    
    setTimeout(() => {
        console.log(`Reconnecting WebSocket (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
        setupWebSocket();
    }, delay);
}
```

**Caption:** "Figure 6.27: WebSocket reconnection logic with exponential backoff strategy"

**Explanation:** This code screenshot shows the reconnection strategy (Section 3.4.3). When WebSocket disconnects, the system attempts reconnection with exponential backoff (1s, 2s, 4s, 8s, 16s, max 30s). After 5 failed attempts, it falls back to polling mode. This implements the reliability requirement (Section 4.3.2), ensuring the dashboard remains functional even under network instability.

### Screenshot 6.28: Face Encoding Storage Format
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 150-160  
**What to Capture:**
```python
# Generate face encoding
face_encodings = face_recognition.face_encodings(rgb_image)
if not face_encodings:
    raise HTTPException(status_code=400, detail="No face detected in the image")

face_encoding = face_encodings[0]  # 128-dimensional vector

# Store as JSON string (not raw binary)
db_student = Student(
    student_id=student.student_id,
    name=student.name,
    email=student.email,
    face_encoding=json.dumps(face_encoding.tolist()),  # Convert to JSON string
    photo_path=str(photo_path)
)
```

**Caption:** "Figure 6.28: Face encoding storage as JSON string for database compatibility"

**Explanation:** This code screenshot demonstrates the biometric data storage design (Section 5.3). The 128-dimensional NumPy array is converted to a Python list, then serialized to JSON string for database storage. This approach ensures database portability (SQLite/PostgreSQL compatible) and aligns with security requirements (Section 4.3.3) - storing abstract embeddings rather than raw images. The JSON format allows easy deserialization back to NumPy arrays for distance calculations.

### Screenshot 6.29: Kiosk UI - CHECKING State
**Type:** UI Screenshot  
**Location:** Kiosk window  
**What to Capture:**
- OpenCV window showing camera feed
- Yellow bounding box around detected face
- Status text: "Status: CHECKING" (yellow)
- Session ID displayed at top

**Caption:** "Figure 6.29: Kiosk interface showing liveness detection in CHECKING state"

**Explanation:** This UI screenshot demonstrates the liveness detection process (Section 6.2.1). The yellow bounding box indicates the system is analyzing the face but hasn't yet confirmed liveness. This occurs during the initial `MIN_FRAMES_FOR_LIVE = 5` frames or when liveness_score is being calculated. The color-coded feedback provides immediate visual indication of system state, meeting the GUI design requirement (Section 5.2.1).

### Screenshot 6.21: Kiosk UI - LIVE State
**Type:** UI Screenshot  
**Location:** Kiosk window  
**What to Capture:**
- Green bounding box around face
- Status text: "Status: LIVE" (green)
- Face clearly visible
- Ready for recognition

**Caption:** "Figure 6.30: Kiosk interface confirming liveness with green bounding box"

**Explanation:** This UI screenshot shows successful liveness confirmation (Section 6.2.1). The green bounding box indicates the subject has passed all liveness checks (depth, blink, movement). At this point, the system proceeds to face recognition. The green color provides positive feedback to the user, indicating they can proceed. This visual feedback minimizes friction in the check-in process (Section 5.2.1).

### Screenshot 6.22: Kiosk UI - FAKE State
**Type:** UI Screenshot  
**Location:** Kiosk window  
**What to Capture:**
- Red bounding box around detected face
- Status text: "Status: FAKE" (red)
- Message: "Check-in blocked: FAKE face detected"
- Photo/video visible in frame

**Caption:** "Figure 6.31: Kiosk interface blocking spoof attempt with red bounding box"

**Explanation:** This UI screenshot demonstrates the anti-spoofing mechanism (Section 6.2.2). The red bounding box and error message indicate a presentation attack was detected. The system has determined the face lacks sufficient depth variance, blink patterns, or movement. Recognition is blocked, and no API call is made. This visual feedback informs users (or attackers) that the attempt failed, implementing the security feedback loop mentioned in Section 6.2.2.

### Screenshot 6.23: Kiosk UI - Recognition Success
**Type:** UI Screenshot  
**Location:** Kiosk window  
**What to Capture:**
- Green bounding box around face
- Green text above face: "Welcome [Student Name]!"
- Status: "Status: LIVE"
- Success message displayed

**Caption:** "Figure 6.23: Kiosk interface showing successful face recognition"

**Explanation:** This UI screenshot demonstrates successful end-to-end verification (Section 6.2). The system has confirmed liveness (green box), performed face recognition, matched the student, and displayed the welcome message. This completes the verification pipeline: liveness detection → face encoding → matching → attendance record creation. The immediate visual feedback ensures a frictionless user experience (Section 4.3.1).

### Screenshot 6.24: Dashboard Real-Time Update
**Type:** UI Screenshot  
**Location:** Browser - Dashboard  
**What to Capture:**
- Dashboard before check-in (0 Present)
- Dashboard immediately after check-in (1 Present, updated list)
- New attendance record visible with timestamp
- Statistics updated

**Caption:** "Figure 6.24: Dashboard real-time update via WebSocket after check-in"

**Explanation:** This UI screenshot demonstrates the real-time update capability (Section 3.4.3). The dashboard updates instantly when a student checks in, without page refresh. The WebSocket connection receives the attendance_update message and refreshes the attendance list. This provides immediate feedback to lecturers, enabling situational awareness during class. The update happens asynchronously, meeting the non-functional requirement of low-latency processing (Section 4.3.1).

### Screenshot 6.25: Dashboard Analytics Charts
**Type:** UI Screenshot  
**Location:** Browser - Dashboard Analytics section  
**What to Capture:**
- Attendance Trend line chart (Chart.js)
- Status Distribution pie chart
- Attendance by Status bar chart
- All charts populated with data

**Caption:** "Figure 6.25: Dashboard analytics visualizations using Chart.js library"

**Explanation:** This UI screenshot demonstrates Objective 4 (Section 2.3.4) - the comprehensive management dashboard. Chart.js (v4.4.0) renders HTML5 Canvas-based visualizations showing attendance trends, status distributions, and hourly patterns. These charts transform raw biometric data into actionable insights for academic staff, enabling data-driven decision making. The visualizations update dynamically as new check-ins occur.

---

## Section 7: Evaluation and Conclusion

### Screenshot 7.1: Test Results - Unit Tests
**Type:** Terminal Screenshot  
**Location:** Terminal after running tests  
**What to Capture:**
```
Ran 21 tests in 0.023s

OK
```

**Caption:** "Figure 7.1: Unit test results showing 21/21 tests passed (Section 6.3.1)"

**Explanation:** This screenshot demonstrates the testing methodology (Section 6.3.1). The test suite achieves 100% pass rate, validating the reliability of the attendance calculation engine. All 21 tests complete in under 0.1 seconds, demonstrating the efficiency of in-memory testing without database overhead.

### Screenshot 7.2: Confusion Matrix
**Type:** Table/Chart Screenshot  
**Location:** Evaluation results  
**What to Capture:**
- Confusion matrix table showing TP, FP, FN, TN
- Or confusion matrix visualization

**Caption:** "Figure 7.2: Confusion matrix summarizing classification performance (Section 7.2.1)"

**Explanation:** This screenshot presents the experimental results (Section 7.2.1). The confusion matrix shows True Positives (genuine users correctly identified), False Negatives (genuine users rejected), True Negatives (spoofs correctly blocked), and False Positives (spoofs bypassed). This matrix is the foundation for calculating Precision, Recall, F1-Score, FAR, and FRR metrics.

### Screenshot 7.3: Performance Metrics Table
**Type:** Table Screenshot  
**Location:** Evaluation results  
**What to Capture:**
- Table showing:
  - Precision: [value]
  - Recall: [value]
  - F1-Score: [value]
  - FAR: [value]%
  - FRR: [value]%

**Caption:** "Figure 7.3: Performance metrics derived from confusion matrix (Section 7.2.2)"

**Explanation:** This screenshot presents the quantitative results (Section 7.2.2). The metrics validate the system's performance against requirements: Precision measures reliability of positive identification, Recall measures ability to recognize valid users, F1-Score is the primary figure of merit, FAR (should be <1% per Section 4.3.2) measures spoof acceptance, and FRR measures false rejections. These metrics demonstrate achievement of Objective 1 (Section 2.3.1).

### Screenshot 7.4: Latency Breakdown Chart
**Type:** Chart Screenshot  
**Location:** Performance analysis  
**What to Capture:**
- Bar chart or table showing:
  - Liveness Inference: ~45ms
  - Vector Generation: ~800ms
  - Network & Database I/O: ~300ms
  - Total: ~1.15 seconds

**Caption:** "Figure 7.4: Latency decomposition showing system meets <2s requirement (Section 7.2.3)"

**Explanation:** This screenshot demonstrates performance analysis (Section 7.2.3). The latency breakdown shows each component's contribution to total processing time. The system meets the non-functional requirement of <2 seconds total processing time (Section 4.3.1). The decomposition helps identify bottlenecks and validates the architectural decision to perform liveness detection at the edge (reducing server load).

---

## Section 8: Appendix

### Screenshot 8.1: Complete System Architecture
**Type:** Diagram Screenshot  
**Location:** Architecture diagram  
**What to Capture:**
- Client-Server architecture diagram
- Showing Kiosk → API → Database flow
- Web Dashboard connection

**Caption:** "Figure 8.1: Complete system architecture diagram (Section 5.1)"

**Explanation:** This diagram provides a high-level overview of the system architecture (Section 5.1), showing the tripartite topology: Presentation Layer (Kiosk and Web Dashboard), Application Layer (FastAPI), and Data Persistence Layer (Database). The diagram illustrates the separation of concerns and data flow between components.

### Screenshot 8.2: Database Schema Diagram
**Type:** ER Diagram Screenshot  
**Location:** Database design document  
**What to Capture:**
- ER diagram showing:
  - Students table
  - Sessions table
  - AttendanceRecords table
  - Courses table
  - Relationships (Foreign Keys)

**Caption:** "Figure 8.2: Database schema diagram showing normalized design (Section 5.3)"

**Explanation:** This diagram illustrates the database schema design (Section 5.3), showing all entities, their attributes, and relationships. The diagram demonstrates Third Normal Form (3NF) normalization, with Foreign Key constraints ensuring referential integrity. This visual representation complements the code screenshots in Section 5.3.

### Screenshot 8.3: Complete Enrollment Workflow
**Type:** UI Screenshot Sequence  
**Location:** Browser - Complete enrollment process  
**What to Capture:**
- Step 1: Click "Enroll Student"
- Step 2: Fill form with student info
- Step 3: Upload photo
- Step 4: Photo preview
- Step 5: Success message
- Step 6: Student appears in list

**Caption:** "Figure 8.3: Complete student enrollment workflow (Section 4.2)"

**Explanation:** This screenshot sequence demonstrates the Enrollment domain functional requirement (Section 4.2) in action. The workflow shows how academic staff register students through the administrative interface, capturing multiple reference images and generating face encodings. This visual guide complements the code explanation in Section 6.11.

### Screenshot 8.4: Complete Check-In Workflow
**Type:** UI Screenshot Sequence  
**Location:** Kiosk and Dashboard  
**What to Capture:**
- Step 1: Kiosk showing CHECKING (yellow)
- Step 2: Kiosk showing LIVE (green)
- Step 3: Kiosk showing "Welcome [Name]!"
- Step 4: Dashboard updating in real-time
- Step 5: Attendance record appears

**Caption:** "Figure 8.4: Complete check-in workflow demonstrating end-to-end system operation"

**Explanation:** This screenshot sequence demonstrates the complete verification pipeline (Section 6.2): liveness detection → face recognition → attendance recording → real-time dashboard update. The sequence shows how the system processes a student check-in from initial face detection through to database persistence and dashboard notification, validating all four project objectives.

### Screenshot 8.5: API Documentation (Swagger UI)
**Type:** UI Screenshot  
**Location:** Browser - `http://localhost:8000/docs`  
**What to Capture:**
- FastAPI automatic Swagger documentation
- All endpoints listed
- Request/response schemas visible
- Try-it-out functionality

**Caption:** "Figure 8.5: FastAPI automatic API documentation (Section 5.1.2)"

**Explanation:** This screenshot demonstrates FastAPI's automatic OpenAPI documentation feature. The Swagger UI provides interactive API documentation, showing all endpoints, request/response models, and allowing API testing. This documentation is automatically generated from the code, ensuring it stays synchronized with the implementation. This supports the maintainability requirement (Section 4.3.4).

---

## Additional Screenshots - Extended Implementation Details

### Screenshot 6.35: Health Check Endpoint
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 77-100  
**Location:** Section 6.3.1 - API Endpoints

**What to Capture:**
```python
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    # Check if using MongoDB
    use_mongodb = os.getenv("USE_MONGODB", "false").lower() == "true" or os.getenv("MONGODB_URL")
    
    if use_mongodb:
        # Initialize MongoDB indexes
        try:
            from src.database.database_mongodb import create_indexes
            create_indexes()
        except ImportError:
            pass
    else:
        # Create SQL tables
        create_tables()
```

**Caption:** "Figure 6.35: Health check endpoint and startup event handler (Section 6.3.1)"

**Explanation:** This screenshot shows the health check endpoint used for system monitoring and the startup event handler that initializes the database. The health check endpoint allows monitoring tools to verify API availability, while the startup event ensures database tables are created before handling requests. This demonstrates proper application lifecycle management in FastAPI.

---

### Screenshot 6.36: Start and Stop Session Endpoints
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 247-273  
**Location:** Section 6.3.2 - Session Management

**What to Capture:**
```python
@app.post("/api/sessions/{session_id}/start")
async def start_session(session_id: int, db: Session = Depends(get_db)):
    """Start an attendance session"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = True
    session.actual_start = datetime.utcnow()
    db.commit()
    
    return {"message": "Session started successfully"}

@app.post("/api/sessions/{session_id}/stop")
async def stop_session(session_id: int, db: Session = Depends(get_db)):
    """Stop an attendance session"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    session.actual_end = datetime.utcnow()
    db.commit()
    
    return {"message": "Session stopped successfully"}
```

**Caption:** "Figure 6.36: Session start and stop endpoints with timestamp tracking (Section 6.3.2)"

**Explanation:** These endpoints control session lifecycle, setting the `is_active` flag and recording actual start/end times. The implementation demonstrates proper state management and timestamp tracking for audit purposes. The `actual_start` and `actual_end` fields allow comparison with scheduled times for attendance analysis.

---

### Screenshot 6.37: Get Session Attendance Endpoint
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 275-298  
**Location:** Section 6.3.3 - Attendance Retrieval

**What to Capture:**
```python
@app.get("/api/sessions/{session_id}/attendance", response_model=List[AttendanceResponse])
async def get_session_attendance(session_id: int, db: Session = Depends(get_db)):
    """Get attendance records for a session"""
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id
    ).all()
    
    return [
        AttendanceResponse(
            id=record.id,
            student=StudentResponse(
                id=record.student.id,
                student_id=record.student.student_id,
                name=record.student.name,
                email=record.student.email,
                is_active=record.student.is_active,
                created_at=record.student.created_at
            ),
            check_in_time=record.check_in_time,
            confidence_score=record.confidence_score,
            status=record.status
        ) for record in attendance_records
    ]
```

**Caption:** "Figure 6.37: Attendance retrieval endpoint with nested response models (Section 6.3.3)"

**Explanation:** This endpoint retrieves all attendance records for a session, using SQLAlchemy relationships to join Student data. The response model demonstrates nested Pydantic models (`AttendanceResponse` containing `StudentResponse`), ensuring type safety and automatic API documentation. This pattern allows efficient data retrieval while maintaining clean separation of concerns.

---

### Screenshot 6.38: Enrollment Script - Image Processing
**Type:** Code Screenshot  
**File:** `src/scripts/enroll.py`  
**Lines:** 8-43  
**Location:** Section 6.4.1 - Enrollment Scripts

**What to Capture:**
```python
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
```

**Caption:** "Figure 6.38: Enrollment script image processing and API communication (Section 6.4.1)"

**Explanation:** This script demonstrates batch enrollment capabilities, processing multiple images per student. The function reads images using OpenCV, encodes them to base64 for API transmission, and handles errors gracefully. This utility script enables efficient bulk enrollment operations, supporting the administrative workflow requirement (Section 4.2).

---

### Screenshot 6.39: Enrollment Script - Multiple Image Handling
**Type:** Code Screenshot  
**File:** `src/scripts/enroll.py`  
**Lines:** 45-132  
**Location:** Section 6.4.1 - Enrollment Scripts

**What to Capture:**
```python
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
```

**Caption:** "Figure 6.39: Enrollment script main function with flexible image input handling (Section 6.4.1)"

**Explanation:** This main function demonstrates robust input handling, supporting directory-based, comma-separated, or interactive image path entry. The script validates paths, enforces the 3-5 image requirement, and provides progress feedback. This implementation supports the multiple reference images requirement (Section 4.2.1) and demonstrates error handling and user feedback best practices.

---

### Screenshot 6.40: Session Management Script - Course Creation
**Type:** Code Screenshot  
**File:** `src/scripts/start_session.py`  
**Lines:** 16-37  
**Location:** Section 6.4.2 - Session Management Scripts

**What to Capture:**
```python
def create_course(course_code, course_name, lecturer_name, description=None, api_url="http://localhost:8000"):
    """Create a new course"""
    course_data = {
        "course_code": course_code,
        "course_name": course_name,
        "lecturer_name": lecturer_name
    }
    if description:
        course_data["description"] = description
    
    try:
        response = requests.post(f"{api_url}/api/courses", json=course_data)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Course created: {result['course_code']} - {result['course_name']}")
            return result['id']
        else:
            print(f"[ERROR] Error creating course: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        return None
```

**Caption:** "Figure 6.40: Course creation function in session management script (Section 6.4.2)"

**Explanation:** This function demonstrates the course creation workflow, handling optional description fields and providing clear success/error feedback. The function returns the course ID for use in session creation, demonstrating proper workflow chaining. This supports the course management requirement (Section 4.2.2).

---

### Screenshot 6.41: Session Management Script - Session Creation
**Type:** Code Screenshot  
**File:** `src/scripts/start_session.py`  
**Lines:** 39-61  
**Location:** Section 6.4.2 - Session Management Scripts

**What to Capture:**
```python
def create_session(course_id, session_name, scheduled_start, scheduled_end, room_location=None, api_url="http://localhost:8000"):
    """Create a new attendance session"""
    session_data = {
        "course_id": course_id,
        "session_name": session_name,
        "scheduled_start": scheduled_start.isoformat(),
        "scheduled_end": scheduled_end.isoformat()
    }
    if room_location:
        session_data["room_location"] = room_location
    
    try:
        response = requests.post(f"{api_url}/api/sessions", json=session_data)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Session created: {result['session_name']} (ID: {result['id']})")
            return result['id']
        else:
            print(f"[ERROR] Error creating session: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        return None
```

**Caption:** "Figure 6.41: Session creation function with datetime serialization (Section 6.4.2)"

**Explanation:** This function creates attendance sessions with scheduled times and optional room location. The datetime objects are serialized to ISO format for JSON transmission, demonstrating proper API communication patterns. The function returns the session ID for subsequent operations like starting the session.

---

### Screenshot 6.42: AttendanceTracker - Mark Present/Absent Methods
**Type:** Code Screenshot  
**File:** `src/api/attendance_tracker.py`  
**Lines:** 34-58  
**Location:** Section 6.5.1 - Attendance Tracking Core

**What to Capture:**
```python
def mark_present(self, student_id: str) -> None:
    """Mark a student as present.

    Raises ValueError if the student is not in the roster.
    """
    if student_id not in self.roster:
        raise ValueError(f"Student '{student_id}' is not in the class roster.")
    self.present_students.add(student_id)

def mark_absent(self, student_id: str) -> None:
    """Mark a student as absent (remove present flag).

    Raises ValueError if the student is not in the roster.
    """
    if student_id not in self.roster:
        raise ValueError(f"Student '{student_id}' is not in the roster.")
    self.present_students.discard(student_id)

def clear(self) -> None:
    """Clear all present marks for a fresh session."""
    self.present_students.clear()

def get_absent_students(self) -> Set[str]:
    """Return set of students in roster but not marked present."""
    return self.roster - self.present_students

def get_attendance_list(self) -> List[str]:
    """Return a sorted list of present student IDs."""
    return sorted(self.present_students)
```

**Caption:** "Figure 6.42: AttendanceTracker core methods with roster validation (Section 6.5.1)"

**Explanation:** These methods form the core of the attendance tracking system, using Python sets for efficient membership testing. The `mark_present` and `mark_absent` methods validate against the roster, preventing invalid operations. The `get_absent_students` method uses set difference for efficient computation, demonstrating algorithmic efficiency.

---

### Screenshot 6.43: AttendanceTracker - Persistence Methods
**Type:** Code Screenshot  
**File:** `src/api/attendance_tracker.py`  
**Lines:** 74-144  
**Location:** Section 6.5.2 - Data Persistence

**What to Capture:**
```python
def to_dict(self) -> Dict[str, List[str]]:
    """Serialize to a plain dict.

    Format: {"roster": [...], "present": [...]} with lists of IDs.
    """
    return {"roster": sorted(self.roster), "present": sorted(self.present_students)}

@classmethod
def from_dict(cls, data: Dict[str, Iterable[str]]) -> "AttendanceTracker":
    """Create an AttendanceTracker from a dict produced by `to_dict`."""
    roster = data.get("roster", [])
    present = set(data.get("present", []))
    at = cls(roster)
    # only keep present IDs that are in the roster
    at.present_students = {s for s in present if s in at.roster}
    return at

def save_json(self, path: Union[str, Path]) -> None:
    """Save tracker state to a JSON file.

    The JSON contains the `roster` and the `present` lists.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

@classmethod
def load_json(cls, path: Union[str, Path]) -> "AttendanceTracker":
    """Load tracker state from a JSON file."""
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return cls.from_dict(data)

def save_csv(self, path: Union[str, Path]) -> None:
    """Save attendance to CSV with columns: id,present

    present column will be '1' for present, '0' for absent.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "present"])
        for sid in sorted(self.roster):
            writer.writerow([sid, "1" if sid in self.present_students else "0"])
```

**Caption:** "Figure 6.43: AttendanceTracker persistence methods supporting JSON and CSV formats (Section 6.5.2)"

**Explanation:** These methods provide flexible data persistence, supporting both JSON (for programmatic use) and CSV (for spreadsheet compatibility) formats. The `from_dict` method includes validation to ensure loaded present students are in the roster, maintaining data integrity. The CSV format uses binary encoding ('1'/'0') for present/absent status, enabling easy analysis in spreadsheet applications.

---

### Screenshot 6.44: Kiosk Session Selection
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 426-450  
**Location:** Section 6.6.1 - Session Management

**What to Capture:**
```python
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
                print("No active sessions available. Please start a session from the dashboard.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sessions: {e}")
```

**Caption:** "Figure 6.44: Kiosk session selection with active session filtering (Section 6.6.1)"

**Explanation:** This method allows the kiosk operator to select an active session interactively. The function fetches all sessions from the API, filters for active ones, and presents them in a numbered list. This demonstrates proper error handling for network failures and invalid user input, ensuring robust operation in production environments.

---

### Screenshot 6.45: Kiosk Snapshot Saving
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 409-424  
**Location:** Section 6.6.2 - Audit Trail

**What to Capture:**
```python
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
```

**Caption:** "Figure 6.45: Snapshot saving functionality for audit trail (Section 6.6.2)"

**Explanation:** This method saves face snapshots for audit purposes, using UTC timestamps and sanitized labels in filenames. The optional feature can be toggled via `save_snapshots` flag, allowing operators to enable/disable based on privacy requirements. The snapshots provide evidence for attendance disputes and system debugging.

---

### Screenshot 6.46: Frontend - Load Attendance Records Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1500-1550 (approximate)  
**Location:** Section 6.7.1 - Dashboard Data Loading

**What to Capture:**
```javascript
async function loadAttendanceRecords() {
    if (!currentSessionId) {
        document.getElementById('attendance-list').innerHTML = '<div class="empty-state">No session selected</div>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/sessions/${currentSessionId}/attendance`);
        const records = await response.json();
        
        // Update attendance list
        const container = document.getElementById('attendance-list');
        if (records.length === 0) {
            container.innerHTML = '<div class="empty-state">No attendance records yet</div>';
            return;
        }
        
        container.innerHTML = records.map(record => `
            <div class="attendance-item">
                <div class="student-info">
                    <strong>${record.student.name}</strong>
                    <span class="student-id">${record.student.student_id}</span>
                </div>
                <div class="check-in-info">
                    <span class="time">${new Date(record.check_in_time).toLocaleString()}</span>
                    <span class="confidence">Confidence: ${(record.confidence_score * 100).toFixed(1)}%</span>
                </div>
            </div>
        `).join('');
        
        // Update statistics
        updateAttendanceStats(records);
        
        // Update chart
        updateAttendanceChart(records);
    } catch (error) {
        console.error('Error loading attendance:', error);
        showError('Failed to load attendance records');
    }
}
```

**Caption:** "Figure 6.46: Frontend function for loading and displaying attendance records (Section 6.7.1)"

**Explanation:** This function demonstrates the frontend's data fetching and rendering logic. It handles empty states, formats timestamps for display, and updates multiple UI components (list, statistics, charts) after fetching data. The function uses async/await for clean asynchronous code and includes error handling with user-friendly error messages.

---

### Screenshot 6.47: Frontend - Export to Excel Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2000-2050 (approximate)  
**Location:** Section 6.7.2 - Data Export

**What to Capture:**
```javascript
function exportToExcel() {
    if (!currentSessionId) {
        showToast('Please select a session first', 'warning');
        return;
    }
    
    fetch(`${API_BASE_URL}/api/sessions/${currentSessionId}/attendance`)
        .then(response => response.json())
        .then(records => {
            const data = records.map(record => ({
                'Student ID': record.student.student_id,
                'Name': record.student.name,
                'Email': record.student.email,
                'Check-in Time': new Date(record.check_in_time).toLocaleString(),
                'Confidence Score': (record.confidence_score * 100).toFixed(2) + '%',
                'Status': record.status
            }));
            
            const ws = XLSX.utils.json_to_sheet(data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Attendance');
            
            const sessionName = document.getElementById('session-select').selectedOptions[0].text;
            const filename = `attendance_${sessionName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.xlsx`;
            
            XLSX.writeFile(wb, filename);
            showToast('Attendance exported successfully', 'success');
        })
        .catch(error => {
            console.error('Export error:', error);
            showError('Failed to export attendance');
        });
}
```

**Caption:** "Figure 6.47: Excel export functionality using SheetJS library (Section 6.7.2)"

**Explanation:** This function demonstrates data export capabilities, converting attendance records to Excel format using the SheetJS (XLSX) library. The function formats data appropriately, creates a workbook with a named sheet, and generates a filename with session name and date. This supports the reporting requirement (Section 4.2.4) and enables offline analysis.

---

### Screenshot 6.48: Frontend - Theme Management
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1183-1207  
**Location:** Section 6.7.3 - UI Enhancements

**What to Capture:**
```javascript
// Theme Management
function initializeTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    const text = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    if (themeToggleBtn) themeToggleBtn.innerHTML = icon;
    if (themeIcon) themeIcon.innerHTML = icon;
    if (themeText) themeText.textContent = text;
}
```

**Caption:** "Figure 6.48: Dark mode theme management with localStorage persistence (Section 6.7.3)"

**Explanation:** This code implements dark mode functionality using CSS custom properties (CSS variables) and the `data-theme` attribute. The theme preference is persisted in localStorage, ensuring the user's choice persists across sessions. The implementation demonstrates modern web development practices and improves user experience through accessibility features.

---

### Screenshot 6.49: Frontend - Toast Notification System
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1255-1281  
**Location:** Section 6.7.4 - User Feedback

**What to Capture:**
```javascript
// Toast Notifications
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        error: '<i class="fas fa-exclamation-circle"></i>',
        warning: '<i class="fas fa-exclamation-triangle"></i>',
        info: '<i class="fas fa-info-circle"></i>'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <div class="toast-content">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
```

**Caption:** "Figure 6.49: Toast notification system with animated dismiss (Section 6.7.4)"

**Explanation:** This function creates user-friendly toast notifications with different types (success, error, warning, info) and corresponding icons. The notifications auto-dismiss after a configurable duration with smooth animations. This provides immediate feedback for user actions, improving the overall user experience and supporting the usability requirement (Section 4.3.3).

---

### Screenshot 6.50: Frontend - Session List Display
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1376-1424  
**Location:** Section 6.7.5 - Session Management UI

**What to Capture:**
```javascript
// Display sessions list
function displaySessionsList(sessions) {
    const container = document.getElementById('sessions-list');
    if (sessions.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon"><i class="fas fa-calendar-alt"></i></div><p>No sessions found. Create your first session!</p></div>';
        return;
    }
    container.innerHTML = sessions.map(session => {
        const status = session.is_active ? 'active' : 
                      new Date(session.scheduled_start) > new Date() ? 'scheduled' : 'completed';
        const statusText = session.is_active ? 'Active' : 
                          new Date(session.scheduled_start) > new Date() ? 'Scheduled' : 'Completed';
        return `
            <div class="session-card" onclick="toggleSessionDetails(${session.id})" data-status="${status}">
                <div class="session-info">
                    <div class="session-name">${session.session_name}</div>
                    <div class="session-id">Course: ${session.course.course_name} | ID: ${session.id}</div>
                    <div style="margin-top: 5px; font-size: 0.9em; color: #666;">
                        <i class="fas fa-calendar-alt"></i> ${new Date(session.scheduled_start).toLocaleString()} - ${new Date(session.scheduled_end).toLocaleString()}
                    </div>
                    ${session.room_location ? `<div style="font-size: 0.9em; color: #666;"><i class="fas fa-map-marker-alt"></i> ${session.room_location}</div>` : ''}
                </div>
                <div>
                    <span class="status-badge status-${status}">${statusText}</span>
                </div>
                <div class="session-details" id="session-details-${session.id}">
                    <div class="session-actions">
                        <button class="btn btn-success btn-sm" onclick="event.stopPropagation(); startSessionById(${session.id})" ${session.is_active ? 'disabled' : ''}><i class="fas fa-play"></i> Start</button>
                        <button class="btn btn-danger btn-sm" onclick="event.stopPropagation(); stopSessionById(${session.id})" ${!session.is_active ? 'disabled' : ''}><i class="fas fa-stop"></i> Stop</button>
                        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); selectSession(${session.id})"><i class="fas fa-eye"></i> View Attendance</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}
```

**Caption:** "Figure 6.50: Session list rendering with status badges and action buttons (Section 6.7.5)"

**Explanation:** This function renders session cards with dynamic status determination based on `is_active` flag and scheduled times. The function includes conditional rendering for optional fields (room location) and disables action buttons based on session state. This demonstrates proper state management and user interface design, ensuring users can only perform valid actions.

---

### Screenshot 6.51: Requirements.txt - Complete Dependency List
**Type:** Code Screenshot  
**File:** `requirements.txt`  
**Lines:** 1-22  
**Location:** Section 6.1.1 - Development Environment

**What to Capture:**
```
numpy>=1.24.0
pandas>=2.0.0
opencv-python>=4.8.0
dlib-bin>=19.24.0
face-recognition>=1.3.0
tensorflow>=2.13.0
deepface>=0.0.79
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
websockets>=12.0
aiofiles>=23.2.0
requests>=2.32.5
mediapipe>=0.10.0
pymongo>=4.6.0
motor>=3.3.0
python-dotenv>=1.0.0
```

**Caption:** "Figure 6.51: Complete Python dependency list with version constraints (Section 6.1.1)"

**Explanation:** This file lists all project dependencies with minimum version requirements. The dependencies cover computer vision (OpenCV, face_recognition, MediaPipe), web framework (FastAPI, uvicorn), database (SQLAlchemy, psycopg2, pymongo), and utility libraries. Version constraints ensure reproducible builds and compatibility across development environments.

---

### Screenshot 6.52: List Sessions Endpoint with Course Joins
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 218-240  
**Location:** Section 6.3.2 - Session Management

**What to Capture:**
```python
# List sessions with course info
@app.get("/api/sessions")
async def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(Session).all()
    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "session_name": s.session_name,
            "scheduled_start": s.scheduled_start.isoformat() if s.scheduled_start else None,
            "scheduled_end": s.scheduled_end.isoformat() if s.scheduled_end else None,
            "actual_start": s.actual_start.isoformat() if s.actual_start else None,
            "actual_end": s.actual_end.isoformat() if s.actual_end else None,
            "room_location": s.room_location,
            "is_active": s.is_active,
            "course": {
                "id": s.course.id if s.course else None,
                "course_code": s.course.course_code if s.course else None,
                "course_name": s.course.course_name if s.course else None,
                "lecturer_name": s.course.lecturer_name if s.course else None
            }
        })
    return result
```

**Caption:** "Figure 6.52: Session listing endpoint with nested course information (Section 6.3.2)"

**Explanation:** This endpoint demonstrates SQLAlchemy relationship navigation, joining Session and Course data through the foreign key relationship. The function handles nullable relationships and serializes datetime objects to ISO format strings for JSON compatibility. This pattern provides complete session information in a single API call, reducing frontend complexity.

---

### Screenshot 6.53: Kiosk Frame Processing Loop
**Type:** Code Screenshot  
**File:** `src/api/kiosk_app.py`  
**Lines:** 180-238  
**Location:** Section 6.6.3 - Main Processing Loop

**What to Capture:**
```python
while True:
    ret, frame = self.cap.read()
    if not ret:
        # Handle camera read failures
        failed_reads += 1
        if failed_reads > 10:
            logging.error("Camera read failed multiple times. Stopping.")
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
```

**Caption:** "Figure 6.53: Main kiosk processing loop with keyboard controls (Section 6.6.3)"

**Explanation:** This main loop demonstrates robust camera handling with failure recovery, frame processing with error handling, and interactive keyboard controls. The loop supports session selection ('s'), session refresh ('r'), snapshot toggle ('t'), and graceful shutdown ('q'). The implementation includes proper resource cleanup (camera release, window destruction) ensuring no resource leaks.

---

### Screenshot 6.54: Frontend - Update Statistics Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1703-1713  
**Location:** Section 6.7.6 - Statistics Calculation

**What to Capture:**
```javascript
// Update statistics
function updateStats(records) {
    const totalStudents = records.length;
    const presentCount = records.filter(r => r.status === 'present').length;
    const absentCount = totalStudents - presentCount;
    const attendanceRate = totalStudents > 0 ? Math.round((presentCount / totalStudents) * 100) : 0;

    document.getElementById('total-students').textContent = totalStudents;
    document.getElementById('present-count').textContent = presentCount;
    document.getElementById('absent-count').textContent = absentCount;
    document.getElementById('attendance-rate').textContent = attendanceRate + '%';
}
```

**Caption:** "Figure 6.54: Statistics calculation function updating dashboard metrics (Section 6.7.6)"

**Explanation:** This function computes real-time attendance statistics from records, calculating total students, present/absent counts, and attendance rate percentage. The function uses JavaScript array filtering and updates DOM elements dynamically, demonstrating reactive UI updates based on data changes.

---

### Screenshot 6.55: Frontend - Create Session Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1733-1765  
**Location:** Section 6.7.7 - Session Creation

**What to Capture:**
```javascript
// Create session
async function createSession(event) {
    event.preventDefault();
    const formData = {
        course_id: parseInt(document.getElementById('session-course-id').value),
        session_name: document.getElementById('session-name').value,
        scheduled_start: new Date(document.getElementById('session-start').value).toISOString(),
        scheduled_end: new Date(document.getElementById('session-end').value).toISOString(),
        room_location: document.getElementById('session-room').value || null
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            closeModal('create-session-modal');
            showSuccess('Session created successfully!');
            loadSessions();
            if (document.getElementById('sessions-tab').classList.contains('active')) {
                loadSessionsList();
            }
            document.getElementById('create-session-form').reset();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to create session');
        }
    } catch (error) {
        showError('Failed to create session: ' + error.message);
    }
}
```

**Caption:** "Figure 6.55: Session creation function with form data serialization (Section 6.7.7)"

**Explanation:** This async function handles session creation from the frontend, collecting form data, converting dates to ISO format, and sending a POST request to the API. The function includes error handling, success notifications, and UI updates, demonstrating proper async/await patterns and user feedback mechanisms.

---

### Screenshot 6.56: Frontend - Enroll Student Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1768-1814  
**Location:** Section 6.7.8 - Student Enrollment

**What to Capture:**
```javascript
// Enroll student
async function enrollStudent(event) {
    event.preventDefault();
    if (selectedPhotos.length < 3) {
        showError('Please upload at least 3 photos');
        return;
    }

    const studentId = document.getElementById('student-id').value;
    const studentName = document.getElementById('student-name').value;
    const studentEmail = document.getElementById('student-email').value;

    try {
        // Enroll with first photo, then add additional photos
        for (let i = 0; i < selectedPhotos.length; i++) {
            const photo = selectedPhotos[i];
            const base64 = await fileToBase64(photo);
            
            const response = await fetch(`${API_BASE_URL}/api/students/enroll`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: studentId,
                    name: studentName,
                    email: studentEmail,
                    photo_base64: base64
                })
            });

            if (!response.ok && i === 0) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to enroll student');
            }
        }

        closeModal('enroll-student-modal');
        showSuccess('Student enrolled successfully!');
        loadStudents();
        if (document.getElementById('students-tab').classList.contains('active')) {
            loadStudentsList();
        }
        selectedPhotos = [];
        document.getElementById('photo-preview').innerHTML = '';
        document.getElementById('enroll-student-form').reset();
    } catch (error) {
        showError('Failed to enroll student: ' + error.message);
    }
}
```

**Caption:** "Figure 6.56: Student enrollment function with multiple photo processing (Section 6.7.8)"

**Explanation:** This function handles student enrollment with multiple photos, validating minimum photo count, converting files to base64, and sending sequential API requests. The implementation demonstrates batch processing, file handling, and proper error handling for the first enrollment attempt.

---

### Screenshot 6.57: Frontend - Photo Preview Functions
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1852-1885  
**Location:** Section 6.7.9 - File Handling

**What to Capture:**
```javascript
// Photo preview
function previewPhotos(event) {
    const files = Array.from(event.target.files);
    selectedPhotos = files;
    const preview = document.getElementById('photo-preview');
    preview.innerHTML = '';

    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const div = document.createElement('div');
            div.className = 'photo-preview-item';
            div.innerHTML = `
                <img src="${e.target.result}" alt="Preview ${index + 1}">
                <button type="button" class="remove-photo" onclick="removePhoto(${index})">×</button>
            `;
            preview.appendChild(div);
        };
        reader.readAsDataURL(file);
    });
}

function removePhoto(index) {
    selectedPhotos.splice(index, 1);
    previewPhotos({ target: { files: selectedPhotos } });
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
    });
}
```

**Caption:** "Figure 6.57: Photo preview and base64 conversion functions (Section 6.7.9)"

**Explanation:** These functions handle file preview and conversion: `previewPhotos` creates thumbnail previews using FileReader API, `removePhoto` allows removing individual photos, and `fileToBase64` converts files to base64 strings for API transmission. The implementation demonstrates modern browser file handling APIs and Promise-based async operations.

---

### Screenshot 6.58: Frontend - Start and Stop Session Functions
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1888-1939  
**Location:** Section 6.7.10 - Session Control

**What to Capture:**
```javascript
// Start session
async function startSession() {
    if (!currentSessionId) return;
    await startSessionById(currentSessionId);
}

async function startSessionById(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/start`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showSuccess('Session started successfully');
            loadSessions();
            if (document.getElementById('sessions-tab').classList.contains('active')) {
                loadSessionsList();
            }
            updateSessionControls();
        } else {
            showError('Failed to start session');
        }
    } catch (error) {
        showError('Failed to start session: ' + error.message);
    }
}

// Stop session
async function stopSession() {
    if (!currentSessionId) return;
    await stopSessionById(currentSessionId);
}

async function stopSessionById(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/stop`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showSuccess('Session stopped successfully');
            loadSessions();
            if (document.getElementById('sessions-tab').classList.contains('active')) {
                loadSessionsList();
            }
            updateSessionControls();
        } else {
            showError('Failed to stop session');
        }
    } catch (error) {
        showError('Failed to stop session: ' + error.message);
    }
}
```

**Caption:** "Figure 6.58: Session start and stop functions with UI updates (Section 6.7.10)"

**Explanation:** These functions control session lifecycle, calling API endpoints to start/stop sessions and updating the UI accordingly. The implementation demonstrates RESTful API patterns, error handling, and coordinated UI updates across multiple components (sessions list, controls, notifications).

---

### Screenshot 6.59: Frontend - Filter Functions
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2243-2289  
**Location:** Section 6.7.11 - Data Filtering

**What to Capture:**
```javascript
// Filtering functions
function filterSessions() {
    const search = document.getElementById('session-search').value.toLowerCase();
    const statusFilter = document.getElementById('session-status-filter').value;
    const courseFilter = document.getElementById('session-course-filter').value;

    let filtered = allSessions.filter(session => {
        const matchSearch = session.session_name.toLowerCase().includes(search) ||
                          session.course.course_name.toLowerCase().includes(search);
        const matchStatus = !statusFilter || 
            (statusFilter === 'active' && session.is_active) ||
            (statusFilter === 'scheduled' && new Date(session.scheduled_start) > new Date() && !session.is_active) ||
            (statusFilter === 'completed' && new Date(session.scheduled_end) < new Date() && !session.is_active);
        const matchCourse = !courseFilter || session.course_id === parseInt(courseFilter);
        return matchSearch && matchStatus && matchCourse;
    });

    displaySessionsList(filtered);
}

function filterStudents() {
    const search = document.getElementById('student-search').value.toLowerCase();
    const filtered = allStudents.filter(student => 
        student.name.toLowerCase().includes(search) ||
        student.student_id.toLowerCase().includes(search) ||
        student.email.toLowerCase().includes(search)
    );
    displayStudentsList(filtered);
}

function filterAttendance() {
    const search = document.getElementById('attendance-search').value.toLowerCase();
    const records = Array.from(document.querySelectorAll('.attendance-item'));
    records.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(search) ? '' : 'none';
    });
}
```

**Caption:** "Figure 6.59: Multi-criteria filtering functions for sessions, students, and attendance (Section 6.7.11)"

**Explanation:** These functions implement client-side filtering with multiple criteria: text search, status filtering, and course filtering. The `filterSessions` function demonstrates complex boolean logic for status determination based on dates and active flags, while `filterAttendance` uses DOM manipulation for real-time filtering without re-rendering.

---

### Screenshot 6.60: Frontend - Sort Attendance Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2291-2313  
**Location:** Section 6.7.12 - Data Sorting

**What to Capture:**
```javascript
function sortAttendance() {
    const sortBy = document.getElementById('attendance-sort').value;
    const container = document.getElementById('attendance-records');
    const items = Array.from(container.querySelectorAll('.attendance-item'));
    
    items.sort((a, b) => {
        const indexA = parseInt(a.dataset.index);
        const indexB = parseInt(b.dataset.index);
        const recordA = currentAttendanceRecords[indexA];
        const recordB = currentAttendanceRecords[indexB];
        
        if (sortBy === 'name') {
            return recordA.student.name.localeCompare(recordB.student.name);
        } else if (sortBy === 'time') {
            return new Date(recordA.check_in_time) - new Date(recordB.check_in_time);
        } else if (sortBy === 'status') {
            return recordA.status.localeCompare(recordB.status);
        }
        return 0;
    });
    
    items.forEach(item => container.appendChild(item));
}
```

**Caption:** "Figure 6.60: Attendance sorting function with multiple sort criteria (Section 6.7.12)"

**Explanation:** This function implements client-side sorting by name, time, or status. The function uses dataset attributes to maintain references to original data, sorts DOM elements, and re-appends them in sorted order. This demonstrates efficient DOM manipulation without full re-rendering.

---

### Screenshot 6.61: Frontend - Export CSV Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2316-2341  
**Location:** Section 6.7.13 - Data Export

**What to Capture:**
```javascript
function exportAttendanceCSV() {
    if (!currentAttendanceRecords || currentAttendanceRecords.length === 0) {
        showError('No attendance records to export');
        return;
    }

    const headers = ['Student ID', 'Name', 'Email', 'Check-in Time', 'Status', 'Confidence'];
    const rows = currentAttendanceRecords.map(r => [
        r.student.student_id,
        r.student.name,
        r.student.email,
        new Date(r.check_in_time).toLocaleString(),
        r.status,
        r.confidence_score ? (r.confidence_score * 100).toFixed(2) + '%' : 'N/A'
    ]);

    const csv = [headers.join(','), ...rows.map(r => r.map(c => `"${c}"`).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_${currentSessionId}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    showSuccess('CSV exported successfully!');
}
```

**Caption:** "Figure 6.61: CSV export function with blob creation and download (Section 6.7.13)"

**Explanation:** This function generates CSV data from attendance records, creates a Blob object, and triggers browser download using URL.createObjectURL. The implementation demonstrates proper CSV formatting with quoted fields, date formatting, and memory cleanup via URL.revokeObjectURL.

---

### Screenshot 6.62: Frontend - Export Excel Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2343-2366  
**Location:** Section 6.7.13 - Data Export

**What to Capture:**
```javascript
function exportAttendanceExcel() {
    if (!currentAttendanceRecords || currentAttendanceRecords.length === 0) {
        showError('No attendance records to export');
        return;
    }

    const data = [
        ['Student ID', 'Name', 'Email', 'Check-in Time', 'Status', 'Confidence'],
        ...currentAttendanceRecords.map(r => [
            r.student.student_id,
            r.student.name,
            r.student.email,
            new Date(r.check_in_time).toLocaleString(),
            r.status,
            r.confidence_score ? (r.confidence_score * 100).toFixed(2) + '%' : 'N/A'
        ])
    ];

    const ws = XLSX.utils.aoa_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Attendance');
    XLSX.writeFile(wb, `attendance_${currentSessionId}_${new Date().toISOString().split('T')[0]}.xlsx`);
    showSuccess('Excel file exported successfully!');
}
```

**Caption:** "Figure 6.62: Excel export function using SheetJS library (Section 6.7.13)"

**Explanation:** This function uses the SheetJS (XLSX) library to create Excel workbooks, converting attendance data to worksheet format. The implementation demonstrates library integration, workbook creation, and file generation with proper naming conventions.

---

### Screenshot 6.63: Frontend - Manual Entry Functions
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2369-2428  
**Location:** Section 6.7.14 - Manual Operations

**What to Capture:**
```javascript
// Manual entry
function openManualEntryModal() {
    if (!currentSessionId) {
        showError('Please select a session first');
        return;
    }
    loadStudentsForManualEntry();
    document.getElementById('manual-checkin-time').value = new Date().toISOString().slice(0, 16);
    document.getElementById('manual-entry-modal').classList.add('active');
}

async function loadStudentsForManualEntry() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/students`);
        const students = await response.json();
        const select = document.getElementById('manual-student-id');
        select.innerHTML = '<option value="">Select a student...</option>';
        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.id;
            option.textContent = `${student.student_id} - ${student.name}`;
            select.appendChild(option);
        });
    } catch (error) {
        showError('Failed to load students');
    }
}

async function submitManualEntry(event) {
    event.preventDefault();
    const studentId = parseInt(document.getElementById('manual-student-id').value);
    const status = document.getElementById('manual-status').value;
    const checkInTime = new Date(document.getElementById('manual-checkin-time').value).toISOString();
    const notes = document.getElementById('manual-notes').value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/attendance/manual-check-in`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: parseInt(currentSessionId),
                student_id: allStudents.find(s => s.id === studentId)?.student_id,
                status: status,
                check_in_time: checkInTime,
                notes: notes
            })
        });

        if (response.ok) {
            closeModal('manual-entry-modal');
            showSuccess('Manual entry added successfully!');
            loadAttendanceRecords();
        } else {
            const error = await response.json();
            showError(error.detail || 'Failed to add manual entry');
        }
    } catch (error) {
        showError('Failed to add manual entry: ' + error.message);
    }
}
```

**Caption:** "Figure 6.63: Manual attendance entry functions with form handling (Section 6.7.14)"

**Explanation:** These functions enable manual attendance entry: opening the modal, loading student options, and submitting entries. The implementation demonstrates form validation, date handling, student lookup, and API integration for administrative override capabilities.

---

### Screenshot 6.64: Frontend - Report Generation Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2431-2473  
**Location:** Section 6.7.15 - Reporting

**What to Capture:**
```javascript
// Report generation
async function generateReport() {
    const startDate = document.getElementById('report-start-date').value;
    const endDate = document.getElementById('report-end-date').value;

    try {
        // Load all sessions and attendance
        const sessionsResponse = await fetch(`${API_BASE_URL}/api/sessions`);
        const sessions = await sessionsResponse.json();
        
        let filteredSessions = sessions;
        if (startDate && endDate) {
            filteredSessions = sessions.filter(s => {
                const sessionDate = new Date(s.scheduled_start);
                return sessionDate >= new Date(startDate) && sessionDate <= new Date(endDate);
            });
        }

        // Calculate statistics
        let totalRecords = 0;
        let presentCount = 0;
        
        for (const session of filteredSessions) {
            try {
                const attResponse = await fetch(`${API_BASE_URL}/api/sessions/${session.id}/attendance`);
                const records = await attResponse.json();
                totalRecords += records.length;
                presentCount += records.filter(r => r.status === 'present').length;
            } catch (e) {}
        }

        document.getElementById('report-total-sessions').textContent = filteredSessions.length;
        document.getElementById('report-total-students').textContent = allStudents.length;
        document.getElementById('report-avg-attendance').textContent = 
            filteredSessions.length > 0 ? Math.round((presentCount / totalRecords) * 100) + '%' : '0%';

        // Update report charts
        updateReportCharts(filteredSessions);

        showSuccess('Report generated successfully!');
    } catch (error) {
        showError('Failed to generate report: ' + error.message);
    }
}
```

**Caption:** "Figure 6.64: Report generation function with date filtering and statistics calculation (Section 6.7.15)"

**Explanation:** This function generates comprehensive attendance reports by fetching sessions, filtering by date range, aggregating attendance data across multiple sessions, and calculating statistics. The implementation demonstrates batch API calls, data aggregation, and chart updates.

---

### Screenshot 6.65: Evaluation Script - Basic Counts Computation
**Type:** Code Screenshot  
**File:** `tools/evaluate_recognition.py`  
**Lines:** 33-59  
**Location:** Section 6.8.1 - Evaluation Metrics

**What to Capture:**
```python
def compute_basic_counts(df: pd.DataFrame, ground_col: str, pred_col: str):
    TP = FP = FN = TN = 0
    per_pair = []  # for confusion matrix

    for _, row in df.iterrows():
        gt = safe_str(row.get(ground_col, ""))
        pred = safe_str(row.get(pred_col, ""))

        if gt and pred:
            if pred == gt:
                TP += 1
            else:
                # predicted someone but wrong => false accept
                FP += 1
        elif gt and not pred:
            # ground truth present but system didn't predict => miss
            FN += 1
        elif not gt and pred:
            # no ground truth, but system predicted => false accept
            FP += 1
        else:
            # no ground truth, no prediction
            TN += 1

        per_pair.append((gt or "__NONE__", pred or "__NONE__"))

    return {"TP": TP, "FP": FP, "FN": FN, "TN": TN}, per_pair
```

**Caption:** "Figure 6.65: Evaluation script basic counts computation for confusion matrix (Section 6.8.1)"

**Explanation:** This function computes True Positives, False Positives, False Negatives, and True Negatives by comparing ground truth and predicted values. The implementation handles edge cases (empty values) and builds a confusion matrix dataset, demonstrating proper evaluation metric calculation for face recognition systems.

---

### Screenshot 6.66: Evaluation Script - Rate Computation
**Type:** Code Screenshot  
**File:** `tools/evaluate_recognition.py`  
**Lines:** 62-83  
**Location:** Section 6.8.2 - Performance Metrics

**What to Capture:**
```python
def compute_rates(counts: dict):
    TP = counts["TP"]
    FP = counts["FP"]
    FN = counts["FN"]
    TN = counts["TN"]

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else 0.0

    FAR = FP / (FP + TN) if (FP + TN) > 0 else 0.0
    FRR = FN / (FN + TP) if (FN + TP) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "FAR": FAR,
        "FRR": FRR,
    }
```

**Caption:** "Figure 6.66: Performance metrics computation including Precision, Recall, F1, FAR, and FRR (Section 6.8.2)"

**Explanation:** This function calculates standard biometric evaluation metrics: Precision, Recall, F1-score, Accuracy, False Acceptance Rate (FAR), and False Rejection Rate (FRR). The implementation includes division-by-zero protection and demonstrates proper metric calculation for face recognition evaluation.

---

### Screenshot 6.67: Evaluation Script - Score Metrics Computation
**Type:** Code Screenshot  
**File:** `tools/evaluate_recognition.py`  
**Lines:** 86-126  
**Location:** Section 6.8.3 - Advanced Metrics

**What to Capture:**
```python
def try_compute_score_metrics(df: pd.DataFrame, ground_col: str, pred_col: str, score_col: str):
    try:
        from sklearn.metrics import roc_curve, auc
    except Exception:
        print("scikit-learn is not available — skipping ROC/AUC/EER calculations.\nInstall with: pip install scikit-learn")
        return None

    # Build labels: genuine (1) if predicted==ground and ground non-empty; impostor (0) otherwise
    y_true = []
    scores = []
    for _, row in df.iterrows():
        gt = safe_str(row.get(ground_col, ""))
        pred = safe_str(row.get(pred_col, ""))
        score = row.get(score_col, None)

        if score is None or (isinstance(score, float) and math.isnan(score)):
            # cannot compute
            continue

        y_true.append(1 if (gt and pred and pred == gt) else 0)
        scores.append(float(score))

    if not scores:
        return None

    fpr, tpr, thresholds = roc_curve(y_true, scores)
    roc_auc = auc(fpr, tpr)

    # Compute EER: point where FNR ~= FPR
    fnr = 1 - tpr
    eer_idx = None
    min_diff = 1.0
    for i in range(len(fpr)):
        diff = abs(fpr[i] - fnr[i])
        if diff < min_diff:
            min_diff = diff
            eer_idx = i

    eer = (fpr[eer_idx] + fnr[eer_idx]) / 2.0 if eer_idx is not None else None

    return {"fpr": fpr, "tpr": tpr, "thresholds": thresholds, "auc": roc_auc, "eer": eer}
```

**Caption:** "Figure 6.66: ROC curve and EER computation using scikit-learn (Section 6.8.3)"

**Explanation:** This function computes advanced biometric metrics: ROC curve, AUC (Area Under Curve), and EER (Equal Error Rate). The implementation uses scikit-learn for ROC computation and calculates EER by finding the threshold where False Positive Rate equals False Negative Rate, demonstrating sophisticated evaluation techniques.

---

### Screenshot 6.68: Test Suite - Initialization and Mark Present Tests
**Type:** Code Screenshot  
**File:** `tests/test_attendance.py`  
**Lines:** 17-48  
**Location:** Section 6.9.1 - Unit Testing

**What to Capture:**
```python
def setUp(self):
    """
    This method is called before each test function is executed.
    It's used to set up a clean state for every test.
    """
    self.class_roster = ["student_01", "student_02", "student_03", "student_04"]
    self.tracker = AttendanceTracker(self.class_roster)
    print("\nSetting up for a new test...")

def test_initialization(self):
    """
    Tests if the tracker initializes correctly with an empty attendance list
    and the correct list of absent students.
    """
    print("Testing initial state...")
    # Assert that the list of present students is initially empty
    self.assertEqual(len(self.tracker.get_attendance_list()), 0)
    # Assert that the list of absent students matches the full roster initially
    self.assertCountEqual(self.tracker.get_absent_students(), self.class_roster)

def test_mark_present(self):
    """
    Tests if a student can be successfully marked as present.
    """
    print("Testing marking a student present...")
    student_to_mark = "student_02"
    self.tracker.mark_present(student_to_mark)
    # Assert that the student now appears in the present list
    self.assertIn(student_to_mark, self.tracker.get_attendance_list())
    # Assert that the student is no longer in the absent list
    self.assertNotIn(student_to_mark, self.tracker.get_absent_students())
```

**Caption:** "Figure 6.68: Unit test setup and basic functionality tests (Section 6.9.1)"

**Explanation:** These test methods demonstrate unit testing patterns: `setUp` provides test fixtures, `test_initialization` verifies initial state, and `test_mark_present` tests core functionality. The tests use unittest assertions (`assertEqual`, `assertIn`, `assertNotIn`) to validate expected behavior.

---

### Screenshot 6.69: Database Models - Course and Lecturer Entities
**Type:** Code Screenshot  
**File:** `src/models/models.py`  
**Lines:** 24-83  
**Location:** Section 5.3.2 - Additional Database Models

**What to Capture:**
```python
class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True, index=True, nullable=False)
    course_name = Column(String(200), nullable=False)
    lecturer_name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="course")

class Lecturer(Base):
    __tablename__ = "lecturers"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Caption:** "Figure 6.69: Course and Lecturer database models with relationships (Section 5.3.2)"

**Explanation:** These models define Course and Lecturer entities with proper SQLAlchemy column definitions, constraints (unique, nullable), and relationships. The Course model includes a one-to-many relationship with Sessions, while the Lecturer model includes authentication fields (hashed_password) for future authentication implementation.

---

### Screenshot 6.70: API - Get and Create Course Endpoints
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 192-206  
**Location:** Section 6.3.4 - Course Management

**What to Capture:**
```python
# Get all courses
@app.get("/api/courses")
async def get_courses(db: Session = Depends(get_db)):
    """Get all courses"""
    courses = db.query(Course).filter(Course.is_active == True).all()
    return courses

# Create course
@app.post("/api/courses")
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course"""
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
```

**Caption:** "Figure 6.70: Course management endpoints for retrieval and creation (Section 6.3.4)"

**Explanation:** These endpoints provide course management functionality: GET retrieves all active courses with filtering, and POST creates new courses using Pydantic models for validation. The implementation demonstrates standard CRUD patterns, database session management, and proper HTTP status codes.

---

### Screenshot 6.71: Frontend - Chart Update Functions
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 1616-1699  
**Location:** Section 6.7.16 - Data Visualization

**What to Capture:**
```javascript
// Update attendance charts
let trendChart = null, pieChart = null, barChart = null;
function updateAttendanceCharts(records) {
    // Attendance Trend Chart
    const ctx1 = document.getElementById('attendance-trend-chart');
    if (ctx1) {
        const dates = [...new Set(records.map(r => new Date(r.check_in_time).toLocaleDateString()))].sort();
        const counts = dates.map(date => records.filter(r => new Date(r.check_in_time).toLocaleDateString() === date).length);
        
        if (trendChart) trendChart.destroy();
        trendChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Check-ins',
                    data: counts,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { display: false } }
            }
        });
    }

    // Status Pie Chart
    const ctx2 = document.getElementById('status-pie-chart');
    if (ctx2) {
        const statusCounts = {
            present: records.filter(r => r.status === 'present').length,
            late: records.filter(r => r.status === 'late').length,
            absent: records.filter(r => r.status === 'absent').length
        };
        
        if (pieChart) pieChart.destroy();
        pieChart = new Chart(ctx2, {
            type: 'pie',
            data: {
                labels: ['Present', 'Late', 'Absent'],
                datasets: [{
                    data: [statusCounts.present, statusCounts.late, statusCounts.absent],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }
}
```

**Caption:** "Figure 6.71: Chart.js chart update functions for trend and pie charts (Section 6.7.16)"

**Explanation:** This function creates and updates multiple Chart.js visualizations: a line chart for attendance trends over time and a pie chart for status distribution. The implementation demonstrates data aggregation, chart lifecycle management (destroying old charts before creating new ones), and Chart.js configuration.

---

### Screenshot 6.72: Frontend - Kiosk Check-In Function
**Type:** Code Screenshot  
**File:** `src/api/web_dashboard.html`  
**Lines:** 2190-2232  
**Location:** Section 6.7.17 - Kiosk Integration

**What to Capture:**
```javascript
async function performCheckIn() {
    const video = document.getElementById('kiosk-video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
    const base64 = dataUrl.split(',')[1];
    try {
        const resp = await fetch(`${API_BASE_URL}/api/attendance/check-in`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: Number(currentSessionId), face_image_base64: base64 })
        });
        const json = await resp.json();
        if (json && json.success) {
            const confidence = json.confidence || 0;
            if (confidence >= kioskSettings.confidenceThreshold) {
                document.getElementById('kiosk-status').innerHTML = `<i class="fas fa-check-circle"></i> Welcome ${json.student_name}! (${(confidence*100).toFixed(0)}%)`;
                document.getElementById('kiosk-status').style.color = '#28a745';
                setTimeout(() => {
                    document.getElementById('kiosk-status').textContent = 'Camera running - Waiting for face...';
                    document.getElementById('kiosk-status').style.color = '';
                }, kioskSettings.successMessageDuration * 1000);
            } else {
                document.getElementById('kiosk-status').textContent = `Low confidence: ${(confidence*100).toFixed(0)}%`;
                document.getElementById('kiosk-status').style.color = '#ffc107';
            }
        } else if (json && json.message) {
            document.getElementById('kiosk-status').textContent = json.message;
            document.getElementById('kiosk-status').style.color = '#dc3545';
        }
    } catch (err) {
        console.warn('check-in failed', err);
    }
}
```

**Caption:** "Figure 6.72: Web-based kiosk check-in function with canvas capture (Section 6.7.17)"

**Explanation:** This function implements web-based face recognition check-in by capturing video frames to canvas, converting to base64, and sending to the API. The function handles confidence thresholds, success/error states, and provides user feedback with colored status messages and auto-dismiss timers.

---

## 📊 SUMMARY: Screenshot Count by Section
**Type:** Code Screenshot  
**File:** `src/api/attendance_api.py`  
**Lines:** 192-206  
**Location:** Section 6.3.4 - Course Management

**What to Capture:**
```python
# Get all courses
@app.get("/api/courses")
async def get_courses(db: Session = Depends(get_db)):
    """Get all courses"""
    courses = db.query(Course).filter(Course.is_active == True).all()
    return courses

# Create course
@app.post("/api/courses")
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course"""
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
```

**Caption:** "Figure 6.70: Course management endpoints for retrieval and creation (Section 6.3.4)"

**Explanation:** These endpoints provide course management functionality: GET retrieves all active courses with filtering, and POST creates new courses using Pydantic models for validation. The implementation demonstrates standard CRUD patterns, database session management, and proper HTTP status codes.

---

## 📊 SUMMARY: Screenshot Count by Section

| Section | Code Screenshots | UI Screenshots | Total |
|---------|------------------|----------------|-------|
| Section 2 | 0 | 1 | 1 |
| Section 4 | 0 | 2 | 2 |
| Section 5 | 5 | 0 | 5 |
| Section 6 | 67 | 6 | 73 |
| Section 7 | 0 | 4 | 4 |
| Section 8 | 0 | 5 | 5 |
| **Total** | **72** | **18** | **90** |

---

## 📝 NOTES FOR SCREENSHOT CAPTURE

1. **Code Screenshots:**
   - Use syntax highlighting
   - Show line numbers
   - Include relevant context (imports, function signatures)
   - Crop to relevant sections (don't show entire file unless necessary)

2. **UI Screenshots:**
   - Use consistent browser zoom (100% or 125%)
   - Show full UI elements
   - Include status indicators
   - Capture before/after states for dynamic features

3. **File Naming Convention:**
   - `fig-2.1-dashboard-overview.png`
   - `fig-5.2-fastapi-setup.png`
   - `fig-6.2-liveness-detector-init.png`
   - etc.

4. **Caption Format:**
   - "Figure X.Y: [Description] (Section Y.Z)"
   - Reference in text: "As shown in Figure X.Y..."

5. **Quality Requirements:**
   - Minimum resolution: 1920x1080
   - Format: PNG for code, PNG/JPG for UI
   - Text must be readable
   - No sensitive data exposed

---

## ✅ CHECKLIST

- [ ] Section 2: Introduction screenshots (1)
- [ ] Section 4: Requirement Analysis screenshots (2)
- [ ] Section 5: Software Design screenshots (5)
- [ ] Section 6: Software Implementation screenshots (34)
- [ ] Section 7: Evaluation screenshots (4)
- [ ] Section 8: Appendix screenshots (5)
- [ ] All code screenshots with line numbers verified
- [ ] All UI screenshots with proper states captured
- [ ] All captions and explanations written
- [ ] Screenshots inserted into report document

---

**Total Screenshots Required: 90**
**Code Screenshots: 72**
**UI Screenshots: 18**

