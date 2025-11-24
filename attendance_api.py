from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import get_db, create_tables
from models import Student, Course, Session, AttendanceRecord, Lecturer
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
from websocket_manager import ConnectionManager

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

# Pydantic models for API
class StudentCreate(BaseModel):
    student_id: str
    name: str
    email: str
    photo_base64: str  # Base64 encoded photo

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
    
    # Save photo to disk
    photos_dir = Path("student_photos")
    photos_dir.mkdir(exist_ok=True)
    photo_filename = f"{student.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    photo_path = photos_dir / photo_filename
    cv2.imwrite(str(photo_path), image)
    
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
    db.refresh(db_student)
    
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
            "course": {
                "id": s.course.id if s.course else None,
                "course_code": s.course.course_code if s.course else None,
                "course_name": s.course.course_name if s.course else None,
                "lecturer_name": s.course.lecturer_name if s.course else None
            }
        })
    return result

# Serve dashboard
@app.get("/")
async def serve_dashboard():
    return FileResponse("web_dashboard.html")

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

# Face recognition endpoint for kiosk
@app.post("/api/attendance/check-in")
async def check_in_student(
    request: CheckInRequest,
    db: Session = Depends(get_db)
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
        
        best_match = None
        best_distance = float('inf')
        
        for student in students:
            if student.face_encoding:
                stored_encoding = np.array(json.loads(student.face_encoding))
                
                # Compare face encodings
                distances = face_recognition.face_distance([stored_encoding], face_encodings[0])
                distance = distances[0]
                
                if distance < best_distance and distance < 0.6:  # Threshold for face recognition
                    best_distance = distance
                    best_match = student
        
        if best_match:
            # Check if already checked in
            existing_record = db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == best_match.id,
                AttendanceRecord.session_id == request.session_id
            ).first()
            
            if existing_record:
                return {"success": False, "message": "Already checked in"}
            
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
            return {"success": False, "message": "Face not recognized"}
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing face: {str(e)}")

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
    db: Session = Depends(get_db)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 