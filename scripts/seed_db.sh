#!/bin/bash
# ValuAdis Database Seeding Script
# Run with: ./scripts/seed_db.sh
# Uses docker-compose to run the seeder against the database

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🌱 Running ValuAdis database seeder..."

# Use dev compose by default; override with COMPOSE_FILE for prod
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

if [ -f "$COMPOSE_FILE" ]; then
    docker-compose -f "$COMPOSE_FILE" exec -T backend python seed_data.py
else
    echo "❌ $COMPOSE_FILE not found. Run from project root."
    exit 1
fi

echo "✅ Database seeding completed."
