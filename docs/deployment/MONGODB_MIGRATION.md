# MongoDB Migration Guide

## 🎯 Why MongoDB?

- ✅ **Flexible Schema** - Perfect for face encodings (JSON arrays)
- ✅ **Easy to Scale** - Horizontal scaling built-in
- ✅ **Cloud-Ready** - MongoDB Atlas free tier
- ✅ **JSON Native** - Face encodings stored naturally
- ✅ **Fast Queries** - Good performance for this use case

---

## 📋 Step 1: Set Up MongoDB Atlas

### **1. Create Account**
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up (free)
3. Create organization

### **2. Create Cluster**
1. Click "Build a Database"
2. Choose **FREE** tier (M0)
3. Select cloud provider (AWS recommended)
4. Choose region closest to you
5. Name cluster: `attendance-cluster`
6. Click "Create"

### **3. Create Database User**
1. Go to "Database Access"
2. Click "Add New Database User"
3. Authentication: Password
4. Username: `attendance_user`
5. Password: Generate secure password (save it!)
6. Database User Privileges: "Atlas admin" (or custom)
7. Click "Add User"

### **4. Whitelist IP Address**
1. Go to "Network Access"
2. Click "Add IP Address"
3. For development: Click "Allow Access from Anywhere" (0.0.0.0/0)
4. For production: Add specific IPs
5. Click "Confirm"

### **5. Get Connection String**
1. Go to "Database" → Click "Connect"
2. Choose "Connect your application"
3. Driver: Python, Version: 3.11 or later
4. Copy connection string:
   ```
   mongodb+srv://attendance_user:<password>@attendance-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password

---

## 🔧 Step 2: Update Code

### **Install MongoDB Drivers**

```bash
pip install pymongo motor python-dotenv
```

### **Update Environment Variables**

Create/update `.env`:
```env
MONGODB_URL=mongodb+srv://attendance_user:your_password@attendance-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=attendance_db
```

---

## 📝 Step 3: Update Database Code

### **Option A: Use MongoDB Adapter (Recommended)**

Use the `database_mongodb.py` file I created. It provides:
- Connection management
- Index creation
- Sync and async support

### **Option B: Update Existing Code**

You'll need to update `attendance_api.py` to use MongoDB instead of SQLAlchemy.

**Example - Enroll Student:**

```python
from database_mongodb import get_db
from bson import ObjectId
import json

@app.post("/api/students/enroll")
async def enroll_student(student: StudentCreate, db = Depends(get_db)):
    # Process face encoding (same as before)
    face_encodings = face_recognition.face_encodings(rgb_image)
    face_encoding = face_encodings[0]
    
    # Create student document
    student_doc = {
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "face_encoding": json.dumps(face_encoding.tolist()),
        "photo_path": str(photo_path),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    # Insert into MongoDB
    result = db.students.insert_one(student_doc)
    student_doc["id"] = str(result.inserted_id)
    
    return student_doc
```

**Example - Get Students:**

```python
@app.get("/api/students")
async def get_students(db = Depends(get_db)):
    students = list(db.students.find({"is_active": True}))
    
    # Convert ObjectId to string
    for student in students:
        student["id"] = str(student["_id"])
        del student["_id"]
    
    return students
```

**Example - Check In:**

```python
@app.post("/api/attendance/check-in")
async def check_in_student(request: CheckInRequest, db = Depends(get_db)):
    # Get face encoding from image
    face_encodings = face_recognition.face_encodings(rgb_image)
    
    # Get all students
    students = list(db.students.find({"is_active": True}))
    
    best_match = None
    best_distance = float('inf')
    
    for student in students:
        if student.get("face_encoding"):
            stored_encoding = np.array(json.loads(student["face_encoding"]))
            distances = face_recognition.face_distance([stored_encoding], face_encodings[0])
            distance = distances[0]
            
            if distance < best_distance and distance < 0.6:
                best_distance = distance
                best_match = student
    
    if best_match:
        # Check if already checked in
        existing = db.attendance_records.find_one({
            "student_id": str(best_match["_id"]),
            "session_id": str(request.session_id)
        })
        
        if existing:
            return {"success": False, "message": "Already checked in"}
        
        # Create attendance record
        record = {
            "student_id": str(best_match["_id"]),
            "session_id": str(request.session_id),
            "check_in_time": datetime.utcnow(),
            "confidence_score": 1 - best_distance,
            "status": "present"
        }
        
        db.attendance_records.insert_one(record)
        return {"success": True, "message": f"Welcome {best_match['name']}!"}
    
    return {"success": False, "message": "Face not recognized"}
```

---

## 🧪 Step 4: Test MongoDB Connection

Create `test_mongodb.py`:

```python
#!/usr/bin/env python3
"""Test MongoDB connection"""
import os
from dotenv import load_dotenv
from database_mongodb import get_db, create_indexes

load_dotenv()

print("Testing MongoDB connection...")

try:
    db = get_db()
    
    # Test connection
    db.command("ping")
    print("✅ Connected to MongoDB!")
    
    # Create indexes
    create_indexes()
    print("✅ Indexes created!")
    
    # Test insert
    test_doc = {"test": "connection", "timestamp": "now"}
    result = db.test.insert_one(test_doc)
    print(f"✅ Test insert successful! ID: {result.inserted_id}")
    
    # Test query
    doc = db.test.find_one({"test": "connection"})
    print(f"✅ Test query successful! Found: {doc}")
    
    # Cleanup
    db.test.delete_one({"_id": result.inserted_id})
    print("✅ Cleanup complete!")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

Run:
```bash
python3 test_mongodb.py
```

---

## 🔄 Step 5: Migrate Existing Data (If Any)

Create `migrate_to_mongodb.py`:

```python
#!/usr/bin/env python3
"""Migrate data from SQLite to MongoDB"""
import sqlite3
from database_mongodb import get_db
from datetime import datetime
import json

# SQLite connection
sqlite_conn = sqlite3.connect('attendance.db')
sqlite_cursor = sqlite_conn.cursor()

# MongoDB connection
mongodb = get_db()

print("Starting migration...")

# Migrate Students
print("Migrating students...")
sqlite_cursor.execute("SELECT * FROM students")
students = sqlite_cursor.fetchall()

for student in students:
    doc = {
        "student_id": student[1],
        "name": student[2],
        "email": student[3],
        "face_encoding": student[4],
        "photo_path": student[5],
        "is_active": bool(student[6]),
        "created_at": student[7] if student[7] else datetime.utcnow()
    }
    mongodb.students.insert_one(doc)

# Migrate Courses
print("Migrating courses...")
sqlite_cursor.execute("SELECT * FROM courses")
courses = sqlite_cursor.fetchall()

for course in courses:
    doc = {
        "course_code": course[1],
        "course_name": course[2],
        "lecturer_name": course[3],
        "description": course[4],
        "is_active": bool(course[5]),
        "created_at": course[6] if course[6] else datetime.utcnow()
    }
    result = mongodb.courses.insert_one(doc)
    course_id_map[course[0]] = str(result.inserted_id)

# Migrate Sessions (need course_id mapping)
print("Migrating sessions...")
course_id_map = {}
sqlite_cursor.execute("SELECT * FROM courses")
for course in sqlite_cursor.fetchall():
    # Find MongoDB course by course_code
    mongo_course = mongodb.courses.find_one({"course_code": course[1]})
    if mongo_course:
        course_id_map[course[0]] = str(mongo_course["_id"])

sqlite_cursor.execute("SELECT * FROM sessions")
sessions = sqlite_cursor.fetchall()

for session in sessions:
    doc = {
        "course_id": course_id_map.get(session[1], ""),
        "session_name": session[2],
        "scheduled_start": session[3],
        "scheduled_end": session[4],
        "actual_start": session[5],
        "actual_end": session[6],
        "room_location": session[7],
        "kiosk_device_id": session[8],
        "is_active": bool(session[9]),
        "created_at": session[10] if session[10] else datetime.utcnow()
    }
    result = mongodb.sessions.insert_one(doc)
    session_id_map[session[0]] = str(result.inserted_id)

# Migrate Attendance Records
print("Migrating attendance records...")
student_id_map = {}
sqlite_cursor.execute("SELECT * FROM students")
for student in sqlite_cursor.fetchall():
    mongo_student = mongodb.students.find_one({"student_id": student[1]})
    if mongo_student:
        student_id_map[student[0]] = str(mongo_student["_id"])

session_id_map = {}
sqlite_cursor.execute("SELECT * FROM sessions")
for session in sqlite_cursor.fetchall():
    mongo_session = mongodb.sessions.find_one({"session_name": session[2]})
    if mongo_session:
        session_id_map[session[0]] = str(mongo_session["_id"])

sqlite_cursor.execute("SELECT * FROM attendance_records")
records = sqlite_cursor.fetchall()

for record in records:
    doc = {
        "student_id": student_id_map.get(record[1], ""),
        "session_id": session_id_map.get(record[2], ""),
        "check_in_time": record[3],
        "confidence_score": record[4],
        "face_photo_path": record[5],
        "status": record[6],
        "notes": record[7],
        "created_at": record[8] if record[8] else datetime.utcnow()
    }
    mongodb.attendance_records.insert_one(doc)

print("Migration complete!")

sqlite_conn.close()
```

---

## ✅ Migration Checklist

- [ ] MongoDB Atlas account created
- [ ] Cluster created (free tier)
- [ ] Database user created
- [ ] IP whitelisted
- [ ] Connection string obtained
- [ ] Environment variables set
- [ ] MongoDB drivers installed
- [ ] Code updated for MongoDB
- [ ] Indexes created
- [ ] Tested connection
- [ ] Data migrated (if needed)
- [ ] All endpoints tested

---

## 🎯 MongoDB vs SQL Differences

### **Key Differences:**

1. **No Tables** → Collections
2. **No Rows** → Documents
3. **No Foreign Keys** → Store ObjectId strings
4. **No JOINs** → Manual lookups or embedded documents
5. **Flexible Schema** → Documents can have different fields

### **Advantages for This Project:**

- Face encodings are JSON arrays → Perfect fit
- Flexible schema → Easy to add fields
- Fast queries → Good performance
- Easy to scale → Horizontal scaling

---

**Your system is now ready for MongoDB! 🎉**

