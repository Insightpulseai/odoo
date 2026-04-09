#!/usr/bin/env bash
set -euo pipefail

: "${BASE_URL:?BASE_URL is required}"
HEALTH_PATH="${HEALTH_PATH:-/web/health}"
LOGIN_PATH="${LOGIN_PATH:-/web/login}"

check_http_success() {
  local url="$1"
  local code
  code="$(curl -k -sS -o /dev/null -w '%{http_code}' "$url")"
  if [[ "$code" -lt 200 || "$code" -ge 400 ]]; then
    echo "FAILED $url -> HTTP $code" >&2
    return 1
  fi
  echo "OK $url -> HTTP $code"
}

check_http_success "${BASE_URL}${HEALTH_PATH}"
check_http_success "${BASE_URL}${LOGIN_PATH}"
