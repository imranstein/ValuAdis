#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${ROOT_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
MOBILE_DIR="${ROOT_DIR}/mobile"

RUN_BACKEND_TESTS="${RUN_BACKEND_TESTS:-1}"
RUN_FRONTEND_CHECKS="${RUN_FRONTEND_CHECKS:-1}"
RUN_MOBILE_CHECKS="${RUN_MOBILE_CHECKS:-0}"
RUN_E2E_CHECKS="${RUN_E2E_CHECKS:-0}"
RUN_E2E_SMOKE="${RUN_E2E_SMOKE:-0}"
MOBILE_REQUIRED="${MOBILE_REQUIRED:-0}"
BACKEND_HEALTH_URL="${BACKEND_HEALTH_URL:-http://127.0.0.1:8020/health}"
FRONTEND_HEALTH_URL="${FRONTEND_HEALTH_URL:-http://127.0.0.1:3020}"
E2E_BASE_URL="${E2E_BASE_URL:-http://127.0.0.1:${E2E_FRONTEND_PORT:-3020}}"
FLUTTER_BIN="${FLUTTER_BIN:-/Users/imranabdul/Dev/flutter/bin/flutter}"

log() {
  printf '%s\n' "$1"
}

check_local_socket_support() {
  /usr/bin/python3 -c "import socket; socket.socket().bind(('127.0.0.1', 0));"
}

verify_flutter_tool() {
  local output_file="$1"
  if "$FLUTTER_BIN" --version >"${output_file}" 2>&1; then
    return 0
  fi

  if grep -q "Operation not permitted" "${output_file}"; then
    return 2
  fi

  return 1
}

run_backend_checks() {
  if [[ "${RUN_BACKEND_TESTS}" != "1" ]]; then
    log "⏭️ Skipping backend checks"
    return 0
  fi

  log "🔧 Running backend quality gate"
  cd "${BACKEND_DIR}"
  /usr/bin/python3 -m pytest -q tests/test_scrapers_api.py
  cd "${ROOT_DIR}"

  if command -v curl >/dev/null 2>&1; then
    if check_local_socket_support >/dev/null 2>&1; then
      if curl -fsS "${BACKEND_HEALTH_URL}" > /dev/null; then
        log "✅ Backend health endpoint reachable: ${BACKEND_HEALTH_URL}"
      else
        log "⚠️ Backend health endpoint not reachable: ${BACKEND_HEALTH_URL}"
      fi
    else
      log "⚠️ Local socket binding is blocked in this runtime; backend health checks are skipped."
    fi
  else
    log "⚠️ curl not available; backend health check skipped"
  fi
}

run_frontend_checks() {
  if [[ "${RUN_FRONTEND_CHECKS}" != "1" ]]; then
    log "⏭️ Skipping frontend checks"
    return 0
  fi

  log "🔧 Running frontend readiness checks"
  cd "${FRONTEND_DIR}"
  npm run lint
  npm run build
  if command -v curl >/dev/null 2>&1; then
    if curl -fsS "${FRONTEND_HEALTH_URL}" > /dev/null; then
      log "✅ Frontend reachable: ${FRONTEND_HEALTH_URL}"
    else
      log "⚠️ Frontend not currently reachable: ${FRONTEND_HEALTH_URL}"
    fi
  else
    log "⚠️ curl not available; frontend health check skipped"
  fi
  cd "${ROOT_DIR}"
}

run_frontend_e2e_checks() {
  if [[ "${RUN_E2E_CHECKS}" != "1" ]]; then
    log "⏭️ Skipping frontend E2E discovery checks"
    return 0
  fi

  log "🔧 Running frontend E2E checks"
  cd "${ROOT_DIR}/frontend"

  local e2e_list_file
  e2e_list_file="$(mktemp)"

  if ! command -v npx >/dev/null 2>&1; then
    echo "❌ npx not available; cannot run Playwright checks" >&2
    cd "${ROOT_DIR}"
    return 1
  fi

  if ! PW_SKIP_WEBSERVER=1 E2E_BASE_URL="${E2E_BASE_URL}" npx playwright test --list > "${e2e_list_file}" 2>&1; then
    echo "❌ Playwright test discovery failed" >&2
    cat "${e2e_list_file}" >&2
    rm -f "${e2e_list_file}"
    cd "${ROOT_DIR}"
    return 1
  fi

  if grep -q "No tests found" "${e2e_list_file}"; then
    echo "⚠️ No E2E tests detected in playwright config" >&2
    rm -f "${e2e_list_file}"
    cd "${ROOT_DIR}"
    return 1
  fi

  local e2e_count
  e2e_count="$(grep -E -c "^\s*\[[^]]+\] › " "${e2e_list_file}")"
  log "✅ Frontend E2E discovery passed (${e2e_count} tests found)"

  if [[ "${RUN_E2E_SMOKE}" == "1" ]]; then
    if curl -fsS "${E2E_BASE_URL}" > /dev/null; then
      log "✅ Frontend E2E smoke will run against ${E2E_BASE_URL}"
      PW_SKIP_WEBSERVER=1 E2E_BASE_URL="${E2E_BASE_URL}" npx playwright test --project=chromium tests/e2e/pages/auth.spec.ts --grep "should login with valid credentials" || {
        echo "❌ Frontend E2E smoke failed" >&2
        rm -f "${e2e_list_file}"
        cd "${ROOT_DIR}"
        return 1
      }
    else
      log "⚠️ Frontend E2E smoke skipped; server is not reachable at ${E2E_BASE_URL}"
    fi
  fi

  rm -f "${e2e_list_file}"
  cd "${ROOT_DIR}"
}

run_mobile_checks() {
  if [[ "${RUN_MOBILE_CHECKS}" != "1" ]]; then
    log "⏭️ Skipping mobile checks"
    return 0
  fi

  if ! command -v "${FLUTTER_BIN}" >/dev/null 2>&1; then
    if [[ "${MOBILE_REQUIRED}" == "1" ]]; then
      echo "❌ Mobile required but flutter binary not found at ${FLUTTER_BIN}" >&2
      return 1
    fi
    log "⚠️ Flutter CLI not available; skipping optional mobile checks"
    return 0
  fi

  log "🔧 Running mobile quality gates and debug build"
  cd "${MOBILE_DIR}"
  local flutter_probe="$(mktemp)"
  verify_flutter_tool "${flutter_probe}" || {
    local flutter_status=$?
    local flutter_error="$(cat "${flutter_probe}")"
    rm -f "${flutter_probe}"
    if [[ "${flutter_status}" == "2" ]]; then
      log "⚠️ Flutter cache/write check failed due runtime restriction: ${flutter_error}"
      if [[ "${MOBILE_REQUIRED}" == "1" ]]; then
        echo "❌ Mobile checks blocked: Flutter is in read-only cache runtime." >&2
        cd "${ROOT_DIR}"
        return 1
      fi
      log "⚠️ Skipping mobile checks in read-only cache runtime."
      cd "${ROOT_DIR}"
      return 0
    fi

    echo "⚠️ Flutter command could not be executed:" >&2
    echo "${flutter_error}" >&2
    cd "${ROOT_DIR}"
    return 1
  }
  rm -f "${flutter_probe}"

  "${FLUTTER_BIN}" test test/quality/mobile_quality_gates_test.dart
  "${FLUTTER_BIN}" build apk --debug
  cd "${ROOT_DIR}"
}

main() {
  run_backend_checks
  run_frontend_checks
  run_frontend_e2e_checks
  run_mobile_checks

  log "✅ Operational readiness checks completed"
}

main "$@"
