# Deployment Guide - Deploy Your Attendance System Live

## 🚀 Quick Deployment Options

### **Option 1: Railway (Recommended - Easiest)**
✅ Free tier available  
✅ PostgreSQL included  
✅ Auto-deploys from GitHub  
✅ Easy setup

### **Option 2: Render**
✅ Free tier available  
✅ PostgreSQL included  
✅ Good for Python apps

### **Option 3: Heroku**
⚠️ No free tier (paid only)  
✅ Well-established platform

### **Option 4: DigitalOcean App Platform**
✅ Good pricing  
✅ PostgreSQL available

---

## 📋 Pre-Deployment Checklist

- [ ] Migrate to PostgreSQL (see DATABASE_MIGRATION.md)
- [ ] Update environment variables
- [ ] Test locally with PostgreSQL
- [ ] Prepare static files
- [ ] Set up GitHub repository (if using Git deploy)

---

## 🚂 Option 1: Deploy to Railway (Recommended)

### **Step 1: Create Railway Account**
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"

### **Step 2: Add PostgreSQL Database**
1. Click "New" → "Database" → "PostgreSQL"
2. Railway will create a PostgreSQL database
3. Note the connection string (will be in environment variables)

### **Step 3: Deploy Your App**
1. Click "New" → "GitHub Repo"
2. Select your repository
3. Railway will detect it's a Python app

### **Step 4: Configure Environment Variables**
In Railway dashboard, add these environment variables:

```
DATABASE_URL=<your-postgres-connection-string>
PORT=8000
API_BASE_URL=https://your-app-name.railway.app
```

### **Step 5: Configure Build & Start Commands**
In Railway settings:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn attendance_api:app --host 0.0.0.0 --port $PORT
```

### **Step 6: Deploy**
Railway will automatically deploy. Your app will be live at:
`https://your-app-name.railway.app`

---

## 🎨 Option 2: Deploy to Render

### **Step 1: Create Render Account**
1. Go to https://render.com
2. Sign up with GitHub

### **Step 2: Create PostgreSQL Database**
1. Go to "New" → "PostgreSQL"
2. Create database
3. Note connection string

### **Step 3: Create Web Service**
1. Go to "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn attendance_api:app --host 0.0.0.0 --port $PORT`

### **Step 4: Set Environment Variables**
```
DATABASE_URL=<postgres-connection-string>
PORT=8000
```

### **Step 5: Deploy**
Render will deploy automatically. Your app will be at:
`https://your-app-name.onrender.com`

---

## 🐳 Option 3: Docker Deployment (Any Platform)

### **Create Dockerfile**

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "attendance_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Create .dockerignore**
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.db
*.sqlite
.env
venv/
.venv/
student_photos/
kiosk_snapshots/
```

### **Build and Run Locally (Test)**
```bash
docker build -t attendance-system .
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... attendance-system
```

---

## 🔧 Update Code for Production

### **1. Update database.py**

Already done! Your `database.py` supports PostgreSQL via `DATABASE_URL` environment variable.

### **2. Create Procfile (for Heroku/Railway)**

Create `Procfile`:
```
web: uvicorn attendance_api:app --host 0.0.0.0 --port $PORT
```

### **3. Update CORS Settings**

In `attendance_api.py`, update CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "http://localhost:8000",  # For local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **4. Handle Static Files**

For production, you might want to serve static files differently. Update `attendance_api.py`:

```python
from fastapi.staticfiles import StaticFiles

# Serve static files (if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")
```

---

## 🌐 Update Frontend for Production

### **Update API_BASE_URL in web_dashboard.html**

Change line 1156:
```javascript
const API_BASE_URL = window.location.origin; // Auto-detect
// Or hardcode: const API_BASE_URL = 'https://your-domain.com';
```

This makes it work automatically in production.

---

## 📝 Environment Variables Needed

Create `.env` file (don't commit this!):

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-here
API_BASE_URL=https://your-domain.com
PORT=8000
```

Add `.env` to `.gitignore`:
```
.env
*.db
*.sqlite
__pycache__/
*.pyc
```

---

## 🔒 Security Considerations

### **1. Add Authentication (Future)**
- Add user authentication
- Protect admin endpoints
- Use JWT tokens

### **2. HTTPS Only**
- Most platforms provide HTTPS automatically
- Ensure all API calls use HTTPS

### **3. Rate Limiting**
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### **4. Input Validation**
Already using Pydantic models - good!

---

## 📊 Monitoring & Logging

### **Add Logging**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### **Health Check Endpoint**
Add to `attendance_api.py`:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}
```

---

## 🧪 Testing Before Deploy

### **Test Locally with PostgreSQL**
1. Install PostgreSQL locally
2. Create database
3. Set `DATABASE_URL` environment variable
4. Run: `python3 -m uvicorn attendance_api:app --reload`
5. Test all endpoints

### **Test Production Build**
```bash
# Build Docker image
docker build -t attendance-test .

# Run with production settings
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  attendance-test
```

---

## 🚨 Common Issues & Solutions

### **Issue: Database Connection Failed**
**Solution:** Check `DATABASE_URL` format:
```
postgresql://username:password@host:port/database
```

### **Issue: Port Already in Use**
**Solution:** Use `$PORT` environment variable (platforms set this)

### **Issue: Static Files Not Loading**
**Solution:** Ensure paths are relative or use CDN

### **Issue: WebSocket Not Working**
**Solution:** Check platform supports WebSockets (Railway/Render do)

---

## 📈 Post-Deployment

### **1. Test Your Live Site**
- Visit your deployed URL
- Test all features
- Check WebSocket connection
- Test face recognition

### **2. Monitor Performance**
- Check logs in platform dashboard
- Monitor database connections
- Watch for errors

### **3. Set Up Backups**
- Most platforms auto-backup databases
- Export data regularly
- Keep local backups

---

## 🎯 Quick Start Commands

### **Railway:**
```bash
# Install Railway CLI (optional)
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

### **Render:**
Just connect GitHub repo - auto-deploys!

---

## ✅ Deployment Checklist

- [ ] Database migrated to PostgreSQL
- [ ] Environment variables set
- [ ] Code updated for production
- [ ] CORS configured
- [ ] Static files handled
- [ ] Health check endpoint added
- [ ] Tested locally with PostgreSQL
- [ ] Deployed to platform
- [ ] Tested live site
- [ ] Monitored for errors

---

**Your system will be live and accessible from anywhere! 🌍**

