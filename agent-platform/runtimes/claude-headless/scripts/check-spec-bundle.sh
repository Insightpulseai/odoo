#!/usr/bin/env bash
# Check a Spec Kit bundle for internal consistency using Claude headless.
# Usage: check-spec-bundle.sh <bundle-dir> [output.json]
set -euo pipefail

BUNDLE="${1:?bundle path required, e.g. spec/pulser-odoo}"
OUT="${2:-/dev/stdout}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/run.sh"

PROMPT=$(cat <<EOF
Check the Spec Kit bundle at $BUNDLE for internal consistency.
Verify that constitution.md, prd.md, plan.md, and tasks.md exist and are aligned:
- Every principle in constitution.md has at least one corresponding PRD section.
- Every PRD requirement is covered by at least one plan section.
- Every plan section has at least one task with a SMART criterion.
- No contradictions between sections.
- No broken cross-references.

Return a structured JSON report matching the provided schema.
EOF
)

claude_bare_json \
  "$PROMPT" \
  "$SCRIPT_DIR/../schemas/spec-check.json" \
  --allowedTools "Read,Grep,Glob" \
  --append-system-prompt "You are a Spec Kit auditor. Be strict about SMART criteria and cross-references. Do not invent sections that don't exist." \
  > "$OUT"
