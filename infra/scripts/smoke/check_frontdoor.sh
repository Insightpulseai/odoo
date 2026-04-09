#!/usr/bin/env bash
set -euo pipefail

: "${FRONTDOOR_URL:?FRONTDOOR_URL is required}"
HEALTH_PATH="${HEALTH_PATH:-/web/health}"
LOGIN_PATH="${LOGIN_PATH:-/web/login}"

head_success() {
  local url="$1"
  local code
  code="$(curl -k -sSI -o /dev/null -w '%{http_code}' "$url")"
  if [[ "$code" -lt 200 || "$code" -ge 400 ]]; then
    echo "FAILED $url -> HTTP $code" >&2
    return 1
  fi
  echo "OK $url -> HTTP $code"
}

head_success "${FRONTDOOR_URL}${HEALTH_PATH}"
head_success "${FRONTDOOR_URL}${LOGIN_PATH}"
