# Render Deployment - Quick Reference

## 🎯 One Command Deploy

After setting up MongoDB Atlas and pushing to GitHub:

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Deploy!

---

## 📋 Required Environment Variables

Set in Render dashboard:

```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/attendance_db?retryWrites=true&w=majority
MONGODB_DATABASE=attendance_db
```

---

## 🔧 Build & Start Commands

**Build:**
```bash
pip install -r requirements.txt
```

**Start:**
```bash
uvicorn attendance_api:app --host 0.0.0.0 --port $PORT
```

---

## 🌐 Your Live URL

After deployment:
```
https://your-app-name.onrender.com
```

---

## 📚 Full Guide

See `RENDER_DEPLOYMENT.md` for complete instructions.

---

**Render is perfect for this project!** ✅

