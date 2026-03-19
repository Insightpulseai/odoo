#!/bin/bash
# Install/update IPAI web branding + OCA server-brand debranding modules
# Run inside devcontainer: bash scripts/odoo/install_web_branding.sh
set -euo pipefail

DB="${1:-odoo_dev}"
MODULES="ipai_web_branding,mail_debranding,disable_odoo_online,remove_odoo_enterprise"

echo "=== Installing web branding modules on database: ${DB} ==="
echo "Modules: ${MODULES}"

/opt/odoo/odoo-bin \
  -d "${DB}" \
  -i "${MODULES}" \
  --stop-after-init \
  --no-http \
  --addons-path=/opt/odoo/addons,/workspaces/odoo/addons/ipai,/workspaces/odoo/addons/oca/server-brand

echo "=== Done. Restart Odoo to see changes. ==="
