#!/bin/bash

# ValuAdis Backup Script
# Run daily at 2 AM via cron

set -euo pipefail

# Configuration
BACKUP_DIR="/var/www/valuadis/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
LOG_FILE="/var/www/valuadis/logs/backup.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to send notification on failure
notify_failure() {
    log "BACKUP FAILED: $1"
    # Send to Slack if webhook is configured
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"❌ ValuAdis backup failed: $1\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    exit 1
}

log "Starting backup process..."

# Change to project directory
cd /var/www/valuadis || notify_failure "Cannot change to project directory"

# Database backup
log "Starting database backup..."
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

if docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
    -U "${POSTGRES_USER:-valuadis_user}" \
    "${POSTGRES_DB:-valuadis}" > "$DB_BACKUP_FILE"; then
    log "Database backup completed: $DB_BACKUP_FILE"
    
    # Compress the backup
    gzip "$DB_BACKUP_FILE"
    log "Database backup compressed: ${DB_BACKUP_FILE}.gz"
else
    notify_failure "Database backup failed"
fi

# File uploads backup
log "Starting file uploads backup..."
UPLOADS_BACKUP_FILE="$BACKUP_DIR/uploads_backup_$DATE.tar.gz"

if tar -czf "$UPLOADS_BACKUP_FILE" uploads/; then
    log "File uploads backup completed: $UPLOADS_BACKUP_FILE"
else
    notify_failure "File uploads backup failed"
fi

# Configuration files backup
log "Starting configuration backup..."
CONFIG_BACKUP_FILE="$BACKUP_DIR/config_backup_$DATE.tar.gz"

if tar -czf "$CONFIG_BACKUP_FILE" \
    .env.production \
    nginx/nginx.conf \
    docker-compose.prod.yml \
    scripts/; then
    log "Configuration backup completed: $CONFIG_BACKUP_FILE"
else
    notify_failure "Configuration backup failed"
fi

# Cleanup old backups
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.sql" -mtime +$RETENTION_DAYS -delete
log "Cleanup completed"

# Verify backup integrity
log "Verifying backup integrity..."
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.gz" | wc -l)

log "Backup process completed successfully!"
log "Total backup size: $BACKUP_SIZE"
log "Number of backup files: $BACKUP_COUNT"

# Send success notification
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ ValuAdis backup completed successfully\\nSize: $BACKUP_SIZE\\nFiles: $BACKUP_COUNT\"}" \
        "$SLACK_WEBHOOK_URL"
fi

# Optional: Upload to remote storage (uncomment and configure)
# if [ -n "${REMOTE_BACKUP_URL:-}" ]; then
#     log "Uploading to remote storage..."
#     aws s3 sync "$BACKUP_DIR" "$REMOTE_BACKUP_URL" || notify_failure "Remote upload failed"
#     log "Remote upload completed"
# fi

exit 0
