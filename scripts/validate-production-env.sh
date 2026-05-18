#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="${1:-.env.production}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Production environment file not found: $ENV_FILE" >&2
  exit 1
fi

load_value() {
  local key="$1"
  local value
  value="$(grep -E "^${key}=" "$ENV_FILE" | tail -1 | cut -d '=' -f2- || true)"
  printf '%s' "$value"
}

require_value() {
  local key="$1"
  local value
  value="$(load_value "$key")"
  if [[ -z "$value" ]]; then
    echo "$key is required in $ENV_FILE" >&2
    exit 1
  fi
  if [[ "$value" =~ (REPLACE_WITH|YOUR_|your-|change-this|changeme|placeholder|example\.com) ]]; then
    echo "$key still contains a placeholder value" >&2
    exit 1
  fi
}

require_url() {
  local key="$1"
  local value
  require_value "$key"
  value="$(load_value "$key")"
  if [[ ! "$value" =~ ^https:// ]]; then
    echo "$key must be an https:// URL" >&2
    exit 1
  fi
  if [[ "$value" =~ (localhost|127\.0\.0\.1) ]]; then
    echo "$key must not point to localhost in production" >&2
    exit 1
  fi
}

require_api_origin() {
  local key="$1"
  local value
  require_url "$key"
  value="$(load_value "$key")"
  if [[ "$value" =~ /api(/v[0-9]+)?/?$ ]]; then
    echo "$key must be the API origin only; the frontend appends /api/v1" >&2
    exit 1
  fi
}

require_no_localhost() {
  local key="$1"
  local value
  require_value "$key"
  value="$(load_value "$key")"
  if [[ "$value" =~ (localhost|127\.0\.0\.1) ]]; then
    echo "$key must not contain localhost in production" >&2
    exit 1
  fi
}

require_https_origins() {
  local key="$1"
  local value
  require_no_localhost "$key"
  value="$(load_value "$key")"

  # Prevent glob expansion so "*" remains literal while validating
  set -f

  local IFS=","
  local origin
  for origin in $value; do
    origin="$(echo "$origin" | tr -d '[:space:]')"
    if [[ -z "$origin" ]]; then
      echo "$key contains an empty origin entry" >&2
      exit 1
    fi

    if [[ ! "$origin" =~ ^https:// ]]; then
      echo "$key entry '$origin' must be an https:// URL" >&2
      exit 1
    fi
  done

  set +f
}

require_value "PROD_POSTGRES_PASSWORD"
require_value "PROD_REDIS_PASSWORD"
require_value "PROD_SECRET_KEY"
require_value "PROD_ALLOWED_HOSTS"
require_api_origin "PROD_NUXT_PUBLIC_API_BASE_URL"

secret_key="$(load_value "PROD_SECRET_KEY")"
if [[ "${#secret_key}" -lt 32 ]]; then
  echo "PROD_SECRET_KEY must be at least 32 characters" >&2
  exit 1
fi

require_no_localhost "PROD_ALLOWED_HOSTS"
require_https_origins "PROD_ALLOWED_HOSTS"

allowed_hosts="$(load_value "PROD_ALLOWED_HOSTS")"
if [[ "$allowed_hosts" == *"*"* ]]; then
  echo "PROD_ALLOWED_HOSTS must list explicit deployed origins, not '*'" >&2
  exit 1
fi

echo "Production environment validation passed for $ENV_FILE"
