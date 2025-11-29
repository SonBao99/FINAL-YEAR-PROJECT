# AI-Powered Face Recognition Attendance System

A complete attendance tracking system using face recognition technology with liveness detection to prevent spoofing. Features a modern web dashboard with real-time updates via WebSocket.

## ✨ Features

- **Face Recognition**: Real-time face detection and recognition using dlib and face_recognition
- **Liveness Detection**: MediaPipe-based anti-spoofing to prevent photo/video attacks
- **Web Dashboard**: Modern, responsive dashboard with real-time attendance updates
- **Kiosk Mode**: Standalone camera application for attendance check-in
- **Multi-Database Support**: SQLite (dev), PostgreSQL, and MongoDB
- **Real-time Updates**: WebSocket integration for live attendance tracking
- **Export Functionality**: CSV and Excel export for attendance records
- **Analytics**: Charts and graphs for attendance trends and statistics

## 📁 Project Structure

```
FINAL-YEAR-PROJECT/
├── src/                          # Source code
│   ├── api/                      # API and Kiosk application
│   │   ├── attendance_api.py     # Main FastAPI server (src version)
│   │   ├── kiosk_app.py          # Kiosk camera application
│   │   ├── websocket_manager.py  # WebSocket manager
│   │   ├── attendance_tracker.py # Core attendance logic
│   │   └── web_dashboard.html    # Web dashboard (src version)
│   ├── database/                 # Database adapters
│   │   ├── database.py           # SQL database (SQLite/PostgreSQL)
│   │   └── database_mongodb.py  # MongoDB adapter
│   ├── models/                   # Data models
│   │   ├── models.py             # SQL models
│   │   └── models_mongodb.py     # MongoDB models
│   └── scripts/                  # Utility scripts
│       ├── enroll.py             # Student enrollment script
│       └── start_session.py      # Session management script
│
├── attendance_api.py             # Root-level FastAPI server
├── database.py                   # Root-level database adapter
├── models.py                     # Root-level models (re-exports)
├── websocket_manager.py          # Root-level WebSocket manager
├── web_dashboard.html            # Root-level web dashboard
│
├── config/                       # Configuration files
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker configuration
│   └── Procfile                  # Platform deployment config
│
├── docs/                         # Documentation
│   ├── demo/                      # Demo guides
│   ├── deployment/             # Deployment guides
│   └── technical/              # Technical documentation
│
├── tests/                        # Test files
│   ├── test_attendance.py        # Unit tests
│   └── run_all_tests.py          # Test runner
│
├── tools/                        # Utility tools
│   └── evaluate_recognition.py   # Evaluation tool
│
├── assets/                       # Static assets
│   ├── cascades/                 # Haar cascade files
│   ├── images/                   # Sample images
│   └── photos/                   # Student photos
│
├── requirements.txt              # Root-level dependencies
├── Dockerfile                    # Root Dockerfile
└── Procfile                      # Root Procfile
```

## 🚀 Quick Start

### **Prerequisites**

- Python 3.11 or higher
- Webcam/camera (for kiosk mode)
- pip package manager

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

**Note:** On Windows, if `dlib` installation fails, you can use `dlib-bin` which is already in requirements.txt.

### **2. Start API Server**

**Option A: Using uvicorn directly (recommended for development)**
```bash
python -m uvicorn attendance_api:app --reload --port 8000
```

**Option B: Using Python script**
```bash
python -c "import uvicorn; uvicorn.run('attendance_api:app', host='0.0.0.0', port=8000, reload=True)"
```

The server will start at: `http://localhost:8000`

### **3. Access Web Dashboard**

Open your browser and navigate to:
- **Dashboard**: `http://localhost:8000/`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### **4. Enroll a Student**

```bash
python src/scripts/enroll.py
```

Or use the root-level script:
```bash
python -c "import sys; sys.path.insert(0, 'src'); from scripts.enroll import main; main()"
```

**When prompted:**
- Enter Student ID (e.g., `STU001`)
- Enter Name (e.g., `John Doe`)
- Enter Email (e.g., `john@example.com`)
- Provide 3-5 image paths (comma-separated or directory path)

### **5. Create a Session**

```bash
python src/scripts/start_session.py
```

**When prompted:**
- Create or select a course
- Enter session details
- Start the session immediately (answer `y`)

### **6. Start Kiosk (Camera Application)**

```bash
python src/api/kiosk_app.py --api http://localhost:8000 --camera 0 --session <SESSION_ID>
```

**Options:**
- `--api`: API server URL (default: http://localhost:8000)
- `--camera`: Camera index (0, 1, 2, etc.)
- `--session`: Session ID to use for attendance
- `--verbose`: Enable verbose logging

## 📚 Documentation

- **Quick Start Guide**: `docs/QUICK_START_GUIDE.md`
- **Demo Guide**: `docs/demo/DEMO_GUIDE.md`
- **Deployment Guide**: `docs/deployment/DEPLOYMENT_GUIDE.md`
- **Technical Explanation**: `docs/technical/TECHNICAL_EXPLANATION.md`
- **Testing Guide**: `docs/TESTING_GUIDE.md`
- **Project Schedule**: `docs/project_schedule.md`

## 🛠️ Technologies

- **Backend Framework**: FastAPI (Python)
- **Database**: 
  - SQLite (development)
  - PostgreSQL (production)
  - MongoDB (alternative)
- **Face Recognition**: 
  - dlib + face_recognition library
  - OpenCV for image processing
- **Liveness Detection**: MediaPipe
- **Frontend**: 
  - HTML5/CSS3/JavaScript
  - Chart.js for analytics
  - Font Awesome icons
- **Real-time Communication**: WebSocket
- **Data Export**: XLSX library for Excel export

## 🎯 Key Features

### Web Dashboard
- Modern, responsive design with dark mode support
- Real-time attendance updates via WebSocket
- Interactive charts and analytics
- Session management interface
- Student enrollment interface
- Course management
- Export functionality (CSV, Excel)
- Search and filtering capabilities

### Kiosk Application
- Real-time face detection and recognition
- Confidence threshold adjustment
- Live camera feed
- Automatic attendance recording
- Event logging

### API Endpoints
- `/api/students` - Student management
- `/api/courses` - Course management
- `/api/sessions` - Session management
- `/api/attendance` - Attendance records
- `/api/recognize` - Face recognition endpoint
- `/health` - Health check
- `/docs` - Interactive API documentation

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///./attendance.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/attendance

# API Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=False

# CORS
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000

# MongoDB (optional)
USE_MONGODB=false
MONGODB_URL=mongodb://localhost:27017/attendance
```

## 📊 Usage Examples

### Enroll Multiple Students

```bash
# Enroll student with images from a directory
python src/scripts/enroll.py
# Enter: STU001
# Enter: John Doe
# Enter: john@example.com
# Enter: assets/images/john/
```

### Create and Start Session

```bash
python src/scripts/start_session.py
# Follow prompts to create course and session
# Answer 'y' to start session immediately
```

### Run Kiosk with Specific Camera

```bash
# List available cameras first
python -c "import cv2; [print(f'Camera {i}: {\"OK\" if cv2.VideoCapture(i).isOpened() else \"Not available\"}') for i in range(3)]"

# Start kiosk with camera 0
python src/api/kiosk_app.py --api http://localhost:8000 --camera 0 --session 1 --verbose
```

## 🧪 Testing

Run the test suite:

```bash
python tests/run_all_tests.py
```

Or run individual tests:

```bash
python -m pytest tests/
```

## 📦 Deployment

The project supports deployment on various platforms:

- **Render**: See `docs/deployment/RENDER_DEPLOYMENT.md`
- **Railway**: See `RAILWAY_DEPLOYMENT.md`
- **Docker**: Use the provided `Dockerfile`
- **Vercel**: See `VERCEL_DEPLOYMENT.md`

## 🐛 Troubleshooting

### Common Issues

1. **Camera not detected**
   - Check camera permissions
   - Try different camera indices (0, 1, 2)
   - Verify camera is not being used by another application

2. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.11+)
   - Verify you're in the correct directory

3. **Database connection errors**
   - Check DATABASE_URL in .env file
   - Ensure database server is running (for PostgreSQL/MongoDB)
   - Verify database credentials

4. **Face recognition not working**
   - Ensure student is enrolled with 3-5 clear images
   - Check lighting conditions
   - Adjust confidence threshold in kiosk settings

## 📝 License

This project is part of a final year project.

## 🤝 Contributing

This is an academic project. For questions or issues, please refer to the documentation in the `docs/` folder.

---

**For detailed information, see the documentation in the `docs/` folder.**
