# Enhanced Dashboard Deployment Guide

## 🚀 Deployment Options

### Option 1: Local Development Server (Quick Test)
### Option 2: Render.com (Free Tier Available)
### Option 3: Railway.app (Recommended)
### Option 4: Vercel/Netlify (Frontend) + Backend API
### Option 5: Self-Hosted with Nginx

---

## 📋 Pre-Deployment Checklist

- [x] Enhanced dashboard implemented (Phases 1-4)
- [ ] API server tested locally
- [ ] Database configured
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Static files ready

---

## 🏠 Option 1: Local Development Server

### Quick Start

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start API server
py -3 -m uvicorn attendance_api:app --reload --port 8000 --host 0.0.0.0

# 3. Access dashboard
# Open browser: http://localhost:8000/
```

The dashboard is automatically served at the root URL.

---

## ☁️ Option 2: Deploy to Render.com

### Step 1: Prepare Files

1. **Create `render.yaml`** (if not exists):
```yaml
services:
  - type: web
    name: attendance-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn attendance_api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: PYTHON_VERSION
        value: 3.10
```

2. **Create `Procfile`**:
```
web: uvicorn attendance_api:app --host 0.0.0.0 --port $PORT
```

### Step 2: Deploy

1. Go to https://render.com
2. Sign up/Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: attendance-dashboard
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn attendance_api:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `DATABASE_URL` (if using PostgreSQL)
7. Click "Create Web Service"

### Step 3: Access

Your dashboard will be available at: `https://your-app-name.onrender.com`

---

## 🚂 Option 3: Deploy to Railway.app (Recommended)

### Step 1: Setup

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"

### Step 2: Configure

1. Select your repository
2. Railway auto-detects Python
3. Add PostgreSQL database:
   - Click "New" → "Database" → "PostgreSQL"
4. Set environment variables:
   - `DATABASE_URL` (auto-set by Railway)
   - `PYTHON_VERSION=3.10`

### Step 3: Deploy

Railway will automatically:
- Install dependencies from `requirements.txt`
- Run `uvicorn attendance_api:app`
- Serve on port provided by Railway

### Step 4: Access

Your dashboard URL: `https://your-app-name.up.railway.app`

---

## 🌐 Option 4: Separate Frontend/Backend Deployment

### Frontend (Vercel/Netlify)

1. **Update API URL in dashboard**:
   - Change `API_BASE_URL` in `web_dashboard.html` to your backend URL
   - Or use environment variable

2. **Deploy to Vercel**:
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

3. **Deploy to Netlify**:
   - Drag and drop `web_dashboard.html` to Netlify
   - Or connect GitHub repo

### Backend (Render/Railway)

Deploy `attendance_api.py` as a separate service (see Option 2 or 3).

### Update CORS

In `attendance_api.py`, update CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🖥️ Option 5: Self-Hosted with Nginx

### Step 1: Server Setup

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Install Python packages
pip3 install -r requirements.txt
```

### Step 2: Create Systemd Service

Create `/etc/systemd/system/attendance-api.service`:
```ini
[Unit]
Description=Attendance API Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn attendance_api:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

### Step 3: Configure Nginx

Create `/etc/nginx/sites-available/attendance`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Step 4: Enable and Start

```bash
# Enable service
sudo systemctl enable attendance-api
sudo systemctl start attendance-api

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/attendance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔧 Configuration Updates

### Update API Base URL

If deploying frontend separately, update in `web_dashboard.html`:

```javascript
// Change this line:
const API_BASE_URL = 'http://localhost:8000';

// To your production API URL:
const API_BASE_URL = 'https://your-api-domain.com';
```

### Environment Variables

Create `.env` file (or set in hosting platform):
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
SECRET_KEY=your-secret-key
API_URL=https://your-api-domain.com
```

### Update CORS Settings

For production, restrict CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 📦 Production Checklist

- [ ] Update `API_BASE_URL` in dashboard
- [ ] Configure CORS properly
- [ ] Set up database (PostgreSQL recommended)
- [ ] Configure environment variables
- [ ] Enable HTTPS/SSL
- [ ] Set up domain name
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging
- [ ] Backup database
- [ ] Test all features

---

## 🔒 Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **CORS**: Restrict to your frontend domain
3. **Environment Variables**: Never commit secrets
4. **Database**: Use strong passwords
5. **Rate Limiting**: Consider adding rate limiting
6. **Authentication**: Add authentication for production (Phase 5)

---

## 🐛 Troubleshooting

### Dashboard not loading
- Check API server is running
- Verify CORS settings
- Check browser console for errors
- Verify API_BASE_URL is correct

### WebSocket not connecting
- Ensure WebSocket support in proxy (Nginx)
- Check firewall allows WebSocket connections
- Verify WebSocket URL uses `wss://` for HTTPS

### Static files not serving
- Verify `FileResponse` path is correct
- Check file permissions
- Ensure file exists in deployment

---

## 📊 Monitoring

### Recommended Tools
- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Error Tracking**: Sentry
- **Analytics**: Google Analytics
- **Logs**: Platform-native logging (Render, Railway)

---

## 🚀 Quick Deploy Script

Create `deploy.sh`:
```bash
#!/bin/bash
echo "Deploying Attendance Dashboard..."

# Install dependencies
pip install -r requirements.txt

# Run migrations (if any)
# alembic upgrade head

# Start server
uvicorn attendance_api:app --host 0.0.0.0 --port ${PORT:-8000}

echo "Deployment complete!"
```

---

## 📝 Next Steps After Deployment

1. Test all dashboard features
2. Set up automated backups
3. Configure monitoring
4. Add custom domain
5. Set up SSL certificate
6. Implement authentication (Phase 5)

---

**Happy Deploying! 🎉**

