#!/bin/sh
# ValuAdis: bring up the local Postgres + PostGIS dev database (one command).
#
# Starts the `db` service from docker-compose.yml, waits until it reports
# healthy, then runs `alembic upgrade head` so the real migration chain
# (including migration 001's CREATE EXTENSION postgis) is applied against a
# genuine PostGIS engine — not the SQLite spatial stubs used by unit tests.
#
# POSIX sh, no exotic dependencies. Requires: docker (with the compose plugin
# or docker-compose), and a backend Python env with alembic installed.
set -eu

# Resolve repo root from this script's location so it runs from anywhere.
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
BACKEND_DIR="$REPO_ROOT/backend"

# Dev credentials/ports (match docker-compose.yml `db` service).
DB_USER="valuadis_user"
DB_NAME="valuadis"
DB_PASSWORD="${DB_PASSWORD:-changeme}"
DB_HOST="localhost"
DB_PORT="5433"
SERVICE="db"

# Prefer `docker compose` (v2 plugin); fall back to legacy `docker-compose`.
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "ERROR: neither 'docker compose' nor 'docker-compose' is available." >&2
    exit 1
fi

cd "$REPO_ROOT"

echo "==> Starting Postgres + PostGIS ($SERVICE) ..."
# shellcheck disable=SC2086
$COMPOSE up -d "$SERVICE"

echo "==> Waiting for $SERVICE to become healthy ..."
ATTEMPTS=0
MAX_ATTEMPTS=60
while [ "$ATTEMPTS" -lt "$MAX_ATTEMPTS" ]; do
    # shellcheck disable=SC2086
    if $COMPOSE exec -T "$SERVICE" pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
        echo "==> Database is ready."
        break
    fi
    ATTEMPTS=$((ATTEMPTS + 1))
    sleep 2
done

if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "ERROR: database did not become healthy in time." >&2
    # shellcheck disable=SC2086
    $COMPOSE logs "$SERVICE" >&2 || true
    exit 1
fi

DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

echo "==> Running 'alembic upgrade head' against $DB_HOST:$DB_PORT/$DB_NAME ..."
cd "$BACKEND_DIR"
DATABASE_URL="$DATABASE_URL" alembic upgrade head

echo ""
echo "==> Local dev database is up and migrated."
echo "    DATABASE_URL=$DATABASE_URL"
echo ""
echo "Next steps:"
echo "  1. Seed an admin user:"
echo "       cd backend && DATABASE_URL=\"$DATABASE_URL\" python create_admin.py"
echo "  2. Start the API:"
echo "       cd backend && DATABASE_URL=\"$DATABASE_URL\" uvicorn app.main:app --reload"
echo ""
echo "To stop the database:  docker compose stop db"
echo "To reset it entirely:  docker compose down -v   (deletes the postgres_data volume)"
