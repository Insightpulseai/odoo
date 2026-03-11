#!/bin/bash
# =============================================================================
# Post-Import Verification Runner
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
DB_NAME="${DB_NAME:-odoo_core}"

echo "Running post-import verification..."
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"; then
    echo "ERROR: Container '$ODOO_CONTAINER' is not running."
    exit 1
fi

# Copy and run verification script
docker cp "$SCRIPT_DIR/verify_import.py" "${ODOO_CONTAINER}:/tmp/"
docker exec -i "$ODOO_CONTAINER" odoo shell -d "$DB_NAME" --no-http < "$SCRIPT_DIR/verify_import.py"
