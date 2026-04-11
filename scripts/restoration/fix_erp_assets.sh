#!/bin/bash
# =============================================================================
# scripts/restoration/fix_erp_assets.sh
# Odoo 18 Asset Bundling Repair (Direct Origin Alignment)
# =============================================================================
set -euo pipefail

# Identification
export RG_RUNTIME="rg-ipai-dev-odoo-runtime"
export APP="ipai-odoo-dev-web"
export BASE_URL="https://erp.insightpulseai.com"
AZ_PATH=$(which az || echo "/opt/homebrew/bin/az")

echo "=== Fixing ERP Asset Bundling for $BASE_URL ==="

# 1. Define SQL Payload
# - Correct base.url
# - Freeze base.url to prevent auto-revert to internal IP
# - Clear asset attachments to force regeneration
SQL_QUERY="
UPDATE ir_config_parameter SET value = '${BASE_URL}' WHERE key = 'web.base.url';
INSERT INTO ir_config_parameter (key, value) VALUES ('web.base.url.freeze', 'True') ON CONFLICT (key) DO UPDATE SET value = 'True';
DELETE FROM ir_attachment WHERE name LIKE 'web.assets_%';
"

echo "Applying SQL Repair to $PG_SERVER..."

# 2. Execute SQL via Azure CLI
# Note: This requires a valid 'az login' session and Postgres credentials.
# If interactive password prompt is an issue, please run the SQL manually.
$AZ_PATH postgres flexible-server execute \
  --resource-group "$RG_DATA" \
  --name "$PG_SERVER" \
  --database-name "$DB_NAME" \
  --querytext "$SQL_QUERY"

echo "=== Asset Repair Applied ==="
echo "NEXT STEP: Clear your browser cache or use Incognito to verify: $BASE_URL"
