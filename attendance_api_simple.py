from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, create_tables
from models import Student, Course, Session, AttendanceRecord, Lecturer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import cv2
import numpy as np
import json
import base64
import os
from pathlib import Path
import asyncio
from websocket_manager import ConnectionManager

app = FastAPI(title="Face Detection Attendance System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
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

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Student enrollment endpoint (simplified - no face recognition yet)
@app.post("/api/students/enroll", response_model=StudentResponse)
async def enroll_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Enroll a new student (face recognition will be added later)"""
    
    # Decode base64 image
    try:
        image_data = base64.b64decode(student.photo_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    # Save photo to disk
    photos_dir = Path("student_photos")
    photos_dir.mkdir(exist_ok=True)
    photo_filename = f"{student.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    photo_path = photos_dir / photo_filename
    cv2.imwrite(str(photo_path), image)
    
    # Create student record (without face encoding for now)
    db_student = Student(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        face_encoding=None,  # Will be added when face_recognition is working
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

# Create course
@app.post("/api/courses")
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course"""
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# Get all courses
@app.get("/api/courses")
async def get_courses(db: Session = Depends(get_db)):
    """Get all courses"""
    courses = db.query(Course).filter(Course.is_active == True).all()
    return courses

# Create session
@app.post("/api/sessions")
async def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new attendance session"""
    db_session = Session(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# Get all sessions
@app.get("/api/sessions")
async def get_sessions(db: Session = Depends(get_db)):
    """Get all sessions"""
    sessions = db.query(Session).all()
    return sessions

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

# Manual check-in endpoint (for testing without face recognition)
@app.post("/api/attendance/manual-check-in")
async def manual_check_in(
    session_id: int,
    student_id: str,
    db: Session = Depends(get_db)
):
    """Manual check-in for testing (without face recognition)"""
    
    # Get active session
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")
    
    # Get student
    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.is_active == True
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already checked in
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student.id,
        AttendanceRecord.session_id == session_id
    ).first()
    
    if existing_record:
        return {"success": False, "message": "Already checked in"}
    
    # Create attendance record
    attendance_record = AttendanceRecord(
        student_id=student.id,
        session_id=session_id,
        check_in_time=datetime.utcnow(),
        confidence_score=1.0,  # Manual check-in gets full confidence
        status="present"
    )
    
    db.add(attendance_record)
    db.commit()
    
    # Notify web dashboard via WebSocket
    await manager.broadcast_to_session(session_id, {
        "type": "attendance_update",
        "student_name": student.name,
        "student_id": student.student_id,
        "check_in_time": attendance_record.check_in_time.isoformat(),
        "confidence": attendance_record.confidence_score
    })
    
    return {
        "success": True,
        "message": f"Welcome {student.name}!",
        "student_name": student.name,
        "student_id": student.student_id
    }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 