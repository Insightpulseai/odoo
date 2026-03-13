#!/bin/bash
# TBWA Backend Theme - Quick Install Script
# Usage: ./install.sh [database_name] [container_name]

DB_NAME="${1:-odoo_core}"
CONTAINER="${2:-odoo-web}"
ADDONS_PATH="${3:-/opt/odoo/addons}"

set -e

echo "=== TBWA Backend Theme Installer ==="
echo "Database: $DB_NAME"
echo "Container: $CONTAINER"
echo "Addons path: $ADDONS_PATH"
echo ""

# Check if running in Docker context
if docker ps | grep -q "$CONTAINER"; then
    echo "[1/4] Container '$CONTAINER' found"
else
    echo "ERROR: Container '$CONTAINER' not found"
    echo "Usage: ./install.sh [database_name] [container_name]"
    exit 1
fi

# Copy module (assumes script is run from module parent directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_DIR="$SCRIPT_DIR"

if [ -f "$MODULE_DIR/__manifest__.py" ]; then
    echo "[2/4] Module found at $MODULE_DIR"
else
    echo "ERROR: __manifest__.py not found. Run from module directory."
    exit 1
fi

# Update module list
echo "[3/4] Updating module list..."
docker exec -i "$CONTAINER" odoo shell -d "$DB_NAME" << 'EOF'
env['ir.module.module'].update_list()
env.cr.commit()
print("Module list updated")
EOF

# Install module
echo "[4/4] Installing ipai_theme_tbwa_backend..."
docker exec -it "$CONTAINER" odoo \
    -d "$DB_NAME" \
    -i ipai_theme_tbwa_backend \
    --stop-after-init

echo ""
echo "=== Installation Complete ==="
echo "Restart container: docker restart $CONTAINER"
echo "Then hard-refresh browser: Ctrl+Shift+R"
