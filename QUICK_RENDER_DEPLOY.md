# Quick Render Deployment (5 Minutes)

## 🚀 Fast Track

### **1. MongoDB Atlas (2 min)**
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up → Create free cluster
3. Create user → Whitelist IP (0.0.0.0/0)
4. Get connection string

### **2. Push to GitHub (1 min)**
```bash
git add .
git commit -m "Deploy to Render"
git push
```

### **3. Deploy on Render (2 min)**
1. Go to https://render.com
2. Sign up with GitHub
3. New → Web Service
4. Connect repo
5. Configure:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `uvicorn attendance_api:app --host 0.0.0.0 --port $PORT`
6. Add env vars:
   - `MONGODB_URL` = your connection string
   - `MONGODB_DATABASE` = `attendance_db`
7. Deploy!

**Done!** Your app: `https://your-app.onrender.com` 🎉

---

## 📝 Environment Variables

Set these in Render dashboard:

```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/attendance_db?retryWrites=true&w=majority
MONGODB_DATABASE=attendance_db
```

---

## ✅ Checklist

- [ ] MongoDB Atlas setup
- [ ] Code on GitHub
- [ ] Render account
- [ ] Web service created
- [ ] Env vars set
- [ ] Deployed!

**That's it!** 🚀

