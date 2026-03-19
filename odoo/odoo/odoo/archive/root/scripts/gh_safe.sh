#!/usr/bin/env bash
# scripts/gh_safe.sh — safe GitHub CLI wrapper for agent and CI contexts
#
# Problem: `gh` prefers GH_TOKEN over GITHUB_TOKEN in many environments.
#   When GITHUB_TOKEN is set but GH_TOKEN is not, `gh` can fall back to an
#   interactive keyring account whose token may be invalid for the target repo.
#
# Solution: Always derive GH_TOKEN from GITHUB_TOKEN before invoking `gh`.
#   Accepts either GH_TOKEN or GITHUB_TOKEN; fails fast when neither is present.
#
# Usage (drop-in replacement for `gh`):
#   scripts/gh_safe.sh pr view 429 --repo Insightpulseai/odoo --json title
#   scripts/gh_safe.sh pr edit 429 --body "..."
#
# In agent runbooks / CI steps, replace bare `gh ...` with:
#   scripts/gh_safe.sh ...
#
# Env vars (at least one required):
#   GH_TOKEN      — takes precedence (gh's own preferred var)
#   GITHUB_TOKEN  — fallback; exported as GH_TOKEN if GH_TOKEN is absent
#   GH_HOST       — defaults to github.com; override for GHES

set -euo pipefail

GH_TOKEN_VAL="${GH_TOKEN:-}"
GITHUB_TOKEN_VAL="${GITHUB_TOKEN:-}"

if [[ -z "$GH_TOKEN_VAL" && -z "$GITHUB_TOKEN_VAL" ]]; then
  echo "ERROR: scripts/gh_safe.sh requires GH_TOKEN or GITHUB_TOKEN to be set." >&2
  echo "  Export one before calling this script, or use CI secrets injection." >&2
  exit 1
fi

# gh prefers GH_TOKEN; derive from GITHUB_TOKEN if not already set
export GH_TOKEN="${GH_TOKEN_VAL:-$GITHUB_TOKEN_VAL}"
export GH_HOST="${GH_HOST:-github.com}"

exec gh "$@"
