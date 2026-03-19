#!/usr/bin/env bash
# guardrail_no_bulk_doc_dump.sh
# =============================
# Fails if a PR introduces an excessive number of docs files in one change.
# Protects curated hubs from accidental bulk migration.
#
# Usage:
#   ./scripts/ci/guardrail_no_bulk_doc_dump.sh [threshold]
#
# Environment:
#   GITHUB_BASE_REF - Base branch for comparison (default: main)
#   GITHUB_SHA - Current commit SHA (default: HEAD)

set -euo pipefail

THRESHOLD="${1:-50}"
BASE="${GITHUB_BASE_REF:-main}"
HEAD="${GITHUB_SHA:-HEAD}"

echo "=== Curation Guardrail: Bulk Doc Dump Check ==="
echo "Base: origin/$BASE"
echo "Head: $HEAD"
echo "Threshold: $THRESHOLD new markdown files"
echo ""

# Fetch base branch if needed
git fetch origin "$BASE" --depth=1 >/dev/null 2>&1 || true

# Count added markdown files under docs/ or docs-site/
# Using git diff to find files with status 'A' (added)
added_files=$(git diff --name-status "origin/$BASE...$HEAD" 2>/dev/null | awk '$1=="A"{print $2}' || echo "")

if [ -z "$added_files" ]; then
    echo "No new files detected."
    added_md=0
else
    # Count markdown files
    added_md=$(echo "$added_files" | grep -cE '\.md$' || echo "0")
fi

echo "New markdown files in this change: $added_md"

# Hard threshold check
if [ "${added_md:-0}" -gt "$THRESHOLD" ]; then
    echo ""
    echo "ERROR: Detected ${added_md} new markdown files added in one change."
    echo "This exceeds the threshold of $THRESHOLD files."
    echo ""
    echo "This check prevents accidental bulk doc dumps/migrations."
    echo "If this is intentional curation:"
    echo "  1. Update docs/curation/CURATED_DOCS.yaml with rationale"
    echo "  2. Request explicit review from docs maintainer"
    echo "  3. Consider splitting into smaller PRs"
    echo ""
    echo "See docs/curation/CURATION_POLICY.md for guidelines."
    exit 1
fi

echo ""
echo "OK: No bulk doc dump detected (added_md=${added_md:-0}, threshold=$THRESHOLD)"
exit 0
