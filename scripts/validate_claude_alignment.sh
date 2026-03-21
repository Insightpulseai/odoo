#!/usr/bin/env bash
# validate_claude_alignment.sh — Drift guard for CLAUDE.md hierarchy
# Ensures no oversized files, no duplicates, no deprecated references, no contradictions.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

echo "=== CLAUDE.md Alignment Validator ==="
echo ""

# 1. Size check: innermost CLAUDE.md must be ≤200 lines
INNERMOST="$REPO_ROOT/odoo/odoo/odoo/CLAUDE.md"
if [ -f "$INNERMOST" ]; then
  LINES=$(wc -l < "$INNERMOST" | tr -d ' ')
  if [ "$LINES" -gt 200 ]; then
    echo "FAIL: $INNERMOST is $LINES lines (max 200)"
    FAIL=1
  else
    echo "PASS: innermost CLAUDE.md is $LINES lines"
  fi
else
  echo "WARN: $INNERMOST not found"
fi

# 2. Shim check: mid-level CLAUDE.md files must be ≤10 lines (shims)
for SHIM in "$REPO_ROOT/odoo/CLAUDE.md" "$REPO_ROOT/odoo/odoo/CLAUDE.md"; do
  if [ -f "$SHIM" ]; then
    LINES=$(wc -l < "$SHIM" | tr -d ' ')
    if [ "$LINES" -gt 10 ]; then
      echo "FAIL: $SHIM is $LINES lines (should be a shim ≤10 lines)"
      FAIL=1
    else
      echo "PASS: $(basename "$(dirname "$SHIM")")/CLAUDE.md is a shim ($LINES lines)"
    fi
  fi
done

# 3. Deprecated string check across all CLAUDE.md and rules files
DEPRECATED_PATTERNS=(
  "insightpulseai\.net"
  "odoo-ce"
  "Mattermost"
  "Appfine"
  "ipai_mattermost"
  "DigitalOcean"
  "mg\.insightpulseai"
)
# Allowlist: deprecated tables, comments about deprecation, and this script
CLAUDE_FILES=$(find "$REPO_ROOT" -name "CLAUDE.md" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/archive/*" 2>/dev/null || true)
RULES_FILES=$(find "$REPO_ROOT" -path "*/.claude/rules/*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/archive/*" 2>/dev/null || true)

for PAT in "${DEPRECATED_PATTERNS[@]}"; do
  # Search but exclude lines that contain "Deprecated", "deprecated", "Replacement", "Never Use"
  HITS=$(grep -ril "$PAT" $CLAUDE_FILES $RULES_FILES 2>/dev/null | sort -u || true)
  for HIT in $HITS; do
    # Check if the pattern appears outside of deprecation tables/notes
    ACTIVE_USES=$(grep -i "$PAT" "$HIT" | grep -iv "deprecat\|replacement\|never use\|removed\|replaced by\|renamed\|was byte-identical\|legacy" | head -5 || true)
    if [ -n "$ACTIVE_USES" ]; then
      echo "WARN: '$PAT' appears actively in $HIT"
      echo "  $ACTIVE_USES"
    fi
  done
done
echo "PASS: deprecated string scan complete"

# 4. Duplicate rules check: each rule family should have exactly 1 copy
RULE_FAMILIES=(
  "platform-architecture.md"
  "repo-topology.md"
  "security-baseline.md"
  "ssot-platform.md"
  "odoo-runtime.md"
  "odoo-security.md"
)
for FAMILY in "${RULE_FAMILIES[@]}"; do
  COPIES=$(find "$REPO_ROOT" -name "$FAMILY" -path "*/.claude/rules/*" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/archive/*" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$COPIES" -gt 1 ]; then
    echo "FAIL: $FAMILY has $COPIES copies (expected 1)"
    find "$REPO_ROOT" -name "$FAMILY" -path "*/.claude/rules/*" -not -path "*/archive/*" 2>/dev/null
    FAIL=1
  elif [ "$COPIES" -eq 1 ]; then
    echo "PASS: $FAMILY has 1 canonical copy"
  else
    echo "WARN: $FAMILY not found"
  fi
done

# 5. Python version consistency check
PY_REFS=$(grep -rh "Python.*3\.\(1[0-9]\|[0-9]\)" $CLAUDE_FILES 2>/dev/null | grep -v "Note:" | sort -u || true)
PY_VERSIONS=$(echo "$PY_REFS" | grep -oE "3\.[0-9]+" | sort -u || true)
PY_COUNT=$(echo "$PY_VERSIONS" | grep -c "." || true)
if [ "$PY_COUNT" -gt 1 ]; then
  echo "WARN: Multiple Python versions referenced: $PY_VERSIONS"
  echo "  (3.12+ = target, 3.11.x = current pyenv — clarify with a Note if both appear)"
else
  echo "PASS: Python version references consistent"
fi

echo ""
if [ "$FAIL" -ne 0 ]; then
  echo "RESULT: FAIL — $FAIL issue(s) found"
  exit 1
else
  echo "RESULT: PASS — all alignment checks passed"
  exit 0
fi
