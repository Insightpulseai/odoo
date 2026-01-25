#!/usr/bin/env bash
# Validates Spec Kit presence and structure for a given spec bundle
set -euo pipefail

SLUG="${1:-odoo-alternatives}"
BASE="spec/${SLUG}"

req=(
  "${BASE}/constitution.md"
  "${BASE}/prd.md"
  "${BASE}/plan.md"
  "${BASE}/tasks.md"
)

echo "Validating Spec Kit: ${SLUG}"

for f in "${req[@]}"; do
  [[ -f "$f" ]] || { echo "Missing: $f"; exit 1; }
  [[ -s "$f" ]] || { echo "Empty: $f"; exit 1; }
done

# Basic structure checks
grep -q "^# Constitution" "${BASE}/constitution.md" || { echo "constitution.md missing title"; exit 1; }
grep -q "^# PRD"          "${BASE}/prd.md"          || { echo "prd.md missing title"; exit 1; }
grep -q "^# Plan"         "${BASE}/plan.md"         || { echo "plan.md missing title"; exit 1; }
grep -q "^# Tasks"        "${BASE}/tasks.md"        || { echo "tasks.md missing title"; exit 1; }

echo "OK: Spec Kit present for ${SLUG}"
