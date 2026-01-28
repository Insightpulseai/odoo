#!/usr/bin/env bash
set -euo pipefail

# Assumptions / placeholders:
# - SUPABASE_SECRETS_ENDPOINT: URL of Edge Function / RPC that returns secret JSON
# - SUPABASE_SECRETS_TOKEN: token with permission to call this endpoint
: "${SUPABASE_SECRETS_ENDPOINT:?SUPABASE_SECRETS_ENDPOINT is required}"
: "${SUPABASE_SECRETS_TOKEN:?SUPABASE_SECRETS_TOKEN is required}"

json="$(curl -sS -H "Authorization: Bearer ${SUPABASE_SECRETS_TOKEN}" "${SUPABASE_SECRETS_ENDPOINT}")"

if [[ -z "${json}" ]]; then
  echo "ERROR: Empty response from Supabase Vault loader endpoint." >&2
  exit 1
fi

# Parse and export known keys. Using jq is recommended.
required_vars=(
  "CLAUDE_API_KEY"
  "SUPABASE_URL"
  "SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY"
)

optional_vars=(
  "OPENAI_API_KEY"
  "GITHUB_TOKEN"
)

for var in "${required_vars[@]}"; do
  value="$(printf '%s' "${json}" | jq -r --arg k "${var}" '.[$k] // empty')"
  if [[ -z "${value}" ]]; then
    echo "ERROR: Required secret ${var} missing from Vault payload." >&2
    exit 1
  fi
  export "${var}=${value}"
done

for var in "${optional_vars[@]}"; do
  value="$(printf '%s' "${json}" | jq -r --arg k "${var}" '.[$k] // empty')"
  if [[ -n "${value}" ]]; then
    export "${var}=${value}"
    echo "Loaded optional secret: ${var}"
  fi
done

echo "All required Claude secrets loaded from Supabase Vault."
