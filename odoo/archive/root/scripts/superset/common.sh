#!/usr/bin/env bash
set -euo pipefail

require_env() { for v in "$@"; do [[ -n "${!v:-}" ]] || { echo "Missing env: $v" >&2; exit 2; }; done; }

superset_login() {
  require_env SUPERSET_BASE_URL SUPERSET_USERNAME SUPERSET_PASSWORD
  local tmp="${1:?tmpdir}"
  local cookiejar="$tmp/cookies.txt"

  curl -sS -c "$cookiejar" -b "$cookiejar" \
    -H "Content-Type: application/json" \
    -X POST "$SUPERSET_BASE_URL/api/v1/security/login" \
    -d "{\"username\":\"$SUPERSET_USERNAME\",\"password\":\"$SUPERSET_PASSWORD\",\"provider\":\"db\",\"refresh\":true}" \
    > "$tmp/login.json"

  python - <<'PY' "$tmp/login.json"
import json,sys
j=json.load(open(sys.argv[1]))
print(j["access_token"])
PY
}

superset_csrf() {
  local token="${1:?token}" tmp="${2:?tmpdir}"
  local cookiejar="$tmp/cookies.txt"
  curl -sS -c "$cookiejar" -b "$cookiejar" \
    -H "Authorization: Bearer $token" \
    "$SUPERSET_BASE_URL/api/v1/security/csrf_token/" \
  | python - <<'PY'
import json,sys
print(json.load(sys.stdin)["result"])
PY
}

api_get() {
  local token="$1" csrf="$2" path="$3" tmp="$4"
  curl -sS -b "$tmp/cookies.txt" \
    -H "Authorization: Bearer $token" \
    -H "X-CSRFToken: $csrf" \
    "$SUPERSET_BASE_URL$path"
}

api_post() {
  local token="$1" csrf="$2" path="$3" body="$4" tmp="$5"
  curl -sS -b "$tmp/cookies.txt" \
    -H "Authorization: Bearer $token" \
    -H "X-CSRFToken: $csrf" \
    -H "Content-Type: application/json" \
    -X POST "$SUPERSET_BASE_URL$path" \
    -d "$body"
}

api_put() {
  local token="$1" csrf="$2" path="$3" body="$4" tmp="$5"
  curl -sS -b "$tmp/cookies.txt" \
    -H "Authorization: Bearer $token" \
    -H "X-CSRFToken: $csrf" \
    -H "Content-Type: application/json" \
    -X PUT "$SUPERSET_BASE_URL$path" \
    -d "$body"
}

api_delete() {
  local token="$1" csrf="$2" path="$3" tmp="$4"
  curl -sS -b "$tmp/cookies.txt" \
    -H "Authorization: Bearer $token" \
    -H "X-CSRFToken: $csrf" \
    -X DELETE "$SUPERSET_BASE_URL$path"
}
