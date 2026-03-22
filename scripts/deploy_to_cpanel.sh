#!/bin/bash
# cPanel Deployment Script for ValuAdis
# Run this in cPanel Terminal

set -e  # Exit on error

echo "🚀 Starting ValuAdis Deployment on cPanel..."

# Configuration
APP_NAME="valuadis"
DOMAIN="valuadis.vulcanig.net"
BACKEND_PORT=8000

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
check_environment() {
    print_status "Checking environment..."
    
    if [ ! -d "$HOME/public_html" ]; then
        print_error "Not in cPanel environment. public_html not found."
        exit 1
    fi
    
    print_status "Environment check passed ✓"
}

# Create folder structure
create_folders() {
    print_status "Creating folder structure..."
    
    mkdir -p $HOME/public_html/$APP_NAME/backend
    mkdir -p $HOME/public_html/$APP_NAME/frontend
    mkdir -p $HOME/public_html/$APP_NAME/uploads
    mkdir -p $HOME/logs
    
    print_status "Folder structure created ✓"
}

# Setup Python backend
setup_backend() {
    print_status "Setting up Python backend..."
    
    cd $HOME/public_html/$APP_NAME/backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate and install dependencies
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found. Skipping pip install."
    fi
    
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
    
    print_status "Backend setup complete ✓"
}

# Create .htaccess
create_htaccess() {
    print_status "Creating .htaccess configuration..."
    
    cd $HOME/public_html/$APP_NAME
    
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

# PHP settings
php_value upload_max_filesize 64M
php_value post_max_size 64M
php_value memory_limit 256M

# Security headers
<IfModule mod_headers.c>
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>
EOF
    
    print_status ".htaccess created ✓"
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."
    
    cd $HOME/public_html/$APP_NAME/frontend
    
    if [ -f "package.json" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
        
        print_status "Building for production..."
        npm run build
        
        print_status "Frontend build complete ✓"
    else
        print_warning "package.json not found. Skipping frontend build."
    fi
}

# Fix permissions
fix_permissions() {
    print_status "Fixing permissions..."
    
    chmod 755 $HOME/public_html/$APP_NAME
    chmod 755 $HOME/public_html/$APP_NAME/backend
    chmod 755 $HOME/public_html/$APP_NAME/frontend
    chmod 755 $HOME/public_html/$APP_NAME/uploads
    
    if [ -f "$HOME/public_html/$APP_NAME/backend/.env" ]; then
        chmod 600 $HOME/public_html/$APP_NAME/backend/.env
    fi
    
    if [ -f "$HOME/public_html/$APP_NAME/frontend/.env" ]; then
        chmod 600 $HOME/public_html/$APP_NAME/frontend/.env
    fi
    
    print_status "Permissions fixed ✓"
}

# Restart application
restart_app() {
    print_status "Restarting application..."
    
    touch $HOME/public_html/$APP_NAME/backend/tmp/restart.txt 2>/dev/null || true
    
    print_status "Application restart triggered ✓"
}

# Main deployment function
deploy() {
    print_status "Starting deployment process..."
    
    check_environment
    create_folders
    setup_backend
    create_htaccess
    build_frontend
    fix_permissions
    restart_app
    
    echo ""
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo ""
    echo "Your application should be available at:"
    echo "  • Frontend: https://$DOMAIN"
    echo "  • API: https://$DOMAIN/api"
    echo ""
    echo "Next steps:"
    echo "  1. Upload your code to ~/public_html/$APP_NAME/"
    echo "  2. Configure your .env files"
    echo "  3. Set up the database"
    echo "  4. Test the application"
    echo ""
}

# Run deployment
deploy
