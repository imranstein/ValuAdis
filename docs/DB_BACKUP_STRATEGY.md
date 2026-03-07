# ValuAdis Database Backup Strategy

## Overview

Automated database backups and disaster recovery for the ValuAdis property valuation platform.

## Backup Schedule

- **Frequency**: Daily at 2:00 AM (configure via cron)
- **Retention**: 30 days
- **Location**: `/var/www/valuadis/backups/`

## Backup Components

1. **Database** (`db_backup_YYYYMMDD_HHMMSS.sql.gz`)
   - PostgreSQL + PostGIS dump via `pg_dump`
   - Compressed with gzip

2. **File Uploads** (`uploads_backup_YYYYMMDD_HHMMSS.tar.gz`)
   - Property photos, certificates, QR codes

3. **Configuration** (`config_backup_YYYYMMDD_HHMMSS.tar.gz`)
   - `.env.production`, nginx config, docker-compose, scripts

## Setup

### Cron (Production)

```bash
# Add to crontab -e
0 2 * * * cd /var/www/valuadis && ./scripts/backup.sh >> /var/www/valuadis/logs/backup.log 2>&1
```

### Environment Variables

- `POSTGRES_USER`, `POSTGRES_DB` - from docker-compose
- `SLACK_WEBHOOK_URL` (optional) - failure/success notifications

## Verification

Run after backup to verify integrity:

```bash
./scripts/verify_backup.sh
# Or verify specific file:
./scripts/verify_backup.sh /var/www/valuadis/backups/db_backup_20260307_020000.sql.gz
```

## Restore Procedure

1. Stop application: `docker-compose -f docker-compose.prod.yml down`
2. Restore DB: `gunzip -c backups/db_backup_YYYYMMDD.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U valuadis_user valuadis`
3. Restore uploads: `tar -xzf backups/uploads_backup_YYYYMMDD.tar.gz`
4. Start application: `docker-compose -f docker-compose.prod.yml up -d`

## Remote Storage (Optional)

Uncomment and configure in `scripts/backup.sh`:

```bash
# AWS S3
aws s3 sync "$BACKUP_DIR" "s3://your-bucket/valuadis-backups/"

# Or set REMOTE_BACKUP_URL for custom sync
```
