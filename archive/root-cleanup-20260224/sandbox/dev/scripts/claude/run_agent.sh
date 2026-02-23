#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-local}"  # "local" or "remote"

if [[ "${MODE}" == "local" ]]; then
  # macOS development
  source ./scripts/claude/load_secrets_local.sh
else
  # CI / remote
  source ./scripts/claude/load_secrets_remote.sh
fi

# Guardrails: ensure critical vars are present
: "${CLAUDE_API_KEY:?CLAUDE_API_KEY is required}"
: "${SUPABASE_URL:?SUPABASE_URL is required}"
: "${SUPABASE_ANON_KEY:?SUPABASE_ANON_KEY is required}"

# Example: run a Claude task file or agent CLI
# Replace with the actual entrypoint you use.
# claude-code run ./spec/agent_task.yaml

echo "✅ All secrets loaded. Environment ready for Claude agent execution."
echo "   MODE: ${MODE}"
echo "   CLAUDE_API_KEY: ${CLAUDE_API_KEY:0:10}..."
echo "   SUPABASE_URL: ${SUPABASE_URL}"
