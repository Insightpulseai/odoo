#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"

require_env SUPERSET_BASE_URL SUPERSET_USERNAME SUPERSET_PASSWORD DB_ID

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

token="$(superset_login "$tmp")"
csrf="$(superset_csrf "$token" "$tmp")"

echo "Testing DB connection DB_ID=$DB_ID"
api_post "$token" "$csrf" "/api/v1/database/${DB_ID}/test_connection" "{}" "$tmp" | cat
echo
