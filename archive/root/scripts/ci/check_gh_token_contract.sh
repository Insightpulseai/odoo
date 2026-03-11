#!/usr/bin/env bash
# scripts/ci/check_gh_token_contract.sh — CI gate: require GH auth token
#
# Fail fast when a workflow step uses `gh` but neither GH_TOKEN nor GITHUB_TOKEN
# is present in the environment. Wire into any job that calls `gh`, scripts/gh_safe.sh,
# or any agent step that edits/views/lists GitHub PRs, issues, or releases.
#
# Usage (in a GitHub Actions step or local CI):
#   bash scripts/ci/check_gh_token_contract.sh
#
# Exit codes:
#   0  — at least one valid token env var is set (non-empty)
#   1  — neither GH_TOKEN nor GITHUB_TOKEN is set; outputs actionable error

set -euo pipefail

GH_TOKEN_VAL="${GH_TOKEN:-}"
GITHUB_TOKEN_VAL="${GITHUB_TOKEN:-}"

if [[ -z "$GH_TOKEN_VAL" && -z "$GITHUB_TOKEN_VAL" ]]; then
  echo "ERROR: GitHub CLI auth contract violated." >&2
  echo "  GH_TOKEN or GITHUB_TOKEN must be set for any step that calls 'gh'." >&2
  echo "  In GitHub Actions: add 'env: GH_TOKEN: \${{ secrets.GITHUB_TOKEN }}' to the job." >&2
  echo "  Locally: export GITHUB_TOKEN=<your-pat> before running gh commands." >&2
  echo "  Use scripts/gh_safe.sh as a drop-in for 'gh' to enforce this automatically." >&2
  exit 1
fi

# Prefer GH_TOKEN (gh's own env var) — log which source is active
if [[ -n "$GH_TOKEN_VAL" ]]; then
  echo "OK: GH_TOKEN is set (${#GH_TOKEN_VAL} chars)."
else
  echo "OK: GITHUB_TOKEN is set (${#GITHUB_TOKEN_VAL} chars). Consider also exporting GH_TOKEN=\$GITHUB_TOKEN."
fi
