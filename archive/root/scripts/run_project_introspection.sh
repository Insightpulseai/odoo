#!/bin/bash
# =============================================================================
# Odoo 18 CE Project Introspection Runner
# READ-ONLY - No destructive operations
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
DB_NAME="${DB_NAME:-odoo_core}"

echo "=============================================="
echo "Odoo 18 CE Project Introspection"
echo "=============================================="
echo "Container: $ODOO_CONTAINER"
echo "Database:  $DB_NAME"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"; then
    echo "ERROR: Container '$ODOO_CONTAINER' is not running."
    echo ""
    echo "Start the stack with:"
    echo "  docker compose up -d"
    echo ""
    echo "Or specify a different container:"
    echo "  ODOO_CONTAINER=odoo-marketing DB_NAME=odoo_marketing $0"
    exit 1
fi

echo "Running introspection (this may take a moment)..."
echo ""

# Copy introspection script to container
docker cp "$SCRIPT_DIR/introspect_project.py" "${ODOO_CONTAINER}:/tmp/introspect_project.py"

# Run the introspection script inside Odoo shell
docker exec -i "$ODOO_CONTAINER" odoo shell -d "$DB_NAME" --no-http < "$SCRIPT_DIR/introspect_project.py"

# Copy artifacts back to host
echo ""
echo "=============================================="
echo "Copying artifacts from container..."
echo "=============================================="

mkdir -p "$PROJECT_ROOT/tmp/introspection"

docker cp "${ODOO_CONTAINER}:/tmp/odoo_project_full.dbml" "$PROJECT_ROOT/tmp/introspection/" 2>/dev/null && \
    echo "  -> tmp/introspection/odoo_project_full.dbml" || \
    echo "  [WARN] odoo_project_full.dbml not found"

docker cp "${ODOO_CONTAINER}:/tmp/odoo_project_full.schema.json" "$PROJECT_ROOT/tmp/introspection/" 2>/dev/null && \
    echo "  -> tmp/introspection/odoo_project_full.schema.json" || \
    echo "  [WARN] odoo_project_full.schema.json not found"

docker cp "${ODOO_CONTAINER}:/tmp/odoo_import_headers.txt" "$PROJECT_ROOT/tmp/introspection/" 2>/dev/null && \
    echo "  -> tmp/introspection/odoo_import_headers.txt" || \
    echo "  [WARN] odoo_import_headers.txt not found"

echo ""
echo "=============================================="
echo "INTROSPECTION COMPLETE"
echo "=============================================="
echo ""
echo "Artifacts saved to: $PROJECT_ROOT/tmp/introspection/"
echo ""
echo "Next steps:"
echo "  1. Review odoo_import_headers.txt for CSV column order"
echo "  2. Use odoo_project_full.dbml in dbdiagram.io for visualization"
echo "  3. Parse odoo_project_full.schema.json for programmatic access"
