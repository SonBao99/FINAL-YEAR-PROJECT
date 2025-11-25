# Quick Demo Reference Card

## 🎯 One-Sentence Summary
**An AI-powered attendance system that automatically recognizes students' faces and records attendance in real-time.**

---

## 🚀 Start Demo (2 commands)

**Terminal 1 - Start API:**
```bash
python3 -m uvicorn attendance_api:app --reload --port 8000
```

**Browser:**
```
http://localhost:8000/
```

---

## 📋 5-Minute Demo Flow

1. **Show Dashboard** (30 sec)
   - "This is where teachers manage everything"
   - Show tabs: Dashboard, Sessions, Students, Courses

2. **Create Course** (30 sec)
   - Click "+" → "Create Course"
   - Fill: CS101, Intro to CS, Dr. Smith
   - "Now we have a course"

3. **Create Session** (30 sec)
   - Click "+" → "Create Session"
   - Select course, fill details
   - Click "Start" button
   - "Session is now active"

4. **Enroll Student** (1 min)
   - Click "+" → "Enroll Student"
   - Fill: DEMO001, John Doe, email
   - Upload 3 photos
   - "System creates face profile"

5. **Show Kiosk** (1 min)
   - Click "Start Camera"
   - "Students look here to check in"
   - Show face detection
   - "Green rectangle = face detected"

6. **Show Real-Time** (1 min)
   - Add manual entry OR use kiosk
   - "Watch dashboard update automatically"
   - Show stats updating
   - "No refresh needed - real-time!"

7. **Export** (30 sec)
   - Click "Export CSV"
   - "Easy reports for teachers"

---

## 💬 Key Talking Points

- **"Automates attendance"** - No manual roll call
- **"Face recognition"** - Like iPhone Face ID
- **"Liveness detection"** - Prevents photo cheating
- **"Real-time updates"** - Instant feedback
- **"Easy to use"** - Simple web interface
- **"Export reports"** - CSV/Excel for records

---

## ❓ If Asked Technical Questions

**"How does it work?"**
→ Uses face recognition AI to extract facial features, compares with enrolled students, matches with high confidence.

**"What if it doesn't recognize someone?"**
→ Manual entry available, or re-enroll with better photos.

**"Is it secure?"**
→ Yes, liveness detection prevents photo spoofing, data stored locally.

**"Can it handle large classes?"**
→ Yes, processes one at a time, can handle hundreds of students.

---

## 🆘 If Something Breaks

**Dashboard not loading?**
→ Check API is running, refresh browser

**Camera not working?**
→ Show manual entry instead, explain it's a backup feature

**Face not recognized?**
→ "That's why we have manual entry - system is flexible"

---

## ✅ Pre-Demo Checklist

- [ ] API server running
- [ ] Dashboard opens
- [ ] Know how to create course/session
- [ ] Have sample photos ready
- [ ] Tested camera (or ready to show manual entry)

---

**Remember: You built this! Be confident! 🎉**

