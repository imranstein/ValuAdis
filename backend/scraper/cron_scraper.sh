#!/bin/bash

# AVM Scraper Cron Wrapper
# This script is meant to be run via cron on a Linux environment (e.g., cPanel).

# ==========================================
# CONFIGURATION
# ==========================================

# 1. Set the absolute path to the backend directory
# Change this to match your cPanel environment path!
# Example: /home/yourusername/public_html/backend
APP_DIR="/Users/imranabdul/Dev/Personal/ValuAdis/backend"

# 2. Set the python executable from your virtual environment
# Usually it's in venv/bin/python
PYTHON_EXEC="${APP_DIR}/venv/bin/python"

# 3. Path to the scraper script
SCRAPER_SCRIPT="${APP_DIR}/scraper/run_scraper.py"

# 4. Where to put the logs
LOG_FILE="${APP_DIR}/scraper/scraper_cron.log"

# ==========================================
# EXECUTION
# ==========================================

echo "----------------------------------------" >> "$LOG_FILE"
echo "Starting AVM Scraper at $(date)" >> "$LOG_FILE"

# Change to the application directory
cd "$APP_DIR" || { echo "Failed to cd into $APP_DIR" >> "$LOG_FILE"; exit 1; }

# Important for Playwright: Ensure necessary environment variables are set
# Depending on cPanel, you might need to export PATH or PLAYWRIGHT_BROWSERS_PATH if installed globally.
export NODE_ENV=production

# Run the scraper
# Add --test-mode if you only want to scrape a couple of listings
$PYTHON_EXEC "$SCRAPER_SCRIPT" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Scraper finished SUCCESSFULLY at $(date)" >> "$LOG_FILE"
else
    echo "Scraper FAILED with exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

echo "----------------------------------------" >> "$LOG_FILE"
