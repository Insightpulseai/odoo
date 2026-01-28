#!/usr/bin/env bash
set -euo pipefail

# macOS Keychain loader for Claude agent secrets
# Assumptions: secrets stored as generic passwords with service name "ipai_claude_secrets"

: "${CLAUDE_SECRET_SERVICE:=ipai_claude_secrets}"

# Required secrets for Claude agents
REQUIRED_SECRETS=(
  "CLAUDE_API_KEY"
  "SUPABASE_URL"
  "SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY"
)

# Optional secrets (best-effort loading)
OPTIONAL_SECRETS=(
  "OPENAI_API_KEY"
  "GITHUB_TOKEN"
  "ANTHROPIC_API_KEY"
  "POSTGRES_PASSWORD"
)

fetch_secret() {
  local name="$1"
  security find-generic-password \
    -s "${CLAUDE_SECRET_SERVICE}" \
    -a "${name}" \
    -w 2>/dev/null || true
}

export_secret() {
  local name="$1"
  local value
  value="$(fetch_secret "${name}")"

  if [[ -z "${value}" ]]; then
    return 1
  fi

  export "${name}=${value}"
  return 0
}

# Load required secrets
echo "Loading Claude secrets from macOS Keychain (service=${CLAUDE_SECRET_SERVICE})..."

for var in "${REQUIRED_SECRETS[@]}"; do
  if ! export_secret "${var}"; then
    echo "ERROR: Required secret ${var} not found in macOS Keychain." >&2
    echo "To add: security add-generic-password -s ${CLAUDE_SECRET_SERVICE} -a ${var} -w 'YOUR_VALUE' -U" >&2
    exit 1
  fi
  echo "✓ Loaded: ${var}"
done

# Load optional secrets (non-fatal if missing)
for var in "${OPTIONAL_SECRETS[@]}"; do
  if export_secret "${var}"; then
    echo "✓ Loaded optional: ${var}"
  else
    echo "⚠ Optional secret not found: ${var} (skipping)"
  fi
done

echo ""
echo "✅ All required Claude secrets loaded from macOS Keychain."
echo "   Service: ${CLAUDE_SECRET_SERVICE}"
echo "   Required: ${#REQUIRED_SECRETS[@]} secrets"
echo ""
