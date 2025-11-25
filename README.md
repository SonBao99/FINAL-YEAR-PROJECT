# AI-Powered Face Recognition Attendance System

A complete attendance tracking system using face recognition technology with liveness detection to prevent spoofing.

## 📁 Project Structure

```
FINAL-YEAR-PROJECT/
├── src/                          # Source code
│   ├── api/                      # API and Kiosk application
│   │   ├── attendance_api.py     # Main FastAPI server
│   │   ├── kiosk_app.py          # Kiosk camera application
│   │   ├── websocket_manager.py  # WebSocket manager
│   │   ├── attendance_tracker.py # Core attendance logic
│   │   └── web_dashboard.html    # Web dashboard
│   ├── database/                 # Database adapters
│   │   ├── database.py           # SQL database (SQLite/PostgreSQL)
│   │   └── database_mongodb.py   # MongoDB adapter
│   ├── models/                   # Data models
│   │   ├── models.py             # SQL models
│   │   └── models_mongodb.py     # MongoDB models
│   └── scripts/                  # Utility scripts
│       ├── enroll.py             # Student enrollment script
│       └── start_session.py      # Session management script
│
├── config/                       # Configuration files
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker configuration
│   ├── Procfile                  # Platform deployment config
│   ├── render.yaml               # Render deployment config
│   └── cleanup.sh                # Cleanup script
│
├── docs/                         # Documentation
│   ├── demo/                     # Demo guides
│   │   ├── DEMO_GUIDE.md
│   │   └── DEMO_QUICK_REFERENCE.md
│   ├── deployment/               # Deployment guides
│   │   ├── RENDER_DEPLOYMENT.md
│   │   ├── DATABASE_MIGRATION.md
│   │   └── MONGODB_MIGRATION.md
│   ├── technical/                # Technical documentation
│   │   ├── TECHNICAL_EXPLANATION.md
│   │   └── SIMPLE_TECHNICAL_EXPLANATION.md
│   ├── QUICK_START_GUIDE.md
│   ├── INSTALLATION_NOTES.md
│   └── TESTING_GUIDE.md
│
├── tests/                        # Test files
│   ├── test_attendance.py        # Unit tests
│   └── run_all_tests.py          # Test runner
│
├── tools/                        # Utility tools
│   └── evaluate_recognition.py   # Evaluation tool
│
└── assets/                       # Static assets
    ├── cascades/                 # Haar cascade files
    ├── images/                   # Sample images
    └── photos/                   # Student photos
```

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
pip install -r config/requirements.txt
```

### **2. Start API Server**

```bash
python3 -m uvicorn src.api.attendance_api:app --reload --port 8000
```

### **3. Access Dashboard**

Open browser: `http://localhost:8000/`

### **4. Enroll a Student**

```bash
python3 src/scripts/enroll.py
```

### **5. Create a Session**

```bash
python3 src/scripts/start_session.py
```

### **6. Start Kiosk**

```bash
python3 src/api/kiosk_app.py --api http://localhost:8000 --camera 0 --session 1
```

## 📚 Documentation

- **Demo Guide:** `docs/demo/DEMO_GUIDE.md`
- **Deployment:** `docs/deployment/RENDER_DEPLOYMENT.md`
- **Technical:** `docs/technical/TECHNICAL_EXPLANATION.md`
- **Quick Start:** `docs/QUICK_START_GUIDE.md`

## 🛠️ Technologies

- **Backend:** FastAPI (Python)
- **Database:** SQLite (dev) / PostgreSQL / MongoDB
- **Face Recognition:** dlib + face_recognition
- **Liveness Detection:** MediaPipe
- **Frontend:** HTML/CSS/JavaScript
- **Real-time:** WebSocket

## 📝 License

This project is part of a final year project.

---

**For detailed information, see the documentation in the `docs/` folder.**

