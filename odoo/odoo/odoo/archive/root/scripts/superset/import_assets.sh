#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"

require_env SUPERSET_BASE_URL SUPERSET_USERNAME SUPERSET_PASSWORD SUPERSET_ASSET_ZIP_PATH

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

token="$(superset_login "$tmp")"
csrf="$(superset_csrf "$token" "$tmp")"

zip_path="$SUPERSET_ASSET_ZIP_PATH"
[[ -f "$zip_path" ]] || { echo "Missing zip: $zip_path" >&2; exit 2; }

echo "Importing Superset assets from $zip_path"

curl -sS -b "$tmp/cookies.txt" \
  -H "Authorization: Bearer $token" \
  -H "X-CSRFToken: $csrf" \
  -F "formData=@${zip_path}" \
  -F "overwrite=true" \
  -X POST "$SUPERSET_BASE_URL/api/v1/assets/import/" | cat
echo
