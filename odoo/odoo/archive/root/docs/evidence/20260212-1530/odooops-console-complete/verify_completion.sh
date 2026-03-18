#!/bin/bash
# OdooOps Console Completion Verification Script

set -e

echo "===== OdooOps Console Completion Verification ====="
echo ""

# Base directory
BASE_DIR="/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/odooops-console"

# Count pages
echo "📄 Counting pages..."
PAGE_COUNT=$(find "$BASE_DIR/src/app/app" -name "page.tsx" 2>/dev/null | wc -l | tr -d ' ')
echo "   Found $PAGE_COUNT pages (expected: 16)"

# Count layouts
echo "📐 Counting layouts..."
LAYOUT_COUNT=$(find "$BASE_DIR/src/app/app" -name "layout.tsx" 2>/dev/null | wc -l | tr -d ' ')
echo "   Found $LAYOUT_COUNT layouts (expected: 2)"

# Count components
echo "🧩 Counting components..."
COMPONENT_COUNT=$(find "$BASE_DIR/src/components/odoo-sh" -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')
echo "   Found $COMPONENT_COUNT components (expected: 2)"

# Count wireframe docs
echo "📋 Counting wireframe docs..."
WIREFRAME_COUNT=$(find "/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/docs/wireframes" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "   Found $WIREFRAME_COUNT wireframe docs (expected: 1)"

echo ""
echo "===== Detailed File List ====="
echo ""

echo "Project Pages:"
find "$BASE_DIR/src/app/app/projects" -name "*.tsx" 2>/dev/null | sort | while read file; do
    echo "  ✅ $(echo "$file" | sed "s|$BASE_DIR/||")"
done

echo ""
echo "Close Pages:"
find "$BASE_DIR/src/app/app/close" -name "*.tsx" 2>/dev/null | sort | while read file; do
    echo "  ✅ $(echo "$file" | sed "s|$BASE_DIR/||")"
done

echo ""
echo "Components:"
find "$BASE_DIR/src/components/odoo-sh" -name "*.tsx" 2>/dev/null | sort | while read file; do
    echo "  ✅ $(echo "$file" | sed "s|$BASE_DIR/||")"
done

echo ""
echo "===== Summary ====="
TOTAL_FILES=$((PAGE_COUNT + LAYOUT_COUNT + COMPONENT_COUNT + WIREFRAME_COUNT))
echo "Total files: $TOTAL_FILES / 21"
echo ""

if [ "$TOTAL_FILES" -eq 21 ]; then
    echo "✅ SUCCESS: All 21 files present (100% complete)"
    exit 0
else
    echo "⚠️ WARNING: Expected 21 files, found $TOTAL_FILES"
    exit 1
fi
