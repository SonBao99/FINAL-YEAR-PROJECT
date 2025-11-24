# Deploy to Render with MongoDB

## 🚀 Why Render?

✅ **Perfect for Python apps** - Full Python runtime support  
✅ **Handles heavy libraries** - Face recognition works great  
✅ **WebSocket support** - Real-time updates work  
✅ **Free tier available** - PostgreSQL + Web service  
✅ **Easy deployment** - Connect GitHub, auto-deploys  
✅ **MongoDB support** - Works with MongoDB Atlas  

---

## 📋 Quick Start (10 minutes)

### **Step 1: Set Up MongoDB Atlas (5 min)**

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up (free)
3. Create cluster:
   - Click "Build a Database"
   - Choose **FREE** tier (M0)
   - Select region
   - Name: `attendance-cluster`
   - Click "Create"
4. Create database user:
   - Go to "Database Access"
   - "Add New Database User"
   - Username: `attendance_user`
   - Password: Generate secure password (save it!)
   - Click "Add User"
5. Whitelist IP:
   - Go to "Network Access"
   - "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"
6. Get connection string:
   - Go to "Database" → "Connect"
   - "Connect your application"
   - Copy connection string:
     ```
     mongodb+srv://attendance_user:<password>@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - Replace `<password>` with your actual password
   - Add database name: `mongodb+srv://...mongodb.net/attendance_db?retryWrites=true&w=majority`

---

### **Step 2: Prepare Your Code**

Your code is already ready! Just make sure:

1. ✅ `requirements.txt` includes MongoDB drivers (already done)
2. ✅ `.gitignore` excludes sensitive files (already done)
3. ✅ Code supports MongoDB (see `database_mongodb.py`)

---

### **Step 3: Push to GitHub**

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Push to GitHub
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

---

### **Step 4: Deploy on Render**

1. **Sign up:**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select your repo

3. **Configure Service:**
   - **Name:** `attendance-system` (or your choice)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn attendance_api:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** Free (or paid for better performance)

4. **Set Environment Variables:**
   Click "Advanced" → "Add Environment Variable":
   - **Key:** `MONGODB_URL`
   - **Value:** Your MongoDB Atlas connection string
   
   - **Key:** `MONGODB_DATABASE`
   - **Value:** `attendance_db`
   
   - **Key:** `PORT`
   - **Value:** `8000` (Render sets this automatically, but good to have)

5. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Wait 5-10 minutes for first deployment

6. **Your app is live!**
   - URL: `https://your-app-name.onrender.com`
   - Dashboard: `https://your-app-name.onrender.com/`

---

## 🔧 Configuration Files

### **render.yaml** (Optional - for Infrastructure as Code)

Create `render.yaml`:

```yaml
services:
  - type: web
    name: attendance-system
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn attendance_api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URL
        sync: false
      - key: MONGODB_DATABASE
        value: attendance_db
      - key: PORT
        value: 8000
```

---

## 📝 Update Code for MongoDB

### **Option 1: Use MongoDB Adapter (Recommended)**

Update `attendance_api.py` to use MongoDB:

```python
# At the top, add:
from database_mongodb import get_db, create_indexes
from models_mongodb import Student, Course, Session, AttendanceRecord
from bson import ObjectId
import json

# Update enrollment endpoint:
@app.post("/api/students/enroll")
async def enroll_student(student: StudentCreate):
    db = get_db()
    
    # Process face encoding
    image_data = base64.b64decode(student.photo_base64)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_image)
    
    if not face_encodings:
        raise HTTPException(status_code=400, detail="No face detected")
    
    face_encoding = face_encodings[0]
    
    # Save photo
    photos_dir = Path("student_photos")
    photos_dir.mkdir(exist_ok=True)
    photo_filename = f"{student.student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    photo_path = photos_dir / photo_filename
    cv2.imwrite(str(photo_path), image)
    
    # Create student document
    student_doc = {
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "face_encoding": json.dumps(face_encoding.tolist()),
        "photo_path": str(photo_path),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    # Insert into MongoDB
    result = db.students.insert_one(student_doc)
    student_doc["id"] = str(result.inserted_id)
    
    return student_doc
```

### **Option 2: Keep SQL Support, Add MongoDB Option**

Update `database.py` to support both:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Check which database to use
USE_MONGODB = os.getenv("USE_MONGODB", "false").lower() == "true"

if USE_MONGODB:
    from database_mongodb import get_db, create_indexes
    # Use MongoDB
else:
    from database import get_db, create_tables
    # Use SQL
```

---

## 🧪 Test Before Deploying

### **Test Locally with MongoDB:**

```bash
# Set environment variables
export MONGODB_URL="your-mongodb-connection-string"
export MONGODB_DATABASE="attendance_db"

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn attendance_api:app --reload
```

Visit: http://localhost:8000

---

## 🚨 Important Notes

### **1. Free Tier Limitations:**

- **Spins down after 15 min inactivity** - First request after spin-down is slow (~30s)
- **512 MB RAM** - Should be enough for face recognition
- **Limited CPU** - May be slower than paid tier

**Solution:** Use Render's paid tier ($7/month) for production, or accept spin-down delays.

### **2. File Storage:**

Render's file system is **ephemeral** - files are deleted on restart.

**Solution:** Use external storage:
- **Vercel Blob** (if using Vercel)
- **AWS S3**
- **Cloudinary** (for images)
- **MongoDB GridFS** (store photos in MongoDB)

### **3. WebSocket Support:**

Render **supports WebSockets** ✅ - Your real-time updates will work!

### **4. Environment Variables:**

Set in Render dashboard:
- `MONGODB_URL` - Your MongoDB Atlas connection string
- `MONGODB_DATABASE` - Database name (e.g., `attendance_db`)

---

## 📊 Monitoring & Logs

### **View Logs:**

1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. See real-time logs

### **Health Check:**

Your `/health` endpoint will work:
```
https://your-app.onrender.com/health
```

---

## 🔄 Auto-Deploy

Render automatically deploys when you push to GitHub:

1. Push code to GitHub
2. Render detects changes
3. Builds automatically
4. Deploys new version
5. Your app updates!

---

## 🎯 Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] IP whitelisted
- [ ] Connection string obtained
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] Environment variables set
- [ ] Build command configured
- [ ] Start command configured
- [ ] Deployed successfully
- [ ] Tested live site
- [ ] Health check working

---

## 🆘 Troubleshooting

### **Issue: Build fails**
**Solution:** Check logs, ensure all dependencies in `requirements.txt`

### **Issue: Application error**
**Solution:** Check logs, verify MongoDB connection string

### **Issue: Slow first request**
**Solution:** Normal on free tier (spin-down). Consider paid tier.

### **Issue: WebSocket not working**
**Solution:** Render supports WebSockets. Check your code.

### **Issue: Files disappearing**
**Solution:** Use external storage (S3, Cloudinary, GridFS)

---

## 💰 Pricing

### **Free Tier:**
- ✅ 750 hours/month
- ✅ 512 MB RAM
- ✅ Spins down after inactivity
- ✅ Perfect for testing

### **Starter ($7/month):**
- ✅ Always on
- ✅ 512 MB RAM
- ✅ Better performance
- ✅ Good for production

---

## ✅ You're Ready!

Follow these steps and your app will be live on Render in minutes! 🚀

**Your app URL:** `https://your-app-name.onrender.com`

