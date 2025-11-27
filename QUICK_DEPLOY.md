# Quick Deployment Guide

## 🚀 Fastest Way to Deploy

### For Testing Locally:

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
py -3 start_server.py

# 3. Open browser
# http://localhost:8000/
```

### For Production (Render.com):

1. **Push to GitHub** (if not already)
2. **Go to Render.com** → New Web Service
3. **Connect GitHub repo**
4. **Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python start_server.py`
5. **Deploy!**

### For Production (Railway.app):

1. **Push to GitHub**
2. **Go to Railway.app** → New Project
3. **Deploy from GitHub**
4. **Add PostgreSQL** (optional)
5. **Deploy!**

---

## 📝 Important Notes

1. **Dashboard is served automatically** at root URL (`/`)
2. **API endpoints** are at `/api/*`
3. **WebSocket** is at `/ws/attendance/{session_id}`
4. **Update CORS** in production (see DASHBOARD_DEPLOYMENT.md)

---

## 🔧 Environment Variables

Create `.env` file (optional for local):
```
PORT=8000
HOST=0.0.0.0
ALLOWED_ORIGINS=*
```

For production, set these in your hosting platform.

---

## ✅ Test After Deployment

1. Open dashboard URL
2. Check all tabs load
3. Test creating a course
4. Test enrolling a student
5. Test creating a session
6. Verify WebSocket connects

---

**See DASHBOARD_DEPLOYMENT.md for detailed instructions!**

