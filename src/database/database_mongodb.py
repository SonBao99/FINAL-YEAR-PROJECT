"""
MongoDB database adapter for the attendance system
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from typing import Optional
from datetime import datetime
import json

# Try to load from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", os.getenv("DATABASE_URL", "mongodb://localhost:27017/"))
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "attendance_db")

# Global client
client: Optional[AsyncIOMotorClient] = None
database = None

def get_mongodb_client():
    """Get MongoDB client (sync version)"""
    global client
    if client is None:
        client = MongoClient(MONGODB_URL)
    return client

def get_mongodb_database():
    """Get MongoDB database"""
    global database
    if database is None:
        client = get_mongodb_client()
        database = client[DATABASE_NAME]
    return database

async def get_async_mongodb():
    """Get async MongoDB client and database"""
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGODB_URL)
    return client[DATABASE_NAME]

def create_indexes():
    """Create indexes for better performance"""
    db = get_mongodb_database()
    
    # Students collection indexes
    db.students.create_index("student_id", unique=True)
    db.students.create_index("email", unique=True)
    db.students.create_index("is_active")
    
    # Courses collection indexes
    db.courses.create_index("course_code", unique=True)
    db.courses.create_index("is_active")
    
    # Sessions collection indexes
    db.sessions.create_index("course_id")
    db.sessions.create_index("is_active")
    db.sessions.create_index("scheduled_start")
    
    # Attendance records indexes
    db.attendance_records.create_index("student_id")
    db.attendance_records.create_index("session_id")
    db.attendance_records.create_index([("student_id", 1), ("session_id", 1)], unique=True)
    db.attendance_records.create_index("check_in_time")

def get_db():
    """Dependency to get MongoDB database"""
    return get_mongodb_database()

async def get_async_db():
    """Async dependency to get MongoDB database"""
    return await get_async_mongodb()

# Initialize indexes on import
try:
    create_indexes()
except Exception as e:
    print(f"Warning: Could not create indexes: {e}")

