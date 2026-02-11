#!/usr/bin/env bash
set -euo pipefail

# Required credentials
: "${VERCEL_TOKEN:?VERCEL_TOKEN is required}"
: "${VERCEL_PROJECT_ID:?VERCEL_PROJECT_ID is required}"
: "${DOMAIN:?DOMAIN is required (e.g. app.yourdomain.com)}"

echo "Adding domain ${DOMAIN} to project ${VERCEL_PROJECT_ID}..."

curl -fsS -X POST "https://api.vercel.com/v9/projects/${VERCEL_PROJECT_ID}/domains" \
  -H "Authorization: Bearer ${VERCEL_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${DOMAIN}\"}" | jq .

echo "OK: domain added"
