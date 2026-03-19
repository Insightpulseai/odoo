#!/usr/bin/env bash
# Example: Addons path configurations for different environments
set -euo pipefail

echo "=== Local dev addons path ==="
echo "vendor/odoo/addons,addons/ipai"

echo "=== Devcontainer addons path ==="
echo "/opt/odoo/addons,/workspaces/odoo/addons/ipai,/workspaces/odoo/addons/oca"

echo "=== List available addons ==="
# Local dev
ls -d vendor/odoo/addons/*/  2>/dev/null | wc -l | xargs echo "Core addons:"
ls -d addons/ipai/*/         2>/dev/null | wc -l | xargs echo "IPAI addons:"
ls -d addons/oca/*/          2>/dev/null | wc -l | xargs echo "OCA addons:"
