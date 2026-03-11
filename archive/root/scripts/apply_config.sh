#!/bin/bash
# One-command configuration - NO PROMPTS
# Reads from ~/.zshrc, applies to Odoo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

DB="${1:-odoo_dev}"

echo "🔧 Configuring Odoo database: $DB"

# Source environment from existing credentials
source scripts/setup_config_env.sh

# Apply configuration
echo "📝 Applying configuration..."
./odoo-bin shell -d "$DB" --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_config_mail_ai_ocr.py

# Verify
echo ""
echo "✅ Verification:"
./odoo-bin shell -d "$DB" --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_check_mail.py

echo ""
echo "✅ Configuration complete for database: $DB"
