#!/usr/bin/env bash
# ==============================================================================
# ODOO 18 SCSS/CSS ASSET COMPILATION DIAGNOSTIC & FIX SCRIPT
# ==============================================================================
# Diagnoses "Style compilation failed" errors and provides fixes.
#
# Usage:
#   ./scripts/odoo/diagnose_scss_error.sh [CONTAINER_NAME] [DB_NAME]
#
# Default: odoo-erp-prod, odoo
# ==============================================================================

set -euo pipefail

# === Configuration ===
CONTAINER_NAME="${1:-odoo-erp-prod}"
DB_NAME="${2:-odoo}"

echo "============================================================"
echo "ODOO 18 SCSS/CSS ASSET DIAGNOSTIC"
echo "============================================================"
echo "Container: $CONTAINER_NAME"
echo "Database:  $DB_NAME"
echo ""

# === Check if container exists ===
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ ERROR: Container '$CONTAINER_NAME' not found"
    echo "Available containers:"
    docker ps --format "  - {{.Names}}"
    exit 1
fi

# === 1. Pull SCSS/SASS Error Logs ===
echo ">>> [1/6] Scanning logs for SCSS/SASS errors..."
echo ""

SCSS_ERRORS=$(docker logs --tail 500 "$CONTAINER_NAME" 2>&1 | \
    grep -iE "style compilation|scss|sass|libsass|ParseError|Undefined variable|could not find|Invalid CSS" | \
    head -50 || true)

if [[ -z "$SCSS_ERRORS" ]]; then
    echo "✓ No SCSS/SASS errors found in recent logs"
else
    echo "⚠️  Found SCSS/SASS errors:"
    echo "------------------------------------------------------------"
    echo "$SCSS_ERRORS"
    echo "------------------------------------------------------------"
fi

echo ""

# === 2. Extract Specific Error Details ===
echo ">>> [2/6] Extracting error details..."
echo ""

# Look for undefined variables
UNDEFINED_VARS=$(echo "$SCSS_ERRORS" | grep -oP 'Undefined variable[:\s]*"\$[^"]*"' | sort -u || true)
if [[ -n "$UNDEFINED_VARS" ]]; then
    echo "⚠️  Undefined SCSS variables found:"
    echo "$UNDEFINED_VARS"
    echo ""
fi

# Look for import errors
IMPORT_ERRORS=$(echo "$SCSS_ERRORS" | grep -oP "File to import not found[^']*'[^']*'" | sort -u || true)
if [[ -n "$IMPORT_ERRORS" ]]; then
    echo "⚠️  Import errors found:"
    echo "$IMPORT_ERRORS"
    echo ""
fi

# Look for file paths
FILE_PATHS=$(echo "$SCSS_ERRORS" | grep -oP "addons/[^:]+\.scss:[0-9]+" | sort -u || true)
if [[ -n "$FILE_PATHS" ]]; then
    echo "⚠️  Error locations:"
    echo "$FILE_PATHS"
    echo ""
fi

# === 3. Check Asset Attachments ===
echo ">>> [3/6] Checking compiled asset attachments..."
echo ""

ASSET_COUNT=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
    "SELECT COUNT(*) FROM ir_attachment WHERE name ILIKE '%assets_%' OR name ILIKE 'web.assets_%';" 2>/dev/null || echo "0")
ASSET_COUNT=$(echo "$ASSET_COUNT" | xargs)

echo "Found $ASSET_COUNT compiled asset attachment(s)"
echo ""

# === 4. List Recently Modified Assets ===
echo ">>> [4/6] Recent asset modifications..."
echo ""

docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -c \
    "SELECT id, name, write_date
     FROM ir_attachment
     WHERE (name ILIKE '%assets_%' OR name ILIKE 'web.assets_%')
     ORDER BY write_date DESC
     LIMIT 10;" 2>/dev/null || echo "Could not query assets"

echo ""

# === 5. Check for Enterprise-only References ===
echo ">>> [5/6] Checking for Enterprise-only references in CE..."
echo ""

ENT_REFS=$(docker exec -i "$CONTAINER_NAME" bash -c \
    "grep -r 'web_enterprise\|@odoo-enterprise' /mnt/extra-addons/ipai/ 2>/dev/null" || true)

if [[ -n "$ENT_REFS" ]]; then
    echo "⚠️  Found Enterprise references in IPAI modules:"
    echo "$ENT_REFS"
else
    echo "✓ No Enterprise references found in IPAI modules"
fi

echo ""

# === 6. Provide Fix Commands ===
echo ">>> [6/6] Suggested Fix Commands"
echo "============================================================"
echo ""
echo "Option A: Purge ALL compiled assets and restart (safest)"
echo "------------------------------------------------------------"
cat << 'PURGE_CMD'
docker exec -it CONTAINER psql -U odoo -d DB -c "
DELETE FROM ir_attachment
WHERE name ILIKE '%assets_%'
   OR name ILIKE 'web.assets_%'
   OR mimetype IN ('text/css', 'application/javascript');"
docker restart CONTAINER
PURGE_CMD
echo ""

echo "Option B: Purge assets via Odoo shell (preserves other attachments)"
echo "------------------------------------------------------------"
cat << 'SHELL_CMD'
docker exec -it CONTAINER bash -lc "odoo shell -d DB <<'PY'
from odoo import api, SUPERUSER_ID
env = api.Environment(cr, SUPERUSER_ID, {})
dom = ['|',('name','ilike','web.assets_'),('name','ilike','%assets_%')]
atts = env['ir.attachment'].search(dom)
print('Deleting asset attachments:', len(atts))
atts.unlink()
env.cr.commit()
PY"
docker restart CONTAINER
SHELL_CMD
echo ""

echo "Option C: Force rebuild specific module assets"
echo "------------------------------------------------------------"
cat << 'REBUILD_CMD'
# Replace <module_name> with the module from the error trace
docker exec -it CONTAINER bash -lc "odoo -d DB -u <module_name> --stop-after-init"
docker restart CONTAINER
REBUILD_CMD
echo ""

echo "Option D: Rebuild all web assets"
echo "------------------------------------------------------------"
cat << 'WEB_REBUILD'
docker exec -it CONTAINER bash -lc "odoo -d DB -u web --stop-after-init"
docker restart CONTAINER
WEB_REBUILD
echo ""

echo "============================================================"
echo "After running fix, verify with:"
echo "  docker logs --tail 100 $CONTAINER_NAME 2>&1 | grep -iE 'scss|sass|style'"
echo "  # Should return empty or no errors"
echo ""
echo "Browser verification:"
echo "  1. Hard refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)"
echo "  2. Check DevTools Network tab - CSS should load with 200 status"
echo "============================================================"
