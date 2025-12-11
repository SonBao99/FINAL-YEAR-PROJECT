from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session as DBSession, joinedload
from database import get_db, create_tables
from models import Student, Course, Session, AttendanceRecord, Lecturer, session_student_enrollment
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import face_recognition
import cv2
import numpy as np
import json
import base64
import os
from pathlib import Path
import asyncio
import subprocess
import sys
import logging
from websocket_manager import ConnectionManager

# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attendance_api.log'),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)

app = FastAPI(title="Face Recognition Attendance System", version="1.0.0")

# CORS middleware
# In production, replace "*" with your actual domain
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager for real-time updates
manager = ConnectionManager()

# Kiosk process management
kiosk_process: Optional[subprocess.Popen] = None

# Pydantic models for API
class StudentCreate(BaseModel):
    student_id: str
    name: str
    email: str
    photo_base64: str  # Base64 encoded photo
    session_ids: Optional[List[int]] = None  # Optional list of session IDs to enroll student into

class StudentResponse(BaseModel):
    id: int
    student_id: str
    name: str
    email: str
    is_active: bool
    created_at: datetime

class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    lecturer_name: str
    description: Optional[str] = None

class SessionCreate(BaseModel):
    course_id: int
    session_name: str
    scheduled_start: datetime
    scheduled_end: datetime
    room_location: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: int
    student: StudentResponse
    check_in_time: datetime
    confidence_score: Optional[float]
    status: str

class CheckInRequest(BaseModel):
    session_id: int
    face_image_base64: str

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check which database is being used
        use_mongodb = os.getenv("USE_MONGODB", "false").lower() == "true" or os.getenv("MONGODB_URL")
        
        if use_mongodb:
            # Test MongoDB connection
            from database_mongodb import get_mongodb_client
            client = get_mongodb_client()
            client.admin.command('ping')
            return {"status": "healthy", "database": "mongodb", "connected": True}
        else:
            # Test SQL database connection
            from database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "sql", "connected": True}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Create database tables/indexes on startup
@app.on_event("startup")
async def startup_event():
    # Check if using MongoDB
    use_mongodb = os.getenv("USE_MONGODB", "false").lower() == "true" or os.getenv("MONGODB_URL")
    
    if use_mongodb:
        # Initialize MongoDB indexes
        try:
            from database_mongodb import create_indexes
            create_indexes()
        except ImportError:
            pass
    else:
        # Create SQL tables
        create_tables()

# Student enrollment endpoint
@app.post("/api/students/enroll", response_model=StudentResponse)
async def enroll_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Enroll a new student with face encoding"""
    
    # Decode base64 image
    try:
        image_data = base64.b64decode(student.photo_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
            
        # Convert BGR to RGB for face_recognition
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find face encodings
        face_encodings = face_recognition.face_encodings(rgb_image)
        
        if not face_encodings:
            raise HTTPException(status_code=400, detail="No face detected in the image")
        
        # Use the first face encoding
        face_encoding = face_encodings[0]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    # Check if student already exists
    db_student = db.query(Student).filter(Student.student_id == student.student_id).first()
    
    if db_student:
        # Student exists - update face encoding and photo
        # This handles the case where multiple photos are uploaded
        db_student.face_encoding = json.dumps(face_encoding.tolist())
        # Save new photo
        photos_dir = Path("student_photos")
        photos_dir.mkdir(exist_ok=True)
        photo_filename = f"{student.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        photo_path = photos_dir / photo_filename
        cv2.imwrite(str(photo_path), image)
        db_student.photo_path = str(photo_path)
        db.commit()
        db.refresh(db_student)
    else:
        # Create new student record
        photos_dir = Path("student_photos")
        photos_dir.mkdir(exist_ok=True)
        photo_filename = f"{student.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        photo_path = photos_dir / photo_filename
        cv2.imwrite(str(photo_path), image)
        
        db_student = Student(
            student_id=student.student_id,
            name=student.name,
            email=student.email,
            face_encoding=json.dumps(face_encoding.tolist()),
            photo_path=str(photo_path)
        )
        
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
    
    # Enroll student into sessions if provided
    enrolled_sessions = []
    if student.session_ids:
        for session_id in student.session_ids:
            session = db.query(Session).filter(Session.id == session_id).first()
            if session and db_student not in session.enrolled_students:
                session.enrolled_students.append(db_student)
                enrolled_sessions.append(session.session_name)
        db.commit()
    
    return StudentResponse(
        id=db_student.id,
        student_id=db_student.student_id,
        name=db_student.name,
        email=db_student.email,
        is_active=db_student.is_active,
        created_at=db_student.created_at
    )

# Get all students
@app.get("/api/students", response_model=List[StudentResponse])
async def get_students(db: Session = Depends(get_db)):
    """Get all enrolled students"""
    students = db.query(Student).filter(Student.is_active == True).all()
    return [
        StudentResponse(
            id=s.id,
            student_id=s.student_id,
            name=s.name,
            email=s.email,
            is_active=s.is_active,
            created_at=s.created_at
        ) for s in students
    ]

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

# Create session
@app.post("/api/sessions")
async def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new attendance session"""
    db_session = Session(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

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
            "enrolled_students_count": len(s.enrolled_students) if s.enrolled_students else 0,
            "course": {
                "id": s.course.id if s.course else None,
                "course_code": s.course.course_code if s.course else None,
                "course_name": s.course.course_name if s.course else None,
                "lecturer_name": s.course.lecturer_name if s.course else None
            }
        })
    return result

# Enroll student into a session
class SessionEnrollmentRequest(BaseModel):
    student_id: int  # Database ID of student
    session_id: int

@app.post("/api/sessions/{session_id}/enroll-student")
async def enroll_student_to_session(
    session_id: int,
    request: SessionEnrollmentRequest,
    db: DBSession = Depends(get_db)
):
    """Enroll a student into a specific session"""
    # Verify session exists - load relationship explicitly
    session = db.query(Session).options(joinedload(Session.enrolled_students)).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify student exists
    student = db.query(Student).filter(Student.id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already enrolled
    enrolled_ids = [s.id for s in session.enrolled_students]
    if student.id in enrolled_ids:
        return {"success": False, "message": "Student already enrolled in this session"}
    
    # Enroll student
    session.enrolled_students.append(student)
    db.commit()
    db.refresh(session)  # Refresh to ensure relationship is loaded
    
    # Verify enrollment was saved
    db.refresh(student)
    enrolled_count = len(session.enrolled_students)
    print(f"✓ Enrollment saved - Session {session.id} now has {enrolled_count} enrolled students")
    logging.info(f"Student {student.id} ({student.name}) enrolled in session {session.id} ({session.session_name}). Total enrolled: {enrolled_count}")
    
    return {
        "success": True,
        "message": f"{student.name} enrolled in session {session.session_name}",
        "student_id": student.id,
        "student_name": student.name,
        "session_id": session.id,
        "session_name": session.session_name,
        "enrolled_count": enrolled_count
    }

# Remove student from session enrollment
@app.delete("/api/sessions/{session_id}/enroll-student/{student_id}")
async def remove_student_from_session(
    session_id: int,
    student_id: int,
    db: DBSession = Depends(get_db)
):
    """Remove a student from a session enrollment"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student not in session.enrolled_students:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this session")
    
    session.enrolled_students.remove(student)
    db.commit()
    
    return {
        "success": True,
        "message": f"{student.name} removed from session {session.session_name}"
    }

# Get enrolled students for a session
@app.get("/api/sessions/{session_id}/enrolled-students")
async def get_enrolled_students(
    session_id: int,
    db: DBSession = Depends(get_db)
):
    """Get all students enrolled in a specific session"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    enrolled_students = []
    for student in session.enrolled_students:
        enrolled_students.append({
            "id": student.id,
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "is_active": student.is_active
        })
    
    return {
        "session_id": session.id,
        "session_name": session.session_name,
        "enrolled_students": enrolled_students,
        "count": len(enrolled_students)
    }

# Get sessions a student is enrolled in
@app.get("/api/students/{student_id}/enrolled-sessions")
async def get_student_enrolled_sessions(
    student_id: int,
    db: DBSession = Depends(get_db)
):
    """Get all sessions a student is enrolled in"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    enrolled_sessions = []
    for session in student.enrolled_sessions:
        enrolled_sessions.append({
            "id": session.id,
            "session_name": session.session_name,
            "scheduled_start": session.scheduled_start.isoformat() if session.scheduled_start else None,
            "scheduled_end": session.scheduled_end.isoformat() if session.scheduled_end else None,
            "is_active": session.is_active,
            "course": {
                "id": session.course.id if session.course else None,
                "course_code": session.course.course_code if session.course else None,
                "course_name": session.course.course_name if session.course else None
            }
        })
    
    return {
        "student_id": student.id,
        "student_name": student.name,
        "enrolled_sessions": enrolled_sessions,
        "count": len(enrolled_sessions)
    }

# Serve dashboard
@app.get("/")
async def serve_dashboard():
    return FileResponse("src/api/web_dashboard.html")

# Start session
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

# Stop session
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

# Get session attendance
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

# Video stream WebSocket endpoint for kiosk to send frames
@app.websocket("/ws/video-stream")
async def video_stream_endpoint(websocket: WebSocket):
    """WebSocket endpoint for kiosk to send video frames"""
    await manager.connect_video_stream_source(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Kiosk sends frames, we broadcast to all connected web clients
            try:
                message = json.loads(data)
                if message.get("type") == "video_frame":
                    # Broadcast to all video stream clients (web dashboard viewers)
                    await manager.broadcast_video_frame(message.get("frame"))
                elif message.get("type") == "stats_update":
                    # Broadcast stats update to all video stream clients
                    await manager.broadcast_stats_update(message.get("stats"))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect_video_stream_source(websocket)

# WebSocket endpoint for web clients to receive video stream
@app.websocket("/ws/video-viewer")
async def video_viewer_endpoint(websocket: WebSocket):
    """WebSocket endpoint for web dashboard to receive live video feed from kiosk"""
    await manager.connect_video_viewer(websocket)
    try:
        # Send a message to indicate connection
        await websocket.send_text(json.dumps({"type": "connected", "message": "Connected to video stream"}))
        # Keep connection alive - frames will be broadcast by broadcast_video_frame
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect_video_viewer(websocket)

# Face recognition endpoint for kiosk
@app.post("/api/attendance/check-in")
async def check_in_student(
    request: CheckInRequest,
    db: DBSession = Depends(get_db)
):
    """Process face recognition and mark attendance"""
    
    # Get active session
    session = db.query(Session).filter(
        Session.id == request.session_id,
        Session.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")
    
    # Decode and process image
    try:
        image_data = base64.b64decode(request.face_image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get face encodings from the image
        face_encodings = face_recognition.face_encodings(rgb_image)
        
        if not face_encodings:
            return {"success": False, "message": "No face detected"}
        
        # Get all enrolled students
        students = db.query(Student).filter(Student.is_active == True).all()
        
        # If no students enrolled, face cannot be recognized
        if not students:
            return {"success": False, "message": "Face not recognized - No students enrolled"}
        
        best_match = None
        best_distance = float('inf')
        
        # Face Recognition Threshold Explanation:
        # LOWER threshold = STRICTER (fewer false matches, but might reject legitimate matches)
        # HIGHER threshold = MORE LENIENT (more matches, but also more false positives)
        # 
        # Distance meaning:
        # - 0.0 = Perfect match (same photo)
        # - 0.2-0.3 = Very similar (same person, different conditions)
        # - 0.4 = Good match (same person) - RECOMMENDED for security
        # - 0.6 = Recommended threshold by library (balanced, allows variation)
        # - 0.8+ = Too lenient (will match different people - CAUSES FALSE MATCHES)
        #
        # For security: Use 0.25 to prevent false matches while still recognizing enrolled students
        # Lower = stricter (fewer false matches)
        # 0.25 is strict but allows normal variation (lighting, angle, expression)
        # This prevents unrecognized faces from matching enrolled students
        # Note: If legitimate enrolled students are being rejected, increase to 0.3
        RECOGNITION_THRESHOLD = 0.25  # Strict but allows normal variation
        
        # Compare face with all enrolled students
        all_distances = []  # Track all distances for debugging
        for student in students:
            if student.face_encoding:
                try:
                    stored_encoding = np.array(json.loads(student.face_encoding))
                    
                    # Compare face encodings
                    distances = face_recognition.face_distance([stored_encoding], face_encodings[0])
                    distance = distances[0]
                    all_distances.append((student.student_id, student.name, distance))
                    
                    # CRITICAL: Only consider matches where distance is STRICTLY BELOW threshold
                    # This ensures we only match faces that are actually similar
                    # Do NOT set best_match if distance >= threshold
                    # IMPORTANT: Use strict comparison (< not <=) to prevent edge cases
                    if distance < RECOGNITION_THRESHOLD:
                        # Track the best match (lowest distance that's below threshold)
                        # Only update if this is a better match AND still below threshold
                        if distance < best_distance:
                            # Double-check threshold before setting match
                            if distance < RECOGNITION_THRESHOLD:
                                best_distance = distance
                                best_match = student
                            else:
                                # This should never happen, but defensive check
                                print(f"🚨 BUG: Distance {distance:.6f} passed first check but failed second check!")
                                logging.error(f"BUG: Distance {distance:.6f} passed first check but failed second check!")
                    else:
                        # Distance is >= threshold, skip this student
                        logging.debug(f"Skipping {student.name}: distance {distance:.6f} >= threshold {RECOGNITION_THRESHOLD}")
                except (json.JSONDecodeError, ValueError) as e:
                    # Skip students with invalid face encodings
                    continue
        
        # Debug: Log distances to help diagnose false matches
        if all_distances:
            all_distances.sort(key=lambda x: x[2])  # Sort by distance
            closest_student_id, closest_name, closest_distance = all_distances[0]
            matched_name = best_match.name if best_match else "NONE"
            matched_distance = best_distance if best_match else float('inf')
            
            # Print to console for immediate visibility
            # Format matched_distance safely (can't use ternary in f-string format specifier)
            matched_dist_str = f"{matched_distance:.6f}" if matched_distance != float('inf') else 'N/A'
            
            print(f"\n{'='*60}")
            print(f"FACE RECOGNITION ATTEMPT")
            print(f"{'='*60}")
            print(f"Threshold: {RECOGNITION_THRESHOLD}")
            print(f"Closest match: {closest_name} ({closest_student_id})")
            print(f"Closest distance: {closest_distance:.6f}")
            print(f"Matched student: {matched_name}")
            print(f"Matched distance: {matched_dist_str}")
            print(f"Match result: {'MATCHED' if best_match else 'REJECTED'}")
            if best_match:
                print(f"⚠️  WARNING: Match found with distance {matched_distance:.6f} (threshold: {RECOGNITION_THRESHOLD})")
                print(f"⚠️  If this is an unrecognized face, the threshold may need to be lower!")
            else:
                print(f"✓ Correctly rejected (distance {closest_distance:.6f} >= threshold {RECOGNITION_THRESHOLD})")
            print(f"{'='*60}\n")
            
            # Also log to file (with error handling)
            try:
                matched_dist_str = f"{matched_distance:.6f}" if matched_distance != float('inf') else 'N/A'
                logging.info(f"Recognition attempt - Closest: {closest_name} ({closest_student_id}) distance={closest_distance:.6f}, threshold={RECOGNITION_THRESHOLD}, matched={matched_name}, matched_distance={matched_dist_str}")
            except Exception as log_err:
                # Don't let logging errors break the recognition flow
                logging.warning(f"Error logging recognition attempt: {log_err}")
        
        # CRITICAL CHECK: Only return a match if:
        # 1. best_match is not None (found a student)
        # 2. best_distance is below the strict threshold (actually similar)
        # This ensures unrecognized faces are correctly rejected
        # IMPORTANT: If best_distance >= threshold, best_match should be None
        # But we double-check here to be absolutely sure
        if best_match is not None:
            # Verify the distance is actually below threshold (safety check)
            if best_distance >= RECOGNITION_THRESHOLD:
                # This should never happen if logic is correct, but reject just in case
                print(f"🚨 CRITICAL ERROR: best_match set but distance {best_distance:.6f} >= threshold {RECOGNITION_THRESHOLD}. Rejecting match.")
                logging.error(f"CRITICAL: best_match set but distance {best_distance:.6f} >= threshold {RECOGNITION_THRESHOLD}. Rejecting match.")
                best_match = None
            else:
                # Additional validation: ensure distance is reasonable
                if best_distance > 0.3:
                    print(f"⚠️  WARNING: Match found with high distance {best_distance:.6f} (threshold: {RECOGNITION_THRESHOLD})")
                    logging.warning(f"Match found with high distance {best_distance:.6f} (threshold: {RECOGNITION_THRESHOLD})")
        # FINAL VALIDATION: Only proceed if we have a valid match
        # Triple-check: best_match must exist AND distance must be strictly below threshold
        if best_match is not None:
            # Final safety check before proceeding
            if best_distance >= RECOGNITION_THRESHOLD:
                print(f"🚨 FINAL CHECK FAILED: best_match exists but distance {best_distance:.6f} >= threshold {RECOGNITION_THRESHOLD}")
                logging.error(f"FINAL CHECK FAILED: best_match exists but distance {best_distance:.6f} >= threshold {RECOGNITION_THRESHOLD}")
                best_match = None
        
        # Only proceed if we have a valid match after all checks
        if best_match is not None and best_distance < RECOGNITION_THRESHOLD:
            # CRITICAL: Check if student is enrolled in this session
            # Use joinedload to ensure enrolled_students relationship is loaded
            session = db.query(Session).options(joinedload(Session.enrolled_students)).filter(Session.id == request.session_id).first()
            if not session:
                return {"success": False, "message": "Session not found"}
            
            # Debug: Log enrollment check
            # Force refresh to ensure we have latest enrollment data
            db.refresh(session)
            enrolled_student_ids = [s.id for s in session.enrolled_students]
            is_enrolled = best_match.id in enrolled_student_ids
            
            print(f"🔍 Enrollment check - Session {session.id} ({session.session_name})")
            print(f"   Enrolled student IDs: {enrolled_student_ids}")
            print(f"   Checking student: {best_match.name} (ID: {best_match.id})")
            print(f"   Is enrolled: {is_enrolled}")
            logging.info(f"Enrollment check - Session {session.id}: Enrolled IDs={enrolled_student_ids}, Checking={best_match.id}, Result={is_enrolled}")
            
            if not is_enrolled:
                return {
                    "success": False,
                    "message": f"Student {best_match.name} is not enrolled in this session"
                }
            
            # Check if already checked in
            existing_record = db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == best_match.id,
                AttendanceRecord.session_id == request.session_id
            ).first()
            
            if existing_record:
                return {
                    "success": False,
                    "message": "Already checked in",
                    "student_name": best_match.name,
                    "student_id": best_match.student_id,
                    "confidence": existing_record.confidence_score or 0.0
                }
            
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
            
            # Notify web dashboard via WebSocket
            await manager.broadcast_to_session(request.session_id, {
                "type": "attendance_update",
                "student_name": best_match.name,
                "student_id": best_match.student_id,
                "check_in_time": attendance_record.check_in_time.isoformat(),
                "confidence": attendance_record.confidence_score
            })
            
            return {
                "success": True,
                "message": f"Welcome {best_match.name}!",
                "student_name": best_match.name,
                "student_id": best_match.student_id,
                "confidence": attendance_record.confidence_score
            }
        else:
            # No match found - face is not in the database
            # This happens when:
            # 1. No students enrolled
            # 2. All students have distance >= threshold (face doesn't match anyone)
            # 3. best_match is None (no student matched)
            return {
                "success": False, 
                "message": "Face not recognized - Person not enrolled in the system"
            }
            
    except Exception as e:
        # Log the full error for debugging
        error_msg = f"Error processing face: {str(e)}"
        logging.error(f"Exception in check_in_student: {error_msg}", exc_info=True)
        print(f"🚨 ERROR in face recognition: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=error_msg)

# Manual check-in endpoint
class ManualCheckInRequest(BaseModel):
    session_id: int
    student_id: str  # Student ID string, not database ID
    status: str = "present"  # present, late, absent
    check_in_time: Optional[datetime] = None
    notes: Optional[str] = None

@app.post("/api/attendance/manual-check-in")
async def manual_check_in(
    request: ManualCheckInRequest,
    db: DBSession = Depends(get_db)
):
    """Manually add attendance record"""
    
    # Get session
    session = db.query(Session).filter(Session.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get student by student_id
    student = db.query(Student).filter(Student.student_id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already checked in
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student.id,
        AttendanceRecord.session_id == request.session_id
    ).first()
    
    if existing_record:
        raise HTTPException(status_code=400, detail="Student already checked in for this session")
    
    # Create attendance record
    check_in_time = request.check_in_time if request.check_in_time else datetime.utcnow()
    attendance_record = AttendanceRecord(
        student_id=student.id,
        session_id=request.session_id,
        check_in_time=check_in_time,
        status=request.status,
        notes=request.notes
    )
    
    db.add(attendance_record)
    db.commit()
    db.refresh(attendance_record)
    
    # Notify web dashboard via WebSocket
    await manager.broadcast_to_session(request.session_id, {
        "type": "attendance_update",
        "student_name": student.name,
        "student_id": student.student_id,
        "check_in_time": attendance_record.check_in_time.isoformat(),
        "status": attendance_record.status
    })
    
    return {
        "success": True,
        "message": f"Manual entry added for {student.name}",
        "attendance_id": attendance_record.id
    }

# Kiosk control endpoints
@app.post("/api/kiosk/start")
async def start_kiosk():
    """Start the kiosk application"""
    global kiosk_process
    
    if kiosk_process is not None and kiosk_process.poll() is None:
        return {"success": False, "message": "Kiosk is already running"}
    
    try:
        # Get the path to kiosk_app.py
        current_dir = Path(__file__).parent
        kiosk_script = current_dir / "src" / "api" / "kiosk_app.py"
        
        if not kiosk_script.exists():
            raise HTTPException(status_code=404, detail="Kiosk script not found")
        
        # Determine Python executable
        python_exe = sys.executable
        
        # Start the kiosk process
        kiosk_process = subprocess.Popen(
            [python_exe, str(kiosk_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(current_dir)
        )
        
        return {
            "success": True,
            "message": "Kiosk started successfully",
            "pid": kiosk_process.pid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start kiosk: {str(e)}")

@app.post("/api/kiosk/stop")
async def stop_kiosk():
    """Stop the kiosk application"""
    global kiosk_process
    
    if kiosk_process is None:
        return {"success": False, "message": "Kiosk is not running"}
    
    try:
        if kiosk_process.poll() is None:  # Process is still running
            kiosk_process.terminate()
            # Wait up to 5 seconds for graceful shutdown
            try:
                kiosk_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                kiosk_process.kill()  # Force kill if it doesn't terminate
        
        kiosk_process = None
        return {"success": True, "message": "Kiosk stopped successfully"}
    except Exception as e:
        kiosk_process = None
        raise HTTPException(status_code=500, detail=f"Failed to stop kiosk: {str(e)}")

@app.get("/api/kiosk/status")
async def get_kiosk_status():
    """Get the current status of the kiosk"""
    global kiosk_process
    
    if kiosk_process is None:
        return {"running": False, "message": "Kiosk is not running"}
    
    if kiosk_process.poll() is None:
        return {"running": True, "pid": kiosk_process.pid, "message": "Kiosk is running"}
    else:
        kiosk_process = None
        return {"running": False, "message": "Kiosk process has terminated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 