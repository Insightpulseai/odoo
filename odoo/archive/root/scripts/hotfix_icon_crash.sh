#!/usr/bin/env bash
set -euo pipefail

# HOTFIX: Fix Odoo crash due to 'fa-' branding in ir_module_module.icon
# Error: ValueError: Unsupported file: fa-layer-group

CONTAINER="${1:-odoo-erp-prod}"
DB="${2:-prod}"
USER="${3:-odoo}"

echo "🔧 Fixing Module Icons in DB: $DB (Container: $CONTAINER)"

# 1. Check count of bad icons
COUNT=$(docker exec -u "$USER" "$CONTAINER" psql -d "$DB" -t -c "SELECT count(*) FROM ir_module_module WHERE icon LIKE 'fa-%';")
COUNT=$(echo "$COUNT" | xargs)

if [ "$COUNT" == "0" ]; then
  echo "✅ No bad icons found. Database is clean."
else
  echo "⚠️  Found $COUNT module(s) with invalid 'fa-' icons."
  
  # 2. Update to default icon
  echo "🚀 Fixing..."
  docker exec -u "$USER" "$CONTAINER" psql -d "$DB" -c "UPDATE ir_module_module SET icon = '/base/static/description/icon.png' WHERE icon LIKE 'fa-%';"
  
  echo "✅ Fixed. Bad icons replaced with default."
fi

echo "🔄 Recommendation: Restart container to clear cache."
echo "   docker restart $CONTAINER"
