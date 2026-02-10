#!/bin/bash
# Fix permissions for Odoo addons directory
# Usage: ./scripts/fix_permissions.sh
set -e

echo "Fixing permissions for addons directory..."
sudo chown -R $(whoami) addons
sudo chmod -R u+w addons
sudo xattr -dr com.apple.quarantine addons 2>/dev/null || true
mkdir -p addons/oca

echo "✓ Done. You can now run ./scripts/install_oca_parity.sh"
