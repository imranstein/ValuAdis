# ValuAdis cPanel App Manager Deployment Guide

## Overview
Deploy ValuAdis using cPanel's built-in **Setup Python App** and **Setup Node.js App** features.
- **Backend**: Python FastAPI via cPanel Python App (Phusion Passenger)
- **Frontend**: Nuxt.js static site via cPanel Node.js App
- **Database**: PostgreSQL with PostGIS
- **Domain**: valuadis.vulcanig.net

## Architecture
```
valuadis.vulcanig.net/
├── / (root) → Node.js App (Nuxt.js static)
├── /api/* → Python App (FastAPI)
└── /uploads/ → Static file serving
```

---

## STEP 1: Prepare Your Code

### A. Create Backend Package
In your local project, create a deployable backend package:

```bash
cd /Users/imranabdul/Dev/Personal/ValuAdis/backend

# Clean up
rm -rf __pycache__ .pytest_cache venv *.pyc

# Create deployment package
zip -r ../deploy/backend.zip . -x "*.pyc" "__pycache__/*" "venv/*" "*.log" "tests/*"
```

### B. Create Frontend Package (Static Build)
```bash
cd /Users/imranabdul/Dev/Personal/ValuAdis/frontend

# Clean build
rm -rf .output node_modules .nuxt

# Install dependencies
npm install

# Build for static export
NUXT_PUBLIC_API_BASE=https://valuadis.vulcanig.net/api npm run build

# Create deployment package
zip -r ../deploy/frontend.zip .output/public/
```

---

## STEP 2: Upload to cPanel

### Option 1: File Manager
1. Log into cPanel
2. Go to **File Manager**
3. Navigate to `public_html/`
4. Create folder: `valuadis`
5. Upload `backend.zip` and `frontend.zip`
6. Extract both zips

### Option 2: Terminal (Quicker)
```bash
# In cPanel Terminal
cd ~/public_html
mkdir -p valuadis
cd valuadis

# Upload files via File Manager first, then:
unzip backend.zip -d backend/
unzip frontend.zip -d frontend/
```

---

## STEP 3: Setup Python Application

### 3.1 Create Python App
1. In cPanel, go to **Setup Python App**
2. Click **Create Application**
3. Fill in:
   - **Python Version**: 3.11 (or latest available)
   - **Application Root**: `public_html/valuadis/backend`
   - **Application URL**: `valuadis.vulcanig.net/api`
   - **Application Startup File**: `passenger_wsgi.py`
   - **Application Entry Point**: `application`
   - **Environment Variables**: (see below)

4. Click **Create**

### 3.2 Create passenger_wsgi.py
In File Manager, navigate to `public_html/valuadis/backend/` and create:

**File: `passenger_wsgi.py`**
```python
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import FastAPI app
from app.main import app as application
```

### 3.3 Install Dependencies
In the Python App panel:
1. Click on your app
2. Go to **Configuration files** section
3. Make sure `requirements.txt` is detected
4. Click **Run Pip Install**

Or manually add via **Edit** button:
```bash
cd /home/username/public_html/valuadis/backend
pip install fastapi uvicorn sqlalchemy alembic python-jose passlib pydantic python-dotenv
```

---

## STEP 4: Setup Node.js Application

### 4.1 Create Node.js App
1. In cPanel, go to **Setup Node.js App**
2. Click **Create Application**
3. Fill in:
   - **Node.js Version**: 18 (or latest LTS)
   - **Application Root**: `public_html/valuadis/frontend`
   - **Application URL**: `valuadis.vulcanig.net` (root)
   - **Application Startup File**: `server.js` (we'll create this)
   - **Environment Variables**: (see below)

4. Click **Create**

### 4.2 Create Simple Node Server
In File Manager, navigate to `public_html/valuadis/frontend/` and create:

**File: `server.js`**
```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, '.output/public');

const server = http.createServer((req, res) => {
    let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
    
    // Default to index.html for SPA routing
    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        filePath = path.join(PUBLIC_DIR, 'index.html');
    }
    
    const ext = path.extname(filePath);
    const contentTypes = {
        '.html': 'text/html',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
    };
    
    const contentType = contentTypes[ext] || 'application/octet-stream';
    
    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404);
            res.end('Not found');
            return;
        }
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(content);
    });
});

server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

---

## STEP 5: Configure PostgreSQL Database

### 5.1 Create Database
1. In cPanel, go to **PostgreSQL Databases**
2. **Create New Database**:
   - Database Name: `valuadis_db`
3. **Create New User**:
   - Username: `valuadis_user`
   - Password: (generate strong password)
4. **Add User to Database**:
   - Select user: `valuadis_user`
   - Select database: `valuadis_db`
   - Privileges: **ALL PRIVILEGES**

### 5.2 Enable PostGIS (via Terminal)
In cPanel Terminal:
```bash
psql -U valuadis_user -d valuadis_db -h localhost

# Run these SQL commands:
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

# Verify
SELECT PostGIS_Version();
\q
```

---

## STEP 6: Environment Variables

### Python App Variables (Backend)
In **Setup Python App** → **Edit** → **Environment Variables**:

```
DATABASE_URL=postgresql://valuadis_user:YOUR_PASSWORD@localhost:5432/valuadis_db
SECRET_KEY=your-super-secret-key-min-32-chars-long-for-production
ENVIRONMENT=production
DEBUG=false
FRONTEND_URL=https://valuadis.vulcanig.net
UPLOAD_DIR=/home/YOUR_CPANEL_USER/public_html/valuadis/uploads
```

### Node.js App Variables (Frontend)
In **Setup Node.js App** → **Edit** → **Environment Variables**:

```
NUXT_PUBLIC_API_BASE=https://valuadis.vulcanig.net/api
ENVIRONMENT=production
```

---

## STEP 7: Database Migration

### Initialize Database Schema
In cPanel Terminal:
```bash
cd ~/public_html/valuadis/backend

# If using Alembic
alembic upgrade head

# Or run your init script
python init_db.py

# Or create admin user
python create_admin.py
```

---

## STEP 8: Fix Permissions

In cPanel Terminal:
```bash
# Fix permissions
cd ~/public_html/valuadis
chmod 755 backend frontend uploads
chmod -R 644 backend/.env frontend/.env 2>/dev/null || true

# Ensure Passenger can execute
chmod 755 backend/passenger_wsgi.py
```

---

## STEP 9: Restart Applications

### Restart Python App
1. Go to **Setup Python App**
2. Click your app
3. Click **Restart**

### Restart Node.js App
1. Go to **Setup Node.js App**
2. Click your app
3. Click **Restart**

---

## STEP 10: Configure .htaccess for Clean URLs

Create `public_html/valuadis/.htaccess`:

```apache
# Enable rewrite
RewriteEngine On

# Handle trailing slashes
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)/$ /$1 [L,R=301]

# API requests - handled by Python App
# (cPanel Passenger handles this automatically)

# Frontend - handled by Node.js App
# (cPanel handles this automatically)

# Static uploads
RewriteRule ^uploads/(.*)$ /uploads/$1 [L]

# Security headers
<IfModule mod_headers.c>
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>

# Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css application/javascript application/json
</IfModule>
```

---

## Testing & Verification

### Test Backend API
```bash
curl https://valuadis.vulcanig.net/api/health
curl https://valuadis.vulcanig.net/api/docs
```

### Test Frontend
Open in browser:
- https://valuadis.vulcanig.net

### Check Logs
**Python App Logs**:
- In cPanel → Setup Python App → View Logs
- Or: `~/logs/passenger.log`

**Node.js App Logs**:
- In cPanel → Setup Node.js App → View Logs
- Or: `~/logs/nodejs.log`

**Error Logs**:
- cPanel → Error Log
- `~/logs/error_log`

---

## Troubleshooting

### Issue: 500 Internal Server Error
1. Check application logs in cPanel
2. Verify environment variables are set
3. Check file permissions
4. Ensure database connection string is correct

### Issue: Database Connection Failed
```bash
# Test in Terminal
psql -U valuadis_user -d valuadis_db -h localhost -c "SELECT 1;"
```

### Issue: Python App Won't Start
1. Check `passenger_wsgi.py` syntax
2. Verify all dependencies installed
3. Check `requirements.txt` is valid

### Issue: Node.js App Won't Start
1. Verify `server.js` exists
2. Check `.output/public/` has built files
3. Verify Node.js version compatibility

---

## Post-Deployment Checklist

- [ ] Python App shows "Running" status
- [ ] Node.js App shows "Running" status
- [ ] Database connected (test with query)
- [ ] API responds at `/api/health`
- [ ] Frontend loads at root URL
- [ ] PostGIS enabled and working
- [ ] File uploads working
- [ ] Environment variables secured
- [ ] SSL certificate active (AutoSSL)

---

## Support Resources

- **cPanel Docs**: https://docs.cpanel.net/
- **Python App Guide**: https://support.cpanel.net/hc/en-us/articles/1500009457741
- **Node.js App Guide**: https://support.cpanel.net/hc/en-us/articles/1500011461921
