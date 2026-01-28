#!/usr/bin/env bash
set -euo pipefail

# Supabase Vault loader for Claude agent secrets (CI/remote environments)
# Fetches secrets from Supabase Edge Function or RPC

: "${SUPABASE_SECRETS_ENDPOINT:?SUPABASE_SECRETS_ENDPOINT is required (Edge Function URL)}"
: "${SUPABASE_SECRETS_TOKEN:?SUPABASE_SECRETS_TOKEN is required (auth token for endpoint)}"

# Required secrets
REQUIRED_VARS=(
  "CLAUDE_API_KEY"
  "SUPABASE_URL"
  "SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY"
)

# Optional secrets
OPTIONAL_VARS=(
  "OPENAI_API_KEY"
  "GITHUB_TOKEN"
  "ANTHROPIC_API_KEY"
  "POSTGRES_PASSWORD"
)

echo "Loading Claude secrets from Supabase Vault..."
echo "Endpoint: ${SUPABASE_SECRETS_ENDPOINT}"

# Fetch secrets JSON from Edge Function
json="$(curl -sS -f -H "Authorization: Bearer ${SUPABASE_SECRETS_TOKEN}" "${SUPABASE_SECRETS_ENDPOINT}")"

if [[ -z "${json}" ]]; then
  echo "ERROR: Empty response from Supabase Vault loader endpoint." >&2
  exit 1
fi

# Verify jq is available
if ! command -v jq &> /dev/null; then
  echo "ERROR: jq is required but not installed. Install via: brew install jq" >&2
  exit 1
fi

# Load required secrets
for var in "${REQUIRED_VARS[@]}"; do
  value="$(printf '%s' "${json}" | jq -r --arg k "${var}" '.[$k] // empty')"
  if [[ -z "${value}" || "${value}" == "null" ]]; then
    echo "ERROR: Required secret ${var} missing from Vault payload." >&2
    exit 1
  fi
  export "${var}=${value}"
  echo "✓ Loaded: ${var}"
done

# Load optional secrets (non-fatal if missing)
for var in "${OPTIONAL_VARS[@]}"; do
  value="$(printf '%s' "${json}" | jq -r --arg k "${var}" '.[$k] // empty')"
  if [[ -n "${value}" && "${value}" != "null" ]]; then
    export "${var}=${value}"
    echo "✓ Loaded optional: ${var}"
  else
    echo "⚠ Optional secret not found: ${var} (skipping)"
  fi
done

echo ""
echo "✅ All required Claude secrets loaded from Supabase Vault."
echo "   Required: ${#REQUIRED_VARS[@]} secrets"
echo ""
