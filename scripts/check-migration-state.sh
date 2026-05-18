#!/usr/bin/env bash

set -euo pipefail

APP_TABLE_COUNT="${1:-}"
HAS_ALEMBIC_VERSION="${2:-}"
CURRENT_REVISION="${3:-}"
HEAD_REVISION="${4:-}"

if [[ -z "$APP_TABLE_COUNT" || -z "$HAS_ALEMBIC_VERSION" ]]; then
  echo "Usage: $0 <app_table_count> <has_alembic_version:true|false|t|f> [current_revision] [head_revision]" >&2
  exit 2
fi

case "$HAS_ALEMBIC_VERSION" in
  t|true|TRUE|1|yes|YES) normalized_has_alembic="true" ;;
  f|false|FALSE|0|no|NO) normalized_has_alembic="false" ;;
  *)
    echo "has_alembic_version must be true/false, t/f, 1/0, or yes/no" >&2
    exit 2
    ;;
esac

if [[ "$normalized_has_alembic" == "false" && "$APP_TABLE_COUNT" -gt 0 ]]; then
  echo "Database has application tables but no Alembic version. Refusing to run migrations against a partial schema." >&2
  echo "Restore a clean backup, run a controlled baseline/stamp procedure, or provision a fresh database before deployment." >&2
  exit 1
fi

if [[ -n "$HEAD_REVISION" && ( -z "$CURRENT_REVISION" || "$CURRENT_REVISION" != "$HEAD_REVISION" ) ]]; then
  echo "Database migration verification failed. Current revision: ${CURRENT_REVISION:-none}; head revision: ${HEAD_REVISION}." >&2
  exit 1
fi

echo "Database migration state check passed"
