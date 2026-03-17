#!/usr/bin/env bash
# Run from repo root or mobile/: ensures Flutter project is created, deps fetched, then runs app.
set -e
cd "$(dirname "$0")/.."

if ! command -v flutter &>/dev/null; then
  echo "Flutter not found in PATH. Install Flutter or add it to PATH and retry."
  exit 1
fi

echo "Flutter: $(flutter --version | head -1)"
echo "Creating platform files if missing..."
flutter create . --project-name valuadis 2>/dev/null || true

echo "Getting dependencies..."
flutter pub get

echo "Running app..."
flutter run
