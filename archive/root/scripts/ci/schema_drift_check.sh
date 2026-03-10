#!/bin/bash
# =============================================================================
# Schema Drift Check
# Verifies that schema artifacts are up to date with the database
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Schema Drift Check ==="

# Check if schema files exist
if [[ ! -f "$ROOT_DIR/docs/data_model/schema.json" ]]; then
    echo "WARN: schema.json not found - skipping drift check"
    echo "Run: python3 tools/odoo_schema/export_schema.py"
    exit 0
fi

# Store current hashes
SCHEMA_HASH=$(md5sum "$ROOT_DIR/docs/data_model/schema.json" | cut -d' ' -f1)
ERD_HASH=$(md5sum "$ROOT_DIR/docs/data_model/erd.mmd" 2>/dev/null | cut -d' ' -f1 || echo "none")
DRAWIO_HASH=$(md5sum "$ROOT_DIR/docs/data_model/erd.drawio" 2>/dev/null | cut -d' ' -f1 || echo "none")

# Re-generate (requires DB connection)
if [[ -n "${PGHOST:-}" ]] || [[ -n "${DB_HOST:-}" ]]; then
    echo "Regenerating schema from database..."
    cd "$ROOT_DIR"
    python3 tools/odoo_schema/export_schema.py
    python3 tools/odoo_schema/schema_to_drawio.py
    python3 tools/odoo_schema/schema_to_pydantic.py

    # Compare hashes
    NEW_SCHEMA_HASH=$(md5sum "$ROOT_DIR/docs/data_model/schema.json" | cut -d' ' -f1)
    NEW_ERD_HASH=$(md5sum "$ROOT_DIR/docs/data_model/erd.mmd" | cut -d' ' -f1)
    NEW_DRAWIO_HASH=$(md5sum "$ROOT_DIR/docs/data_model/erd.drawio" | cut -d' ' -f1)

    if [[ "$SCHEMA_HASH" != "$NEW_SCHEMA_HASH" ]]; then
        echo "ERROR: schema.json has drifted!"
        echo "  Old hash: $SCHEMA_HASH"
        echo "  New hash: $NEW_SCHEMA_HASH"
        echo ""
        echo "Commit the updated schema files:"
        echo "  git add docs/data_model/"
        echo "  git commit -m 'docs: update schema artifacts'"
        exit 1
    fi

    if [[ "$ERD_HASH" != "$NEW_ERD_HASH" ]]; then
        echo "ERROR: erd.mmd has drifted!"
        exit 1
    fi

    if [[ "$DRAWIO_HASH" != "$NEW_DRAWIO_HASH" ]]; then
        echo "ERROR: erd.drawio has drifted!"
        exit 1
    fi

    echo "OK: All schema artifacts are up to date"
else
    echo "SKIP: No database connection (set PGHOST or DB_HOST)"
    echo "Running git diff check instead..."

    # Check if schema files are tracked and uncommitted
    cd "$ROOT_DIR"
    if git diff --quiet docs/data_model/ 2>/dev/null; then
        echo "OK: No uncommitted changes to schema files"
    else
        echo "WARN: Uncommitted changes to schema files detected"
        git diff --stat docs/data_model/
    fi
fi

echo "=== Schema Drift Check Complete ==="
