# Project Structure Guide

## 📁 Directory Organization

### **src/** - Source Code
All application code organized by functionality.

#### **src/api/** - API and Application Layer
- `attendance_api.py` - Main FastAPI server with all endpoints
- `kiosk_app.py` - Kiosk camera application with liveness detection
- `websocket_manager.py` - WebSocket connection manager
- `attendance_tracker.py` - Core attendance tracking logic
- `web_dashboard.html` - Web dashboard interface

#### **src/database/** - Database Layer
- `database.py` - SQL database adapter (SQLite/PostgreSQL)
- `database_mongodb.py` - MongoDB database adapter

#### **src/models/** - Data Models
- `models.py` - SQLAlchemy models for SQL databases
- `models_mongodb.py` - Pydantic models for MongoDB

#### **src/scripts/** - Utility Scripts
- `enroll.py` - Student enrollment script
- `start_session.py` - Session creation and management script

---

### **config/** - Configuration Files
All configuration and deployment files.

- `requirements.txt` - Python package dependencies
- `Dockerfile` - Docker container configuration
- `Procfile` - Platform deployment configuration
- `render.yaml` - Render.com deployment config
- `cleanup.sh` - Codebase cleanup script

---

### **docs/** - Documentation
Organized by category.

#### **docs/demo/** - Demo Documentation
- `DEMO_GUIDE.md` - Complete demo guide
- `DEMO_QUICK_REFERENCE.md` - Quick demo reference

#### **docs/deployment/** - Deployment Guides
- `RENDER_DEPLOYMENT.md` - Render deployment guide
- `DATABASE_MIGRATION.md` - Database migration guide
- `MONGODB_MIGRATION.md` - MongoDB setup guide
- `DEPLOYMENT_GUIDE.md` - General deployment guide

#### **docs/technical/** - Technical Documentation
- `TECHNICAL_EXPLANATION.md` - Full technical explanation
- `SIMPLE_TECHNICAL_EXPLANATION.md` - Simple tech overview

#### **docs/** - Other Documentation
- `QUICK_START_GUIDE.md` - Quick start guide
- `INSTALLATION_NOTES.md` - Installation instructions
- `TESTING_GUIDE.md` - Testing guide
- `CODEBASE_REVIEW.md` - Codebase review
- `project_schedule.md` - Project schedule

---

### **tests/** - Test Files
- `test_attendance.py` - Unit tests for attendance tracker
- `run_all_tests.py` - Test runner script

---

### **tools/** - Utility Tools
- `evaluate_recognition.py` - Face recognition evaluation tool

---

### **assets/** - Static Assets
- `cascades/` - Haar cascade XML files for face detection
- `images/` - Sample/test images
- `photos/` - Student enrollment photos (gitignored)

---

## 🔄 Import Path Changes

After reorganization, imports have been updated:

**Old:**
```python
from database import get_db
from models import Student
```

**New:**
```python
from src.database.database import get_db
from src.models.models import Student
```

---

## 🚀 Running the Application

### **Local Development:**

```bash
# Start API
python3 -m uvicorn src.api.attendance_api:app --reload --port 8000

# Run scripts
python3 src/scripts/enroll.py
python3 src/scripts/start_session.py
python3 src/api/kiosk_app.py --api http://localhost:8000
```

### **Deployment:**

Update paths in deployment configs:
- `config/render.yaml` - Updated
- `config/Procfile` - Updated
- `config/Dockerfile` - Updated

---

## 📝 Notes

- All Python packages have `__init__.py` files for proper imports
- Configuration files reference new paths
- Asset paths updated (student_photos → assets/photos)
- Documentation organized by category

---

**The project is now well-organized and ready for development and deployment! 🎉**

