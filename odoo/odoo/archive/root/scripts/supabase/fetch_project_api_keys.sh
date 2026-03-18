#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Fetch Supabase Project API Keys
# ========================================
# Retrieves current API keys from Supabase Management API
# Usage: ./fetch_project_api_keys.sh

: "${SUPABASE_ACCESS_TOKEN:?set SUPABASE_ACCESS_TOKEN (Supabase PAT)}"
: "${SUPABASE_PROJECT_REF:?set SUPABASE_PROJECT_REF (project ref)}"

API="https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/api-keys"

echo "🔑 Fetching API keys for project: ${SUPABASE_PROJECT_REF}" >&2
echo "" >&2

curl -fsSL "$API" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
