#!/usr/bin/env bash
# Review a PR diff using Claude headless with structured JSON output.
# Usage: review-pr.sh <base-branch> <head-branch> [output.json]
set -euo pipefail

BASE="${1:-main}"
HEAD="${2:-HEAD}"
OUT="${3:-/dev/stdout}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
source "$SCRIPT_DIR/../lib/run.sh"

DIFF=$(git -C "$ROOT" diff "$BASE"..."$HEAD")
CHANGED_FILES=$(git -C "$ROOT" diff --name-only "$BASE"..."$HEAD")

PROMPT=$(cat <<EOF
Review this PR diff for security, correctness, migration safety, and performance.
Return a structured JSON report matching the provided schema.

Changed files:
$CHANGED_FILES

Diff:
$DIFF
EOF
)

claude_bare_json \
  "$PROMPT" \
  "$SCRIPT_DIR/../schemas/pr-review.json" \
  --allowedTools "Read,Grep,Glob" \
  --append-system-prompt "You are a senior code reviewer for the InsightPulseAI platform (Odoo CE 18 + Azure). Focus on: secrets exposure, OCA/CE compliance, SQL safety, migration reversibility, cost impact, and reporting-policy violations (no pricing in AI outputs). Be concise." \
  > "$OUT"
