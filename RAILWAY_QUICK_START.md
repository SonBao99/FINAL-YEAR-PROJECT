# 🚂 Railway Quick Start Guide

## Deploy in 5 Minutes!

### Step 1: Push to GitHub ✅
```bash
git add .
git commit -m "Ready for Railway"
git push
```

### Step 2: Create Railway Project
1. Go to https://railway.app
2. Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository

### Step 3: Add PostgreSQL Database
1. In Railway project, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Done! Railway sets `DATABASE_URL` automatically

### Step 4: Deploy!
Railway auto-detects and deploys:
- ✅ Detects Python
- ✅ Runs `pip install -r requirements.txt`
- ✅ Starts with `python start_server.py`
- ✅ Creates database tables automatically

### Step 5: Access Dashboard
1. Railway dashboard → Your service
2. Click "Settings" → "Generate Domain"
3. Open the URL in browser
4. Dashboard loads automatically! 🎉

---

## 🔧 Environment Variables (Optional)

Railway sets these automatically:
- `DATABASE_URL` ✅ (from PostgreSQL service)
- `PORT` ✅ (Railway assigns)

You can add:
- `ALLOWED_ORIGINS=*` (or your domain)
- `HOST=0.0.0.0`

---

## ✅ That's It!

Your dashboard is live with PostgreSQL!

**URL**: `https://your-app-name.up.railway.app`

---

## 🐛 Troubleshooting

**Build fails?**
- Check `requirements.txt` is correct
- Check Railway logs

**Database error?**
- Verify PostgreSQL service is running
- Check `DATABASE_URL` is set

**Dashboard not loading?**
- Check Railway logs
- Verify deployment succeeded

---

**See RAILWAY_DEPLOYMENT.md for detailed guide!**

