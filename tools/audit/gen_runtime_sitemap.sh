#!/usr/bin/env bash
# =============================================================================
# GENERATE ODOO RUNTIME SITEMAP FROM DATABASE
# =============================================================================
# Extracts menus, actions, modules, and models from Odoo database.
#
# Usage:
#   ./tools/audit/gen_runtime_sitemap.sh [compose_file] [db_service] [db_name] [db_user]
#
# Defaults:
#   compose_file: deploy/docker-compose.prod.yml
#   db_service: db
#   db_name: odoo
#   db_user: odoo
#
# Outputs:
#   docs/runtime/ODOO_MENU_SITEMAP.prod.json
#   docs/runtime/ODOO_MODEL_SNAPSHOT.prod.json
#   docs/runtime/MODULE_STATES.prod.csv
#   docs/runtime/ADDONS_PATH.prod.txt
#   docs/runtime/CONTAINER_PATH_CHECK.prod.txt
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/docs/runtime"

# Configuration
COMPOSE_FILE="${1:-deploy/docker-compose.prod.yml}"
COMPOSE_OVERRIDE="${COMPOSE_OVERRIDE:-deploy/docker-compose.workos-deploy.yml}"
DB_SERVICE="${2:-db}"
DB_NAME="${3:-odoo}"
DB_USER="${4:-odoo}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"

mkdir -p "$OUTPUT_DIR"

cd "$REPO_ROOT"

echo "=== Generating Odoo Runtime Sitemap ==="
echo "Compose: $COMPOSE_FILE"
echo "DB Service: $DB_SERVICE"
echo "Database: $DB_NAME"
echo "Output: $OUTPUT_DIR"
echo ""

# Helper function for psql
run_psql() {
    local query="$1"
    if [[ -f "$COMPOSE_OVERRIDE" ]]; then
        docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" exec -T "$DB_SERVICE" \
            psql -U "$DB_USER" -d "$DB_NAME" -tAc "$query" 2>/dev/null
    else
        docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
            psql -U "$DB_USER" -d "$DB_NAME" -tAc "$query" 2>/dev/null
    fi
}

run_psql_formatted() {
    local query="$1"
    if [[ -f "$COMPOSE_OVERRIDE" ]]; then
        docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" exec -T "$DB_SERVICE" \
            psql -U "$DB_USER" -d "$DB_NAME" -c "$query" 2>/dev/null
    else
        docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
            psql -U "$DB_USER" -d "$DB_NAME" -c "$query" 2>/dev/null
    fi
}

# =============================================================================
# MODULE STATES
# =============================================================================
echo "Extracting MODULE_STATES.prod.csv..."

{
    echo "name,state,latest_version,shortdesc"
    run_psql "SELECT name || ',' || state || ',' || COALESCE(latest_version, 'null') || ',' || COALESCE(REPLACE(shortdesc, ',', ';'), '') FROM ir_module_module WHERE state IN ('installed', 'to install', 'to upgrade') ORDER BY name;"
} > "$OUTPUT_DIR/MODULE_STATES.prod.csv"

# Count
installed_count=$(run_psql "SELECT COUNT(*) FROM ir_module_module WHERE state = 'installed';" || echo "0")
echo "  ✓ MODULE_STATES.prod.csv ($installed_count installed modules)"

# =============================================================================
# MENU SITEMAP
# =============================================================================
echo "Extracting ODOO_MENU_SITEMAP.prod.json..."

# Get menus as JSON
cat > "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json" << EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "database": "$DB_NAME",
  "menus": [
EOF

# Extract menus
run_psql "SELECT json_build_object('id', id, 'name', name, 'parent_id', parent_id, 'sequence', sequence, 'action', action) FROM ir_ui_menu ORDER BY parent_id NULLS FIRST, sequence;" | \
    sed 's/$/,/' | sed '$ s/,$//' >> "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json" 2>/dev/null || echo "    {\"error\": \"could not extract menus\"}" >> "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json"

cat >> "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json" << EOF
  ],
  "workos_menus": [
EOF

# Extract WorkOS-specific menus
run_psql "SELECT json_build_object('id', id, 'name', name, 'parent_id', parent_id, 'action', action) FROM ir_ui_menu WHERE name ILIKE '%workos%' OR name ILIKE '%workspace%' OR name ILIKE '%affine%' ORDER BY id;" | \
    sed 's/$/,/' | sed '$ s/,$//' >> "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json" 2>/dev/null || echo "    {\"note\": \"no workos menus found\"}" >> "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json"

cat >> "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json" << EOF
  ]
}
EOF

menu_count=$(run_psql "SELECT COUNT(*) FROM ir_ui_menu;" || echo "0")
echo "  ✓ ODOO_MENU_SITEMAP.prod.json ($menu_count menus)"

# =============================================================================
# MODEL SNAPSHOT
# =============================================================================
echo "Extracting ODOO_MODEL_SNAPSHOT.prod.json..."

cat > "$OUTPUT_DIR/ODOO_MODEL_SNAPSHOT.prod.json" << EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "database": "$DB_NAME",
  "ipai_models": [
EOF

# Extract IPAI models
run_psql "SELECT json_build_object('model', model, 'name', name, 'state', state) FROM ir_model WHERE model LIKE 'ipai.%' ORDER BY model;" | \
    sed 's/$/,/' | sed '$ s/,$//' >> "$OUTPUT_DIR/ODOO_MODEL_SNAPSHOT.prod.json" 2>/dev/null || echo "    {\"note\": \"no ipai models found\"}" >> "$OUTPUT_DIR/ODOO_MODEL_SNAPSHOT.prod.json"

cat >> "$OUTPUT_DIR/ODOO_MODEL_SNAPSHOT.prod.json" << EOF
  ],
  "workos_models": [
EOF

# Extract WorkOS models specifically
run_psql "SELECT json_build_object('model', model, 'name', name) FROM ir_model WHERE model LIKE 'ipai.workos.%' ORDER BY model;" | \
    sed 's/$/,/' | sed '$ s/,$//' >> "$OUTPUT_DIR/ODOO_MODEL_SNAPSHOT.prod.json" 2>/dev/null || echo "    {\"note\": \"no workos models found\"}" >> "$OUTPUT_DIR/ODOO_MODEL_SNAPSHOT.prod.json"

cat >> "$OUTPUT_DIR/ODOO_MODEL_SNAPSHOT.prod.json" << EOF
  ],
  "model_counts": {
    "total": $(run_psql "SELECT COUNT(*) FROM ir_model;" || echo "0"),
    "ipai": $(run_psql "SELECT COUNT(*) FROM ir_model WHERE model LIKE 'ipai.%';" || echo "0"),
    "workos": $(run_psql "SELECT COUNT(*) FROM ir_model WHERE model LIKE 'ipai.workos.%';" || echo "0")
  }
}
EOF

echo "  ✓ ODOO_MODEL_SNAPSHOT.prod.json"

# =============================================================================
# ACTIONS SNAPSHOT
# =============================================================================
echo "Extracting actions..."

cat > "$OUTPUT_DIR/ODOO_ACTIONS.prod.json" << EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "window_actions": [
EOF

run_psql "SELECT json_build_object('id', id, 'name', name, 'res_model', res_model, 'view_mode', view_mode) FROM ir_act_window WHERE res_model LIKE 'ipai.%' ORDER BY id LIMIT 100;" | \
    sed 's/$/,/' | sed '$ s/,$//' >> "$OUTPUT_DIR/ODOO_ACTIONS.prod.json" 2>/dev/null || echo "    {\"note\": \"no ipai actions\"}" >> "$OUTPUT_DIR/ODOO_ACTIONS.prod.json"

cat >> "$OUTPUT_DIR/ODOO_ACTIONS.prod.json" << EOF
  ]
}
EOF

echo "  ✓ ODOO_ACTIONS.prod.json"

# =============================================================================
# ADDONS PATH
# =============================================================================
echo "Extracting ADDONS_PATH.prod.txt..."

{
    echo "# Addons Path Configuration"
    echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""

    # From odoo.conf if accessible
    echo "## From deploy/odoo.conf:"
    grep -E "^addons_path" "$REPO_ROOT/deploy/odoo.conf" 2>/dev/null || echo "# (not found in deploy/odoo.conf)"
    echo ""

    # From container
    echo "## From Odoo container (if running):"
    if [[ -f "$COMPOSE_OVERRIDE" ]]; then
        docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" exec -T "$ODOO_SERVICE" \
            python3 -c "import odoo.tools.config as c; print('addons_path:', c.config.get('addons_path', 'N/A'))" 2>/dev/null || echo "# (container not accessible)"
    else
        docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
            python3 -c "import odoo.tools.config as c; print('addons_path:', c.config.get('addons_path', 'N/A'))" 2>/dev/null || echo "# (container not accessible)"
    fi
} > "$OUTPUT_DIR/ADDONS_PATH.prod.txt"

echo "  ✓ ADDONS_PATH.prod.txt"

# =============================================================================
# CONTAINER PATH CHECK
# =============================================================================
echo "Checking container paths..."

{
    echo "# Container Path Verification"
    echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""

    echo "## Odoo installation path:"
    if [[ -f "$COMPOSE_OVERRIDE" ]]; then
        docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" exec -T "$ODOO_SERVICE" \
            python3 -c "import odoo; print(odoo.__file__)" 2>/dev/null || echo "# (not accessible)"
    else
        docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
            python3 -c "import odoo; print(odoo.__file__)" 2>/dev/null || echo "# (not accessible)"
    fi
    echo ""

    echo "## /mnt/addons/ipai contents:"
    if [[ -f "$COMPOSE_OVERRIDE" ]]; then
        docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" exec -T "$ODOO_SERVICE" \
            ls -la /mnt/addons/ipai/ 2>/dev/null | head -30 || echo "# (path not accessible)"
    else
        docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
            ls -la /mnt/addons/ipai/ 2>/dev/null | head -30 || echo "# (path not accessible or not mounted)"
    fi
    echo ""

    echo "## IPAI WorkOS modules visible:"
    if [[ -f "$COMPOSE_OVERRIDE" ]]; then
        docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" exec -T "$ODOO_SERVICE" \
            ls -d /mnt/addons/ipai/ipai_workos_* 2>/dev/null || echo "# (not found)"
    else
        docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
            ls -d /mnt/addons/ipai/ipai_workos_* 2>/dev/null || echo "# (not mounted or not found)"
    fi
} > "$OUTPUT_DIR/CONTAINER_PATH_CHECK.prod.txt"

echo "  ✓ CONTAINER_PATH_CHECK.prod.txt"

# =============================================================================
# IPAI MODULE STATUS (detailed)
# =============================================================================
echo "Extracting IPAI module status..."

{
    echo "# IPAI Module Status"
    echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""
    run_psql_formatted "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name;"
} > "$OUTPUT_DIR/IPAI_MODULE_STATUS.prod.txt"

echo "  ✓ IPAI_MODULE_STATUS.prod.txt"

echo ""
echo "=== Runtime Sitemap Complete ==="
echo "Artifacts in: $OUTPUT_DIR"
