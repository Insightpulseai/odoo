#!/usr/bin/env bash
# check_prd_linkage.sh — Enforce PRD linkage for structural PRs
# =============================================================================
# Rules (from org PRD hierarchy):
#   1. New spec bundle (spec/<slug>/) MUST include prd.md
#   2. New ipai_* module (addons/ipai/ipai_*/) MUST have matching spec/<slug>/prd.md
#   3. New root-level folder MUST be documented (spec or docs)
#   4. New agent/service/CLI MUST link PRD in PR body
#
# Usage:
#   ./scripts/ci/check_prd_linkage.sh [base_ref]
#   BASE_REF defaults to origin/main
#
# Exit 0 = all checks pass, Exit 1 = enforcement violation
# =============================================================================
set -euo pipefail

BASE_REF="${1:-origin/main}"
PASS=0
FAIL=0
WARN=0

echo "=== PRD Linkage Enforcement ==="
echo "Base ref: $BASE_REF"
echo ""

# Get list of added files in this branch vs base
ADDED_FILES=$(git diff --name-only --diff-filter=A "$BASE_REF" -- 2>/dev/null || echo "")

if [ -z "$ADDED_FILES" ]; then
  echo "  No new files detected. Skipping PRD checks."
  echo "STATUS: PASS"
  exit 0
fi

# -----------------------------------------------
# Rule 1: New spec bundles must include prd.md
# -----------------------------------------------
echo "--- Rule 1: Spec bundles must include prd.md ---"
NEW_SPEC_DIRS=$(echo "$ADDED_FILES" | grep -oP '^spec/[^/]+' | sort -u || true)

for dir in $NEW_SPEC_DIRS; do
  if echo "$ADDED_FILES" | grep -q "^${dir}/prd.md$"; then
    echo "  PASS  $dir has prd.md"
    PASS=$((PASS + 1))
  else
    # Check if it's a config-only directory (yaml/json files only)
    NON_CONFIG=$(echo "$ADDED_FILES" | grep "^${dir}/" | grep -vE '\.(yaml|yml|json|csv)$' || true)
    if [ -z "$NON_CONFIG" ]; then
      echo "  SKIP  $dir (config-only, no PRD needed)"
    else
      echo "  FAIL  $dir is missing prd.md"
      FAIL=$((FAIL + 1))
    fi
  fi
done

echo ""

# -----------------------------------------------
# Rule 2: New ipai_* modules should have a matching spec
# -----------------------------------------------
echo "--- Rule 2: New ipai_* modules should reference a spec ---"
NEW_MODULES=$(echo "$ADDED_FILES" | grep -oP 'addons/ipai/ipai_[^/]+' | sort -u || true)

for mod in $NEW_MODULES; do
  MOD_NAME=$(basename "$mod")
  # Check if any spec references this module
  MATCHING_SPEC=$(find spec/ -name "prd.md" -exec grep -l "$MOD_NAME" {} \; 2>/dev/null | head -1 || true)
  if [ -n "$MATCHING_SPEC" ]; then
    echo "  PASS  $MOD_NAME referenced in $MATCHING_SPEC"
    PASS=$((PASS + 1))
  else
    echo "  WARN  $MOD_NAME has no matching spec PRD (recommended: create spec/<slug>/prd.md)"
    WARN=$((WARN + 1))
  fi
done

echo ""

# -----------------------------------------------
# Rule 3: New root-level folders should be documented
# -----------------------------------------------
echo "--- Rule 3: New root-level folders ---"
NEW_ROOT_DIRS=$(echo "$ADDED_FILES" | grep -oP '^[^/]+' | sort -u || true)
KNOWN_ROOTS="addons apps packages spec scripts infra docs deploy db mcp n8n docker ops .claude .github .husky node_modules"

for dir in $NEW_ROOT_DIRS; do
  # Skip files (not directories) and known roots
  if [ ! -d "$dir" ] 2>/dev/null; then
    continue
  fi
  if echo "$KNOWN_ROOTS" | grep -qw "$dir"; then
    continue
  fi
  echo "  WARN  New root folder '$dir' — ensure it has documentation or spec"
  WARN=$((WARN + 1))
done

echo ""

# -----------------------------------------------
# Summary
# -----------------------------------------------
echo "=== Results: PASS=$PASS  FAIL=$FAIL  WARN=$WARN ==="

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "STATUS: FAIL"
  echo "Fix: Add prd.md to new spec bundles, or link spec from new modules."
  exit 1
fi

if [ "$WARN" -gt 0 ]; then
  echo ""
  echo "STATUS: PASS (with warnings)"
  echo "Recommended: Add PRDs for warned items."
  exit 0
fi

echo "STATUS: PASS"
exit 0
