#!/usr/bin/env bash
# scan-dependencies.sh — Runs npm audit (frontend) and pip-audit/safety (backend)
# Exits non-zero if critical vulnerabilities are found.
# Generates JSON reports under reports/dependency-scan/

set -euo pipefail

REPORT_DIR="reports/dependency-scan"
mkdir -p "$REPORT_DIR"

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
EXIT_CODE=0

# ─── Frontend: npm audit ──────────────────────────────────────────────────────
echo "==> Scanning frontend npm dependencies..."
if [ -f "frontend/package.json" ]; then
  # --audit-level=critical makes the command exit non-zero only on critical issues
  # --json captures the full report regardless of severity
  npm audit \
    --prefix frontend \
    --json \
    --audit-level=critical \
    > "$REPORT_DIR/npm-audit-${TIMESTAMP}.json" 2>&1 || {
      echo "[WARN] npm audit detected critical vulnerabilities in frontend dependencies."
      EXIT_CODE=1
    }
  echo "    Report: $REPORT_DIR/npm-audit-${TIMESTAMP}.json"
else
  echo "[SKIP] frontend/package.json not found — skipping npm audit."
fi

# ─── Backend: pip-audit (preferred) with safety fallback ─────────────────────
echo "==> Scanning backend Python dependencies..."
if [ -f "backend/requirements.txt" ]; then
  if command -v pip-audit &>/dev/null; then
    # pip-audit exits non-zero when vulnerabilities are found
    pip-audit \
      --requirement backend/requirements.txt \
      --format json \
      --output "$REPORT_DIR/pip-audit-${TIMESTAMP}.json" \
      --vulnerability-service pypi \
      || {
        echo "[WARN] pip-audit detected vulnerabilities in backend dependencies."
        EXIT_CODE=1
      }
    echo "    Report: $REPORT_DIR/pip-audit-${TIMESTAMP}.json"
  elif command -v safety &>/dev/null; then
    # Fallback to safety CLI (v3+)
    safety check \
      --file backend/requirements.txt \
      --json \
      > "$REPORT_DIR/safety-${TIMESTAMP}.json" 2>&1 \
      || {
        echo "[WARN] safety detected vulnerabilities in backend dependencies."
        EXIT_CODE=1
      }
    echo "    Report: $REPORT_DIR/safety-${TIMESTAMP}.json"
  else
    echo "[ERROR] Neither pip-audit nor safety is installed. Install one:"
    echo "        pip install pip-audit   # recommended"
    echo "        pip install safety"
    EXIT_CODE=1
  fi
else
  echo "[SKIP] backend/requirements.txt not found — skipping Python scan."
fi

# ─── Summary ─────────────────────────────────────────────────────────────────
echo ""
if [ "$EXIT_CODE" -eq 0 ]; then
  echo "==> Dependency scan PASSED. No critical vulnerabilities found."
else
  echo "==> Dependency scan FAILED. Critical vulnerabilities detected — see reports above."
fi

exit "$EXIT_CODE"
