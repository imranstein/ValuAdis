# ValuAdis cPanel Deployment - Quick Start Checklist

## ✅ Pre-Deployment (Do These First)

### 1. Database Setup
- [ ] Go to cPanel → PostgreSQL Databases
- [ ] Create database: `valuadis_db`
- [ ] Create user: `valuadis_user` 
- [ ] Set strong password (save it!)
- [ ] Add user to database with ALL PRIVILEGES
- [ ] Enable PostGIS (via Terminal):
  ```bash
  psql -U valuadis_user -d valuadis_db -h localhost
  CREATE EXTENSION IF NOT EXISTS postgis;
  \q
  ```

### 2. Domain Configuration
- [ ] Ensure `valuadis.vulcanig.net` subdomain exists
- [ ] Check SSL certificate (should be auto-enabled)

---

## 📦 Code Preparation (Local Machine)

### 3. Prepare Backend
```bash
cd /Users/imranabdul/Dev/Personal/ValuAdis/backend

# Clean up
rm -rf __pycache__ .pytest_cache *.pyc .env

# Create required files for cPanel
cat > passenger_wsgi.py << 'PYEOF'
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from app.main import app as application
PYEOF

# Create .htaccess for backend folder
cat > .htaccess << 'HTEOF'
PassengerEnabled on
PassengerPython /home/YOUR_USERNAME/virtualenv/public_html/valuadis/backend/3.11/bin/python
HTEOF

# Create deployment package
zip -r ../deploy/backend.zip . -x "*.pyc" "__pycache__/*" "venv/*" "*.log" "tests/*" "tmp/*"
```

### 4. Prepare Frontend
```bash
cd /Users/imranabdul/Dev/Personal/ValuAdis/frontend

# Clean build
rm -rf .output node_modules .nuxt

# Install dependencies
npm install

# Build for production
NUXT_PUBLIC_API_BASE=https://valuadis.vulcanig.net/api npm run build

# Create simple Node.js server for cPanel
cat > server.js << 'JSEOF'
const http = require('http');
const fs = require('fs');
const path = require('path');
const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, '.output/public');

const server = http.createServer((req, res) => {
    let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        filePath = path.join(PUBLIC_DIR, 'index.html');
    }
    const ext = path.extname(filePath);
    const contentTypes = {
        '.html': 'text/html', '.js': 'text/javascript',
        '.css': 'text/css', '.json': 'application/json',
        '.png': 'image/png', '.jpg': 'image/jpg',
        '.gif': 'image/gif', '.svg': 'image/svg+xml',
    };
    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404); res.end('Not found'); return;
        }
        res.writeHead(200, { 'Content-Type': contentTypes[ext] || 'application/octet-stream' });
        res.end(content);
    });
});
server.listen(PORT, () => console.log(`Server on port ${PORT}`));
JSEOF

# Create deployment package
zip -r ../deploy/frontend.zip .output/ server.js package.json -x "node_modules/*" ".nuxt/*"
```

---

## ☁️ Upload to cPanel

### 5. Upload Files
- [ ] Log into cPanel → File Manager
- [ ] Navigate to `public_html/`
- [ ] Create folder: `valuadis`
- [ ] Upload `backend.zip` and `frontend.zip` (from `deploy/` folder)
- [ ] Extract both files
- [ ] Delete zip files after extraction

### 6. Create Uploads Directory
- [ ] In `public_html/valuadis/`, create folder: `uploads`
- [ ] Set permissions to 755

---

## ⚙️ Configure Applications

### 7. Setup Python App (Backend)
1. Go to cPanel → **Setup Python App**
2. Click **Create Application**
3. Fill the form:
   | Field | Value |
   |-------|-------|
   | Python Version | 3.11 |
   | Application Root | `public_html/valuadis/backend` |
   | Application URL | `valuadis.vulcanig.net/api` |
   | Application Startup File | `passenger_wsgi.py` |
   | Application Entry Point | `application` |

4. Click **Create**
5. **Add Environment Variables**:
   ```
   DATABASE_URL=postgresql://valuadis_user:YOUR_DB_PASSWORD@localhost:5432/valuadis_db
   SECRET_KEY=your-32-char-secret-key-here-change-this
   ENVIRONMENT=production
   DEBUG=false
   FRONTEND_URL=https://valuadis.vulcanig.net
   UPLOAD_DIR=/home/YOUR_USERNAME/public_html/valuadis/uploads
   ```
6. Click **Save**
7. Click **Run Pip Install** (to install requirements.txt)
8. Click **Restart**

### 8. Setup Node.js App (Frontend)
1. Go to cPanel → **Setup Node.js App**
2. Click **Create Application**
3. Fill the form:
   | Field | Value |
   |-------|-------|
   | Node.js Version | 18 |
   | Application Root | `public_html/valuadis/frontend` |
   | Application URL | `valuadis.vulcanig.net` |
   | Application Startup File | `server.js` |
   | Application Entry Point | `server.js` |

4. Click **Create**
5. **Add Environment Variables**:
   ```
   NUXT_PUBLIC_API_BASE=https://valuadis.vulcanig.net/api
   ENVIRONMENT=production
   PORT=3000
   ```
6. Click **Save**
7. Click **Run NPM Install**
8. Click **Restart**

---

## 🗄️ Database Migration

### 9. Initialize Database
```bash
# In cPanel Terminal
cd ~/public_html/valuadis/backend
source /home/YOUR_USERNAME/virtualenv/public_html/valuadis/backend/3.11/bin/activate

# Run migrations
alembic upgrade head

# Or initialize database
python init_db.py

# Create admin user
python create_admin.py
```

---

## 🔧 Final Configuration

### 10. Fix Permissions
```bash
# In cPanel Terminal
cd ~/public_html/valuadis
chmod 755 backend frontend uploads
chmod 644 backend/.env frontend/.env 2>/dev/null || true
chmod 755 backend/passenger_wsgi.py
```

### 11. Create Root .htaccess
Create file: `public_html/valuadis/.htaccess`
```apache
RewriteEngine On

# Security headers
<IfModule mod_headers.c>
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
</IfModule>

# Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css application/javascript
</IfModule>
```

---

## 🧪 Testing

### 12. Verify Deployment
- [ ] Visit https://valuadis.vulcanig.net
- [ ] Test API: https://valuadis.vulcanig.net/api/health
- [ ] Check database connection
- [ ] Verify file uploads work
- [ ] Test login functionality

### 13. Check Logs (if issues)
- cPanel → Setup Python App → Logs
- cPanel → Setup Node.js App → Logs  
- cPanel → Error Log

---

## 🎉 Done!

Your ValuAdis application should now be live at:
**https://valuadis.vulcanig.net**

---

## 🆘 Emergency Contacts

If something breaks:
1. Check application logs first
2. Verify environment variables
3. Test database connection
4. Restart both applications
5. Check file permissions
