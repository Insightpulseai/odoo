#!/usr/bin/env bash
set -euo pipefail

TARGET="${TARGET:-http://178.128.112.214:8766}"
TIMEOUT="${TIMEOUT:-10}"          # curl timeout seconds
API_KEY="${API_KEY:-}"            # optional for authenticated endpoints

PASS=0
FAIL=0

log_pass() { echo "✅ PASS: $1"; PASS=$((PASS+1)); }
log_fail() { echo "❌ FAIL: $1"; FAIL=$((FAIL+1)); }
log_info() { echo "ℹ️  INFO: $1"; }

# Curl wrapper:
# - returns HTTP status code only
# - never causes script to exit from curl failures (we handle)
http_code() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  local extra=()

  if [ -n "${API_KEY}" ]; then
    extra+=(-H "x-api-key: ${API_KEY}")
  fi

  if [ "$method" = "POST" ]; then
    curl -sS -m "${TIMEOUT}" -o /dev/null -w "%{http_code}" -X POST "${extra[@]}" \
      -H "content-type: application/json" \
      --data "${data}" \
      "${url}" || echo "000"
  else
    curl -sS -m "${TIMEOUT}" -o /dev/null -w "%{http_code}" -X GET "${extra[@]}" \
      "${url}" || echo "000"
  fi
}

expect_code() {
  local name="$1"
  local method="$2"
  local path="$3"
  local expected="$4"
  local data="${5:-}"

  local code
  code="$(http_code "$method" "${TARGET}${path}" "${data}")"

  if [ "$code" = "$expected" ]; then
    log_pass "${name} (${method} ${path} -> ${code})"
    return 0
  fi

  log_fail "${name} (${method} ${path} -> ${code}, expected ${expected})"
  return 1
}

echo "=== MCP Coordinator GitHub App Smoke Test ==="
echo "Target: ${TARGET}"

# Health should be 200
expect_code "Health endpoint" "GET" "/health" "200" || true

# Expected failure modes (no params / no signature / no auth):
expect_code "OAuth callback missing params" "GET" "/oauth/github/callback" "422" || true
expect_code "Webhook missing signature" "POST" "/webhooks/github" "401" '{}' || true
expect_code "Installations without API key" "GET" "/github/installations" "401" || true

# If API_KEY is provided, validate authenticated endpoints return success-ish codes.
if [ -n "${API_KEY}" ]; then
  expect_code "Installations with API key" "GET" "/github/installations" "200" || true
fi

echo "============================================"
echo "PASS=${PASS} FAIL=${FAIL}"

# Non-zero exit only if any FAIL
if [ "${FAIL}" -gt 0 ]; then
  exit 1
fi
