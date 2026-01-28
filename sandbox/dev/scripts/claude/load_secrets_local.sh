#!/usr/bin/env bash
set -euo pipefail

# Assumptions (update if you change Keychain service name)
: "${CLAUDE_SECRET_SERVICE:=ipai_claude_secrets}"

# List of env vars we care about
REQUIRED_SECRETS=(
  "CLAUDE_API_KEY"
  "SUPABASE_URL"
  "SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY"
)

OPTIONAL_SECRETS=(
  "OPENAI_API_KEY"
  "GITHUB_TOKEN"
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
for var in "${REQUIRED_SECRETS[@]}"; do
  if ! export_secret "${var}"; then
    echo "ERROR: Required secret ${var} not found in macOS Keychain (service=${CLAUDE_SECRET_SERVICE})." >&2
    exit 1
  fi
done

# Load optional secrets (best-effort)
for var in "${OPTIONAL_SECRETS[@]}"; do
  if export_secret "${var}"; then
    echo "Loaded optional secret: ${var}"
  fi
done

echo "All required Claude secrets loaded from macOS Keychain."
