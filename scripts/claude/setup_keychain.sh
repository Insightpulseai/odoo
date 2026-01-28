#!/usr/bin/env bash
set -euo pipefail

# Interactive setup script for macOS Keychain secret storage
# Run once per development machine to configure Claude agent secrets

: "${CLAUDE_SECRET_SERVICE:=ipai_claude_secrets}"

echo "======================================================================"
echo "  Claude Agent Secret Setup - macOS Keychain"
echo "======================================================================"
echo ""
echo "This script will guide you through storing Claude agent secrets"
echo "in macOS Keychain with service name: ${CLAUDE_SECRET_SERVICE}"
echo ""
echo "Required secrets:"
echo "  - CLAUDE_API_KEY"
echo "  - SUPABASE_URL"
echo "  - SUPABASE_ANON_KEY"
echo "  - SUPABASE_SERVICE_ROLE_KEY"
echo ""
echo "Optional secrets:"
echo "  - OPENAI_API_KEY"
echo "  - GITHUB_TOKEN"
echo "  - ANTHROPIC_API_KEY"
echo "  - POSTGRES_PASSWORD"
echo ""
echo "======================================================================"
echo ""

read -rp "Continue? [y/N] " confirm
if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo ""

add_secret() {
  local name="$1"
  local required="${2:-false}"

  echo "──────────────────────────────────────────────────────────────────"
  echo "Setting: ${name}"
  echo "──────────────────────────────────────────────────────────────────"

  # Check if secret already exists
  existing="$(security find-generic-password -s "${CLAUDE_SECRET_SERVICE}" -a "${name}" -w 2>/dev/null || true)"

  if [[ -n "${existing}" ]]; then
    echo "⚠ Secret already exists in Keychain (${#existing} chars)"
    read -rp "Overwrite? [y/N] " overwrite
    if [[ ! "${overwrite}" =~ ^[Yy]$ ]]; then
      echo "Skipped."
      echo ""
      return 0
    fi
  fi

  read -rsp "Enter ${name} (input hidden): " value
  echo ""

  if [[ -z "${value}" ]]; then
    if [[ "${required}" == "true" ]]; then
      echo "ERROR: ${name} is required and cannot be empty." >&2
      exit 1
    else
      echo "Skipped (empty value)."
      echo ""
      return 0
    fi
  fi

  # Add or update secret in Keychain
  security add-generic-password \
    -s "${CLAUDE_SECRET_SERVICE}" \
    -a "${name}" \
    -w "${value}" \
    -U 2>/dev/null || {
      echo "ERROR: Failed to add secret to Keychain." >&2
      exit 1
    }

  echo "✅ Saved: ${name}"
  echo ""
}

# Required secrets
add_secret "CLAUDE_API_KEY" true
add_secret "SUPABASE_URL" true
add_secret "SUPABASE_ANON_KEY" true
add_secret "SUPABASE_SERVICE_ROLE_KEY" true

# Optional secrets
echo ""
echo "Optional secrets (press Enter to skip):"
echo ""

add_secret "OPENAI_API_KEY" false
add_secret "GITHUB_TOKEN" false
add_secret "ANTHROPIC_API_KEY" false
add_secret "POSTGRES_PASSWORD" false

echo "======================================================================"
echo "✅ Setup complete!"
echo "======================================================================"
echo ""
echo "Test the configuration:"
echo "  source ./scripts/claude/load_secrets_local.sh"
echo ""
echo "Run an agent:"
echo "  ./scripts/claude/run_agent.sh local <command>"
echo ""
