# Deploy to Vercel with MongoDB

## 🚀 Quick Start

### **Step 1: Set Up MongoDB Atlas (Free)**

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create a new cluster (Free tier: M0)
4. Create database user:
   - Username: `attendance_user`
   - Password: (generate secure password)
5. Whitelist IP: `0.0.0.0/0` (allow from anywhere)
6. Get connection string:
   - Click "Connect" → "Connect your application"
   - Copy connection string
   - Format: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

### **Step 2: Install Vercel CLI**

```bash
npm i -g vercel
```

### **Step 3: Configure Project**

1. **Update requirements.txt** - Add MongoDB driver:
   ```
   pymongo>=4.6.0
   motor>=3.3.0
   ```

2. **Create vercel.json** (already created)

3. **Set Environment Variables:**
   ```bash
   vercel env add MONGODB_URL
   # Paste your MongoDB Atlas connection string
   
   vercel env add MONGODB_DATABASE
   # Enter: attendance_db
   ```

### **Step 4: Deploy**

```bash
# Login to Vercel
vercel login

# Deploy
vercel

# For production
vercel --prod
```

---

## 📋 Vercel Configuration

### **vercel.json** (Already Created)

This file configures Vercel to run FastAPI as serverless functions.

### **Important Notes:**

1. **Serverless Functions:**
   - Each API route becomes a serverless function
   - Cold starts may occur (first request slower)
   - WebSocket support is limited (consider alternatives)

2. **File Size Limits:**
   - Vercel has limits on function size
   - Face recognition libraries are large
   - May need to optimize or use external API

3. **Environment Variables:**
   - Set in Vercel dashboard
   - Or use `vercel env` command

---

## 🔧 MongoDB Setup

### **Connection String Format:**

```
mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
```

### **Environment Variables:**

```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=attendance_db
```

---

## 🚨 Important Considerations

### **1. Face Recognition on Vercel**

**Challenge:** Face recognition libraries (dlib, face_recognition) are very large and may exceed Vercel's limits.

**Solutions:**

**Option A: Use External API**
- Deploy face recognition to separate service (Railway/Render)
- Call it from Vercel functions

**Option B: Optimize**
- Use lighter face recognition library
- Split into microservices

**Option C: Use Vercel Pro**
- Higher limits
- Better for heavy workloads

### **2. WebSocket Limitations**

Vercel serverless functions don't support WebSocket well.

**Solutions:**
- Use polling instead of WebSocket
- Use external WebSocket service
- Use Vercel's Edge Functions (limited)

### **3. File Uploads**

Vercel has limits on request body size.

**Solutions:**
- Use Vercel Blob storage
- Use external storage (S3, Cloudinary)
- Compress images before upload

---

## 📝 Migration from SQL to MongoDB

### **Update attendance_api.py**

You'll need to update API endpoints to use MongoDB instead of SQLAlchemy.

**Example:**

```python
from database_mongodb import get_db
from models_mongodb import Student
from bson import ObjectId

@app.post("/api/students/enroll")
async def enroll_student(student: StudentCreate):
    db = get_db()
    
    # Insert student
    student_dict = {
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "face_encoding": json.dumps(face_encoding.tolist()),
        "photo_path": str(photo_path),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    result = db.students.insert_one(student_dict)
    return {"id": str(result.inserted_id), **student_dict}
```

---

## 🎯 Recommended Architecture

### **Hybrid Approach (Best for Vercel):**

1. **Vercel:** Frontend + API endpoints (lightweight)
2. **Railway/Render:** Face recognition service (heavy)
3. **MongoDB Atlas:** Database (cloud)

**Flow:**
```
Frontend (Vercel) → API (Vercel) → Face Recognition Service (Railway) → MongoDB Atlas
```

---

## ✅ Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] IP whitelisted
- [ ] Connection string obtained
- [ ] Vercel CLI installed
- [ ] `vercel.json` created
- [ ] Environment variables set
- [ ] Code updated for MongoDB
- [ ] Tested locally
- [ ] Deployed to Vercel

---

## 🧪 Test Locally

```bash
# Set environment variables
export MONGODB_URL="your-connection-string"
export MONGODB_DATABASE="attendance_db"

# Run locally
python3 -m uvicorn attendance_api:app --reload
```

---

## 📊 MongoDB vs PostgreSQL

### **MongoDB Advantages:**
- ✅ Flexible schema (good for face encodings)
- ✅ Easy to scale
- ✅ Good for JSON data
- ✅ Free tier available (MongoDB Atlas)

### **PostgreSQL Advantages:**
- ✅ Better for relational data
- ✅ ACID compliance
- ✅ More mature ecosystem
- ✅ Better for complex queries

**For this project:** MongoDB works well because:
- Face encodings are JSON arrays
- Flexible schema for future features
- Easy to scale

---

## 🔗 Useful Links

- **Vercel Docs:** https://vercel.com/docs
- **MongoDB Atlas:** https://www.mongodb.com/cloud/atlas
- **Motor (Async MongoDB):** https://motor.readthedocs.io/
- **PyMongo:** https://pymongo.readthedocs.io/

---

**Your app will be live on Vercel! 🚀**

