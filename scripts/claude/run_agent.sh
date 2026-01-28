#!/usr/bin/env bash
set -euo pipefail

# Universal agent runner with secret loading
# Usage: ./scripts/claude/run_agent.sh [local|remote] [agent_command...]

MODE="${1:-local}"
shift || true

case "${MODE}" in
  local)
    echo "🔐 Loading secrets from macOS Keychain..."
    # shellcheck source=./load_secrets_local.sh
    source "$(dirname "$0")/load_secrets_local.sh"
    ;;
  remote)
    echo "🔐 Loading secrets from Supabase Vault..."
    # shellcheck source=./load_secrets_remote.sh
    source "$(dirname "$0")/load_secrets_remote.sh"
    ;;
  *)
    echo "ERROR: Invalid mode '${MODE}'. Use 'local' or 'remote'." >&2
    echo "Usage: $0 [local|remote] [agent_command...]" >&2
    exit 1
    ;;
esac

# Mandatory environment variable checks
echo ""
echo "🔍 Verifying required environment variables..."

: "${CLAUDE_API_KEY:?CLAUDE_API_KEY is required}"
: "${SUPABASE_URL:?SUPABASE_URL is required}"
: "${SUPABASE_ANON_KEY:?SUPABASE_ANON_KEY is required}"
: "${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY is required}"

echo "✅ All required environment variables present."
echo ""

# Run agent command if provided
if [[ $# -gt 0 ]]; then
  echo "🚀 Running agent command: $*"
  echo ""
  exec "$@"
else
  echo "✅ Environment ready for agent execution."
  echo ""
  echo "Example usage:"
  echo "  ./scripts/claude/run_agent.sh local claude-code run ./spec/agent_task.yaml"
  echo "  ./scripts/claude/run_agent.sh local python -m tools.agent_entrypoint"
  echo "  ./scripts/claude/run_agent.sh remote npm run agent:run"
fi
