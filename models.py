# Re-export models from src.models.models for root-level imports
from src.models.models import (
    Base,
    Student,
    Course,
    Session,
    AttendanceRecord,
    Lecturer
)

__all__ = ['Base', 'Student', 'Course', 'Session', 'AttendanceRecord', 'Lecturer']

