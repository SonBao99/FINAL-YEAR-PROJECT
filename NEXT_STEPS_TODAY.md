# Next Steps for Today - AI Attendance System

## ✅ What's Working
- ✅ API server running on port 8000
- ✅ `enroll.py` script created and functional
- ✅ `start_session.py` script created and working (Session ID 2 created)
- ✅ `kiosk_app.py` script created with command-line args
- ✅ All dependencies installed in virtual environment

## 🎯 Next Tasks for Today (Phase 1.2 & 1.3)

### Task 1: Complete Student Enrollment (15-20 mins)
**Goal:** Enroll yourself or a test student with real face images

**Steps:**
1. **Prepare 3-5 face images:**
   - Take 3-5 photos of your face (or a test subject)
   - Save them in a folder (e.g., `images/` or `test_images/`)
   - Make sure images are clear, well-lit, and show the face clearly
   - Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`

2. **Run enrollment:**
   ```powershell
   # Make sure venv is activated
   .venv310\Scripts\Activate.ps1
   
   # Run enrollment
   python enroll.py
   ```

3. **When prompted:**
   - Student ID: e.g., `STU001` or `0123`
   - Name: Your name or test name
   - Email: test@email.com
   - Image paths: Either:
     - Enter directory path: `images/` (if all images are in one folder)
     - Or enter paths one by one: `images/face1.jpg`, `images/face2.jpg`, etc.

4. **Verify enrollment:**
   - Check API terminal for success messages
   - Visit `http://localhost:8000/api/students` to see enrolled students
   - Or check the database: `attendance.db` → `students` table

---

### Task 2: Start an Active Session (5 mins)
**Goal:** Create and start a session for testing

**Steps:**
```powershell
python start_session.py
```

**When prompted:**
- Use existing course? `n` (create new)
- Course code: e.g., `TEST101`
- Course name: e.g., `Test Course`
- Lecturer: Your name
- Session name: e.g., `Test Session 1`
- Start time: `now` (or specific time)
- **IMPORTANT:** When asked "Do you want to start the session now?" → Answer `y` (yes)

**Note the Session ID** - you'll need it for the kiosk!

---

### Task 3: Fix Camera Issue & Test Kiosk (20-30 mins)
**Goal:** Get the kiosk working with your webcam

**Issue:** Camera index 0 might not be available

**Solutions to try:**

1. **Check available cameras:**
   ```powershell
   python -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
   ```

2. **Try different camera indices:**
   ```powershell
   # Try camera 1
   python kiosk_app.py --api http://localhost:8000 --camera 1 --session 2 --verbose
   
   # Or camera 2
   python kiosk_app.py --api http://localhost:8000 --camera 2 --session 2 --verbose
   ```

3. **If no webcam available:**
   - You can test the API endpoints manually
   - Or use a phone as a webcam (apps like DroidCam, iVCam)
   - Or skip camera testing for now and verify API works

4. **Once camera works:**
   - Point camera at your enrolled face
   - Wait for recognition (3-second cooldown between attempts)
   - Should see "Welcome [Your Name]!" message
   - Check API terminal for check-in logs

---

### Task 4: Verify Database Records (5 mins)
**Goal:** Confirm attendance was recorded

**Option 1: Using SQLite Browser**
- Open `attendance.db` with DB Browser for SQLite
- Check `attendance_records` table
- Should see your check-in record

**Option 2: Using Python**
```powershell
python -c "import sqlite3; conn = sqlite3.connect('attendance.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM attendance_records'); print(cursor.fetchall()); conn.close()"
```

**Option 3: Using API**
- Visit: `http://localhost:8000/api/sessions/{session_id}/attendance`
- Should see your attendance record

---

## 📝 Quick Reference Commands

```powershell
# Activate virtual environment
.venv310\Scripts\Activate.ps1

# Enroll a student
python enroll.py

# Create and start session
python start_session.py

# Start kiosk (replace X with session ID, Y with camera index)
python kiosk_app.py --api http://localhost:8000 --camera Y --session X --verbose

# Check enrolled students
python -c "import requests; print(requests.get('http://localhost:8000/api/students').json())"

# Check sessions
python -c "import requests; print(requests.get('http://localhost:8000/api/sessions').json())"
```

---

## 🎯 Success Criteria for Today

By end of today, you should have:
- [ ] At least 1 student enrolled with 3-5 face images
- [ ] At least 1 active session created and started
- [ ] Kiosk window opens (even if camera doesn't work, window should open)
- [ ] If camera works: Successfully recognized face and checked in
- [ ] Verified attendance record in database

---

## 🐛 Troubleshooting

### No camera available?
- **Option A:** Test API endpoints manually using Postman or curl
- **Option B:** Use phone as webcam (DroidCam, iVCam apps)
- **Option C:** Focus on enrollment and session creation today, test camera tomorrow

### Enrollment fails?
- Check image paths are correct
- Ensure images contain clear faces
- Check API is running
- Look at API terminal for error messages

### Session not starting?
- Make sure to answer `y` when asked to start session
- Check session ID is correct
- Verify session is active: `GET /api/sessions` should show `is_active: true`

---

## 📊 Progress Tracking

**Milestone 1 Progress: ~60% Complete**

- ✅ Phase 1.0: Environment & Setup (100%)
- ✅ Phase 1.1: Scripts Created (100%)
- ⏳ Phase 1.2: API Functionality Testing (50% - scripts work, need real data)
- ⏳ Phase 1.3: Full System Test (0% - need to complete enrollment first)

**Next Milestone:** Milestone 2 - Liveness & Security (Due: Sat, Nov 15)

---

**Good luck! Focus on getting enrollment and basic kiosk working today.** 🚀

