# ValuAdis cPanel Terminal Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying ValuAdis on cPanel using terminal-based approach with:
- **Backend**: Python FastAPI (via Passenger WSGI)
- **Frontend**: Nuxt.js (static export)
- **Database**: PostgreSQL with PostGIS
- **Domain**: valuadis.vulcanig.net

## Prerequisites
- cPanel Terminal access
- Domain: valuadis.vulcanig.net
- PostgreSQL enabled in cPanel

## Folder Structure on cPanel

```
/home/username/                    # cPanel home directory
├── public_html/                   # Root web folder
│   └── valuadis/                  # Your app folder
│       ├── backend/               # FastAPI application
│       │   ├── app/
│       │   ├── venv/              # Python virtual environment
│       │   ├── passenger_wsgi.py  # WSGI entry point
│       │   └── .env               # Environment variables
│       ├── frontend/              # Nuxt.js frontend
│       │   ├── .output/           # Built static files
│       │   └── .env
│       └── .htaccess              # Apache config
├── postgresql/                    # Database backups (if needed)
└── logs/                          # Application logs
```

## Step 1: Environment Variables Template

Create this file locally first, fill in the values, then we'll upload it.

### `/backend/.env`
```env
# Database Configuration
DATABASE_URL=postgresql://valuadis_user:YOUR_PASSWORD@localhost:5432/valuadis_db
POSTGRES_DB=valuadis_db
POSTGRES_USER=valuadis_user
POSTGRES_PASSWORD=YOUR_PASSWORD

# Application Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
ENVIRONMENT=production
DEBUG=false

# Frontend URL (for CORS)
FRONTEND_URL=https://valuadis.vulcanig.net

# API Settings
API_BASE_URL=https://valuadis.vulcanig.net/api

# Redis (if available, otherwise we'll skip)
# REDIS_URL=redis://localhost:6379/0

# Email Configuration (optional)
# SMTP_HOST=
# SMTP_PORT=587
# SMTP_USER=
# SMTP_PASSWORD=

# Sentry (optional)
# SENTRY_DSN=

# File Upload Settings
UPLOAD_DIR=/home/username/public_html/valuadis/uploads
MAX_UPLOAD_SIZE=10485760

# API Documentation
DOCS_ENABLED=false
```

### `/frontend/.env`
```env
NUXT_PUBLIC_API_BASE=https://valuadis.vulcanig.net/api
NUXT_PUBLIC_APP_URL=https://valuadis.vulcanig.net
ENVIRONMENT=production
```

## Step 2: Terminal Commands

### A. Connect to Terminal
1. Log into cPanel
2. Click "Terminal" in the Tools section
3. Wait for the terminal to load

### B. Create Folder Structure
```bash
# Navigate to public_html
cd ~/public_html

# Create app directory
mkdir -p valuadis/backend
mkdir -p valuadis/frontend
mkdir -p valuadis/uploads

# Verify structure
ls -la valuadis/
```

### C. Upload Your Code
You'll need to upload your code. Options:
1. **Git Clone** (if repo is accessible)
2. **File Manager** (upload zip and extract)
3. **SFTP/SCP** (using terminal)

Option 1 - Git Clone (recommended):
```bash
cd ~/public_html/valuadis/backend
git clone YOUR_REPO_URL .
# Or if you have a zip file uploaded via File Manager:
# cd ~/public_html/valuadis/backend
# unzip ~/backend.zip
```

### D. Setup Python Environment
```bash
cd ~/public_html/valuadis/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Create passenger_wsgi.py
cat > passenger_wsgi.py << 'EOF'
import sys
import os

# Add the virtual environment path
INTERP = os.path.expanduser("~/public_html/valuadis/backend/venv/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import FastAPI app
from app.main import app as application
EOF

chmod 755 passenger_wsgi.py
```

### E. Setup Database (PostgreSQL with PostGIS)

In cPanel:
1. Go to "PostgreSQL Databases"
2. Create Database: `valuadis_db`
3. Create User: `valuadis_user` with password
4. Add user to database with "All Privileges"

Then in Terminal:
```bash
# Connect to PostgreSQL (you'll need the password)
psql -U valuadis_user -d valuadis_db -h localhost

# Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

# Verify installation
SELECT PostGIS_Version();
\q
```

### F. Initialize Database Schema
```bash
cd ~/public_html/valuadis/backend
source venv/bin/activate

# Run migrations (if using Alembic)
alembic upgrade head

# Or initialize with your init script
python init_db.py
```

### G. Build Frontend
```bash
cd ~/public_html/valuadis/frontend

# Install Node.js dependencies
npm install

# Build for production
npm run build

# The built files will be in .output/public
```

### H. Configure .htaccess
```bash
cd ~/public_html/valuadis
cat > .htaccess << 'EOF'
# Enable rewrite engine
RewriteEngine On

# API requests go to backend
RewriteCond %{REQUEST_URI} ^/api/
RewriteRule ^api/(.*)$ /backend/passenger_wsgi.py/$1 [QSA,L]

# Static files served directly
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]

# Everything else goes to frontend
RewriteRule ^(.*)$ /frontend/.output/public/$1 [L]

# PHP settings (if needed)
php_value upload_max_filesize 64M
php_value post_max_size 64M
php_value memory_limit 256M

# Security headers
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"
EOF
```

### I. Restart Application
```bash
# Create restart script
touch ~/public_html/valuadis/backend/tmp/restart.txt
```

## Step 3: Testing

1. **Backend API**: https://valuadis.vulcanig.net/api/health
2. **Frontend**: https://valuadis.vulcanig.net
3. **Check logs**:
   ```bash
   tail -f ~/public_html/valuadis/backend/logs/error.log
   ```

## Troubleshooting

### Issue: 500 Internal Server Error
```bash
# Check Passenger logs
tail -f ~/logs/error_log

# Check application logs
tail -f ~/public_html/valuadis/backend/logs/*.log
```

### Issue: Database Connection
```bash
# Test connection
psql -U valuadis_user -d valuadis_db -h localhost -c "SELECT 1;"
```

### Issue: Permission Denied
```bash
# Fix permissions
chmod 755 ~/public_html/valuadis
chmod 755 ~/public_html/valuadis/backend
chmod 644 ~/public_html/valuadis/backend/.env
chmod 755 ~/public_html/valuadis/backend/venv/bin/python
```

## Post-Deployment Checklist

- [ ] Database connected and migrated
- [ ] API endpoints responding (test /api/health)
- [ ] Frontend loading correctly
- [ ] File uploads working
- [ ] Environment variables secured
- [ ] SSL certificate active (should be automatic via cPanel)
- [ ] Backups configured

## Support

If you encounter issues:
1. Check cPanel error logs
2. Review application logs
3. Verify environment variables
4. Ensure PostGIS is enabled
