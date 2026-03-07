# Zero-Downtime Migrations (VA-113)

## Overview

Guidelines for deploying database migrations without service interruption.

## Principles

1. **Additive changes first**: Add new columns/tables before removing old ones.
2. **Backward-compatible deploys**: New code must work with old schema; old code with new schema during rollout.
3. **Multi-phase migrations**: Split breaking changes into multiple migrations.

## Safe Migration Patterns

### Adding a Column (Nullable)

```python
# Migration 1: Add column as nullable
op.add_column('users', sa.Column('new_field', sa.String(100), nullable=True))

# Deploy new code that writes to new_field

# Migration 2 (optional): Backfill, then add NOT NULL
op.execute("UPDATE users SET new_field = 'default' WHERE new_field IS NULL")
op.alter_column('users', 'new_field', nullable=False)
```

### Adding a Column (Non-Nullable with Default)

```python
op.add_column('users', sa.Column('status', sa.String(20), nullable=False, server_default='active'))
```

### Adding an Index

```python
# Use CONCURRENTLY in PostgreSQL to avoid locking
op.execute("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_name ON table(column)")
```

### Dropping a Column (Multi-Phase)

```python
# Phase 1: Deploy code that stops using the column
# Phase 2: Migration to drop column
op.drop_column('table', 'old_column')
```

## Deployment Steps

1. **Backup**: Run `scripts/backup.sh` before any migration.
2. **Test**: Run migrations against a staging database.
3. **Deploy migration**: `alembic upgrade head` (during low traffic if possible).
4. **Deploy application**: Roll out new code.
5. **Verify**: Check health endpoints and logs.

## Docker Compose

```bash
# Run migrations in prod
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Or as a one-off before starting new containers
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

## Rollback

- **Alembic downgrade**: `alembic downgrade -1` (use with caution; ensure downgrade path is tested).
- **Restore backup**: Use `scripts/backup.sh` output and PostgreSQL restore if needed.

## Checklist

- [ ] Backup taken
- [ ] Migration tested on staging
- [ ] Downgrade path tested (if applicable)
- [ ] Low-traffic window (for schema changes)
- [ ] Health checks passing after deploy
