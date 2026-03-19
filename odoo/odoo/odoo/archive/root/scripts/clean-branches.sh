#!/bin/bash
# Clean all remote branches except main
# Usage: ./scripts/clean-branches.sh [--dry-run]

set -euo pipefail

DRY_RUN="${1:-}"

echo "=== Branch Cleanup Script ==="
echo "Repository: jgtolentino/odoo-ce"
echo ""

# Fetch latest remote state
git fetch origin --prune

# Get all remote branches except main
BRANCHES=$(git branch -r | grep -v 'origin/main' | grep -v 'HEAD' | sed 's|origin/||' | sort)
BRANCH_COUNT=$(echo "$BRANCHES" | wc -l)

echo "Found $BRANCH_COUNT branches to delete (excluding main):"
echo ""
echo "$BRANCHES" | head -20
if [ "$BRANCH_COUNT" -gt 20 ]; then
    echo "... and $((BRANCH_COUNT - 20)) more"
fi
echo ""

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "[DRY RUN] Would delete the following branches:"
    echo "$BRANCHES"
    exit 0
fi

echo "Deleting branches..."
echo ""

DELETED=0
FAILED=0

for branch in $BRANCHES; do
    echo -n "Deleting $branch... "
    if git push origin --delete "$branch" 2>/dev/null; then
        echo "OK"
        ((DELETED++))
    else
        echo "FAILED"
        ((FAILED++))
    fi
done

echo ""
echo "=== Summary ==="
echo "Deleted: $DELETED"
echo "Failed: $FAILED"
echo "Remaining: main"
