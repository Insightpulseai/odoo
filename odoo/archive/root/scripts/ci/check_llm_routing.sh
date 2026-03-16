#!/usr/bin/env bash
# check_llm_routing.sh — CI regression guard
#
# Fail if any addon bypasses ProviderRouter with direct LLM HTTP calls.
# Lines can be exempted with a trailing "# ALLOW:" comment.
#
# Usage:
#   bash scripts/ci/check_llm_routing.sh
#   # Returns 0 (pass) or 1 (fail)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ADDONS_DIR="${REPO_ROOT}/addons"

echo "Checking: addons must not call LLM provider endpoints directly..."

HITS=$(rg -n "IPAI_LLM_BASE_URL|/v1/chat/completions|/api/generate" \
  --type py --type js "$ADDONS_DIR" 2>/dev/null \
  | grep -v "# ALLOW:" || true)

if [ -n "$HITS" ]; then
  echo "ERROR: direct LLM HTTP calls detected:"
  echo "$HITS"
  echo ""
  echo "Route via infra/ai/provider_router/router.py instead."
  echo "To exempt a line, append '# ALLOW:' at the end of that line."
  exit 1
fi

echo "OK: no direct LLM calls in addons/."
