# 🚂 Railway Deployment Guide with PostgreSQL

## Complete Step-by-Step Guide

---

## 📋 Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)
- Code pushed to GitHub repository

---

## 🚀 Step 1: Prepare Your Repository

### 1.1 Ensure Required Files Exist

Your project should have:
- ✅ `attendance_api.py` - Main API file
- ✅ `database.py` - Database configuration (already supports PostgreSQL!)
- ✅ `web_dashboard.html` - Dashboard file
- ✅ `requirements.txt` - Dependencies
- ✅ `start_server.py` - Server startup script
- ✅ `Procfile` - Railway process file

### 1.2 Push to GitHub

```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

---

## 🚂 Step 2: Deploy to Railway

### 2.1 Create Railway Account

1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub

### 2.2 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Railway will start deploying automatically

### 2.3 Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will create a PostgreSQL database
4. **Important**: Note the database connection details (shown in Variables tab)

---

## 🔧 Step 3: Configure Environment Variables

### 3.1 Automatic Variables (Set by Railway)

Railway automatically sets:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Port number (Railway assigns this)
- `RAILWAY_ENVIRONMENT` - Environment name

### 3.2 Manual Variables (Optional)

Click on your service → **"Variables"** tab → Add:

```
HOST=0.0.0.0
ALLOWED_ORIGINS=*
DEBUG=False
```

**For Production**, update `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://your-app-name.up.railway.app
```

---

## 📦 Step 4: Configure Build Settings

### 4.1 Railway Auto-Detection

Railway should auto-detect:
- **Language**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start_server.py`

### 4.2 Manual Configuration (if needed)

1. Go to your service → **"Settings"**
2. Under **"Build & Deploy"**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_server.py`
   - **Watch Paths**: `attendance_api.py,start_server.py`

---

## 🗄️ Step 5: Database Setup

### 5.1 Database Already Configured!

Your `database.py` already supports PostgreSQL! It will:
- ✅ Auto-detect PostgreSQL from `DATABASE_URL`
- ✅ Create tables automatically on first run
- ✅ Use connection pooling for production

### 5.2 Verify Database Connection

After deployment, check logs:
```bash
# In Railway dashboard → Deployments → View Logs
# Look for: "Database connected successfully"
```

### 5.3 Migrate Existing Data (Optional)

If you have SQLite data to migrate:

1. **Export from SQLite**:
```python
# Run locally
python export_sqlite_data.py
```

2. **Import to PostgreSQL**:
```python
# Run after Railway deployment
python import_to_postgresql.py
```

---

## 🌐 Step 6: Access Your Dashboard

### 6.1 Get Your URL

1. In Railway dashboard → Your service
2. Click **"Settings"** → **"Generate Domain"**
3. Your dashboard will be at: `https://your-app-name.up.railway.app`

### 6.2 Test Your Deployment

1. Open your Railway URL in browser
2. Dashboard should load automatically
3. Test features:
   - Create a course
   - Enroll a student
   - Create a session
   - Check WebSocket connection

---

## 🔒 Step 7: Security & Production Settings

### 7.1 Update CORS (Important!)

In Railway Variables, set:
```
ALLOWED_ORIGINS=https://your-app-name.up.railway.app
```

Or if using custom domain:
```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 7.2 Enable HTTPS

Railway provides HTTPS automatically! ✅

### 7.3 Custom Domain (Optional)

1. Railway dashboard → Your service → **"Settings"**
2. **"Custom Domain"** → Add your domain
3. Follow DNS configuration instructions

---

## 📊 Step 8: Monitor Your Deployment

### 8.1 View Logs

Railway dashboard → **"Deployments"** → Click deployment → **"View Logs"**

### 8.2 Check Metrics

Railway dashboard → **"Metrics"** tab:
- CPU usage
- Memory usage
- Network traffic
- Request count

---

## 🐛 Troubleshooting

### Issue: Database Connection Failed

**Solution**:
1. Check `DATABASE_URL` is set correctly
2. Verify PostgreSQL service is running
3. Check logs for connection errors

### Issue: Dashboard Not Loading

**Solution**:
1. Check API server is running (view logs)
2. Verify `web_dashboard.html` exists
3. Check browser console for errors

### Issue: WebSocket Not Connecting

**Solution**:
1. Verify WebSocket URL uses `wss://` (not `ws://`)
2. Check Railway allows WebSocket connections (it does!)
3. Update `API_BASE_URL` in dashboard if needed

### Issue: Build Fails

**Solution**:
1. Check `requirements.txt` is correct
2. Verify Python version (Railway uses 3.10+)
3. Check build logs for specific errors

---

## 🔄 Step 9: Update Deployment

### Automatic Updates

Railway auto-deploys when you push to GitHub!

### Manual Redeploy

1. Railway dashboard → Your service
2. **"Deployments"** → **"Redeploy"**

---

## 📝 Railway Configuration File (Optional)

Create `railway.json` in project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python start_server.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Project created from GitHub
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] Build settings verified
- [ ] Deployment successful
- [ ] Dashboard accessible
- [ ] Database tables created
- [ ] All features tested
- [ ] CORS configured
- [ ] Custom domain set (optional)

---

## 🎯 Quick Commands Reference

### Local Testing
```bash
# Test with PostgreSQL locally
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
python start_server.py
```

### Railway CLI (Optional)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

---

## 📚 Additional Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your Dashboard: `https://your-app-name.up.railway.app`

---

## 🎉 Success!

Your dashboard is now live on Railway with PostgreSQL!

**Next Steps**:
1. Test all features
2. Set up monitoring
3. Configure backups
4. Add custom domain (optional)

---

**Happy Deploying! 🚀**

