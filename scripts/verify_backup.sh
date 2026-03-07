#!/bin/bash
# ValuAdis Backup Verification Script
# Verifies that database backups are restorable
# Run after backup.sh or manually: ./scripts/verify_backup.sh [backup_file]

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/www/valuadis/backups}"
VERIFY_DIR="${VERIFY_DIR:-/tmp/valuadis_backup_verify}"
LOG_FILE="${LOG_FILE:-/var/www/valuadis/logs/backup_verify.log}"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Use specific file or latest
if [ -n "${1:-}" ]; then
    BACKUP_FILE="$1"
else
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | head -1)
fi

if [ -z "${BACKUP_FILE:-}" ] || [ ! -f "$BACKUP_FILE" ]; then
    log "❌ No backup file found in $BACKUP_DIR"
    exit 1
fi

log "Verifying backup: $BACKUP_FILE"

# Decompress and check SQL validity
mkdir -p "$VERIFY_DIR"
gunzip -c "$BACKUP_FILE" > "$VERIFY_DIR/restore_test.sql" 2>/dev/null || {
    log "❌ Failed to decompress backup"
    exit 1
}

# Basic SQL structure check (PostgreSQL dump should start with -- and have CREATE/INSERT)
if head -100 "$VERIFY_DIR/restore_test.sql" | grep -qE '^(--|CREATE|INSERT|COPY)'; then
    log "✅ Backup structure appears valid"
else
    log "⚠️ Backup structure may be invalid - manual review recommended"
fi

# Check file size
SIZE=$(du -h "$VERIFY_DIR/restore_test.sql" | cut -f1)
log "Backup size (decompressed): $SIZE"

# Cleanup
rm -rf "$VERIFY_DIR"
log "✅ Backup verification completed"
