# Quick Start Guide - Complete Today's Tasks

## 🚀 Fast Track to Complete Phase 1.2 & 1.3

### Step 1: Enroll a Student (5 mins)

You have sample images in the `images/` folder! Let's use them:

```powershell
# Make sure venv is activated
.venv310\Scripts\Activate.ps1

# Run enrollment
python enroll.py
```

**When prompted, enter:**
- Student ID: `STU001`
- Name: `Test Student`
- Email: `test@example.com`
- Image paths: `images/` (this will use all images in the folder)

**OR** enter paths individually:
- Image 1: `images/sample_image.png`
- Image 2: `images/sample_image1.png`
- Image 3: `images/sample_image2.jpg`
- Image 4: (press Enter to skip)
- Image 5: (press Enter to skip)

**Verify:** Check `http://localhost:8000/api/students` in browser

---

### Step 2: Create & Start Session (2 mins)

```powershell
python start_session.py
```

**Quick answers:**
- Use existing course? `n`
- Course code: `TEST101`
- Course name: `Test Course`
- Lecturer: `Test Lecturer`
- Description: (press Enter)
- Session name: `Test Session`
- Start time: `now`
- End time: (press Enter for default)
- Room: `Room 101`
- **Start now?** `y` ← **IMPORTANT: Say yes!**

**Note the Session ID** (probably 2 or 3)

---

### Step 3: Test Kiosk (10-15 mins)

**First, check which camera works:**
```powershell
python -c "import cv2; [print(f'Camera {i}: Works' if cv2.VideoCapture(i).isOpened() else f'Camera {i}: Not available') for i in range(3)]"
```

**Then start kiosk with working camera:**
```powershell
# Replace X with your session ID from Step 2
python kiosk_app.py --api http://localhost:8000 --camera 0 --session X --verbose
```

**If camera 0 doesn't work, try:**
```powershell
python kiosk_app.py --api http://localhost:8000 --camera 1 --session X --verbose
```

**What to expect:**
- Kiosk window opens
- Shows camera feed (if camera works)
- Shows "Session ID: X" in green
- Detects faces with green rectangles
- Every 3 seconds, tries to recognize face
- If recognized: Shows "Welcome Test Student!"

---

### Step 4: Verify Success (2 mins)

**Check attendance record:**
```powershell
# Replace X with your session ID
python -c "import requests; import json; r = requests.get('http://localhost:8000/api/sessions/X/attendance'); print(json.dumps(r.json(), indent=2))"
```

**Or visit in browser:**
- `http://localhost:8000/api/sessions/X/attendance`
- Should show your attendance record!

---

## ✅ Checklist

- [ ] Student enrolled successfully
- [ ] Session created and started (is_active = true)
- [ ] Kiosk window opens
- [ ] Face detected (green rectangle)
- [ ] Face recognized (shows welcome message)
- [ ] Attendance record in database/API

---

## 🎉 If Everything Works

**Congratulations!** You've completed:
- ✅ Phase 1.2: API Functionality (Data)
- ✅ Phase 1.3: Debug & Full System Test

**Next up:** Milestone 2 - Liveness & Security (add Mediapipe for anti-spoofing)

---

## 🆘 Quick Troubleshooting

**"No module named 'requests'"**
→ Make sure venv is activated: `.venv310\Scripts\Activate.ps1`

**"Camera index out of range"**
→ Try different camera index (0, 1, 2) or skip camera testing for now

**"Face not recognized"**
→ Make sure you enrolled with clear face images
→ Ensure good lighting when testing
→ Wait 3 seconds between recognition attempts

**"Session not found"**
→ Make sure session is started (is_active = true)
→ Check session ID is correct

---

**Ready? Start with Step 1!** 🚀

