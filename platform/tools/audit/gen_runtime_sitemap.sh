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

# Configuration with environment variable support
DEFAULT_COMPOSE="${COMPOSE_FILE:-deploy/docker-compose.prod.yml}"
DEFAULT_COMPOSE_OVERRIDE="${COMPOSE_OVERRIDE:-deploy/docker-compose.workos-deploy.yml}"
DEFAULT_DB_SERVICE="${DB_SERVICE:-db}"
DEFAULT_DB_NAME="${DB_NAME:-odoo}"
DEFAULT_DB_USER="${DB_USER:-odoo}"
DEFAULT_ODOO_SERVICE="${ODOO_SERVICE:-odoo}"

COMPOSE_FILE="${1:-$DEFAULT_COMPOSE}"
COMPOSE_OVERRIDE="${2:-$DEFAULT_COMPOSE_OVERRIDE}"
DB_SERVICE="${3:-$DEFAULT_DB_SERVICE}"
DB_NAME="${4:-$DEFAULT_DB_NAME}"
DB_USER="${5:-$DEFAULT_DB_USER}"
ODOO_SERVICE="${ODOO_SERVICE:-$DEFAULT_ODOO_SERVICE}"

mkdir -p "$OUTPUT_DIR"

cd "$REPO_ROOT"

# Detect if docker compose service is available, fallback to docker exec
DC=""
if [[ -f "$COMPOSE_FILE" ]]; then
    if [[ -f "$COMPOSE_OVERRIDE" ]]; then
        DC="docker compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE"
    else
        DC="docker compose -f $COMPOSE_FILE"
    fi

    # Verify service exists
    if ! $DC ps --services 2>/dev/null | grep -qx "$DB_SERVICE"; then
        echo "⚠️  Service '$DB_SERVICE' not found in compose, falling back to docker exec"
        DC=""
    fi
fi

echo "=== Generating Odoo Runtime Sitemap ==="
echo "Compose: $COMPOSE_FILE"
echo "DB Service: $DB_SERVICE"
echo "Database: $DB_NAME"
echo "Output: $OUTPUT_DIR"
echo "Mode: $([ -n "$DC" ] && echo "docker compose" || echo "docker exec (fallback)")"
echo ""

# Helper function for psql with docker exec fallback
run_psql() {
    local query="$1"
    if [[ -n "$DC" ]]; then
        $DC exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -tAc "$query" 2>/dev/null
    else
        docker exec -i "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -tAc "$query" 2>/dev/null
    fi
}

run_psql_formatted() {
    local query="$1"
    if [[ -n "$DC" ]]; then
        $DC exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -c "$query" 2>/dev/null
    else
        docker exec -i "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -c "$query" 2>/dev/null
    fi
}

# =============================================================================
# MODULE STATES
# =============================================================================
echo "Extracting MODULE_STATES.prod.csv..."

{
    echo "name,state,latest_version,shortdesc"
    run_psql "SELECT name || ',' || state || ',' || COALESCE(latest_version, 'null') || ',' || COALESCE(REPLACE(shortdesc::text, ',', ';'), '') FROM ir_module_module WHERE state IN ('installed', 'to install', 'to upgrade') ORDER BY name;"
} > "$OUTPUT_DIR/MODULE_STATES.prod.csv"

# Count
installed_count=$(run_psql "SELECT COUNT(*) FROM ir_module_module WHERE state = 'installed';" || echo "0")
echo "  ✓ MODULE_STATES.prod.csv ($installed_count installed modules)"

# =============================================================================
# MENU SITEMAP
# =============================================================================
echo "Extracting ODOO_MENU_SITEMAP.prod.json..."

# Extract menu sitemap using proper JSONB handling
run_psql "
SELECT json_build_object(
  'generated_at', to_char(now() at time zone 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"'),
  'database', '$DB_NAME',
  'menus', COALESCE(json_agg(json_build_object(
    'id', id,
    'name', COALESCE(name->>'en_US', (SELECT value FROM jsonb_each_text(name) LIMIT 1)),
    'parent_id', parent_id,
    'sequence', sequence,
    'action', action
  ) ORDER BY COALESCE(parent_id,0), sequence, id), '[]'::json),
  'workos_menus', (
    SELECT COALESCE(json_agg(json_build_object(
      'id', m.id,
      'name', COALESCE(m.name->>'en_US', (SELECT value FROM jsonb_each_text(m.name) LIMIT 1)),
      'parent_id', m.parent_id,
      'action', m.action
    ) ORDER BY m.id), '[]'::json)
    FROM ir_ui_menu m
    WHERE COALESCE(m.name->>'en_US', (SELECT value FROM jsonb_each_text(m.name) LIMIT 1), m.name::text) ILIKE '%workos%'
       OR COALESCE(m.name->>'en_US', (SELECT value FROM jsonb_each_text(m.name) LIMIT 1), m.name::text) ILIKE '%workspace%'
       OR COALESCE(m.name->>'en_US', (SELECT value FROM jsonb_each_text(m.name) LIMIT 1), m.name::text) ILIKE '%affine%'
  )
)
FROM ir_ui_menu;
" > "$OUTPUT_DIR/ODOO_MENU_SITEMAP.prod.json"

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
