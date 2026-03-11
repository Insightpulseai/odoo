#!/usr/bin/env bash
# ==============================================================================
# ODOO 18 TREE→LIST XML VIEW AUDIT SCRIPT
# ==============================================================================
# Scans module directories for deprecated <tree> view tags that should be
# replaced with <list> for Odoo 18+ compatibility.
#
# Usage:
#   ./scripts/ci/audit_tree_tags.sh [ADDONS_PATH]
#
# Default: addons/ipai
#
# Exit codes:
#   0 - No deprecated tags found
#   1 - Found deprecated tags (prints file:line for each)
# ==============================================================================

set -euo pipefail

ADDONS_PATH="${1:-addons/ipai}"

echo "============================================================"
echo "Odoo 18 <tree> → <list> XML View Audit"
echo "============================================================"
echo "Scanning: $ADDONS_PATH"
echo ""

# Find all XML files and grep for <tree> tags
# Exclude comments and strings that mention "tree" in other contexts
FOUND_FILES=$(grep -rln --include="*.xml" '<tree[[:space:]]' "$ADDONS_PATH" 2>/dev/null || true)

if [[ -z "$FOUND_FILES" ]]; then
    echo "✓ No deprecated <tree> view tags found"
    echo ""
    echo "All XML views are using the correct <list> tag for Odoo 18+."
    exit 0
fi

echo "⚠️  Found deprecated <tree> tags in the following files:"
echo "------------------------------------------------------------"

TOTAL_COUNT=0
for file in $FOUND_FILES; do
    # Get line numbers and context
    MATCHES=$(grep -n '<tree[[:space:]]' "$file" 2>/dev/null || true)
    if [[ -n "$MATCHES" ]]; then
        echo ""
        echo "📄 $file"
        echo "$MATCHES" | while IFS= read -r line; do
            echo "   $line"
            ((TOTAL_COUNT++)) || true
        done
    fi
done

echo ""
echo "------------------------------------------------------------"
echo "Total files with deprecated tags: $(echo "$FOUND_FILES" | wc -l | xargs)"
echo ""
echo "Migration steps:"
echo "  1. Replace <tree ...> with <list ...>"
echo "  2. Replace </tree> with </list>"
echo "  3. Update view IDs from *_tree to *_list (convention)"
echo "  4. Update view_mode='tree' to view_mode='list' in actions"
echo ""
echo "Quick sed fix (review changes before committing):"
echo "  sed -i 's/<tree /<list /g; s/<\/tree>/<\/list>/g' <file>"
echo ""

# Exit with error code if deprecated tags found
exit 1
