#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Install ipai_mailgun_bridge Addon
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo "❌ Error: .env file not found at $PROJECT_ROOT/.env"
    exit 1
fi

# Configuration
CONTAINER_NAME="${ODOO_CONTAINER_NAME:-odoo-dev}"
DB_NAME="${ODOO_DB_NAME:-odoo_dev}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"

echo "════════════════════════════════════════════════════════════════"
echo "Install ipai_mailgun_bridge Addon"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  Database: $DB_NAME"
echo "  Addon: ipai_mailgun_bridge"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    echo "   Run: ./scripts/dev/up.sh"
    exit 1
fi

# Check if addon directory exists
if [ ! -d "$PROJECT_ROOT/addons/ipai_mailgun_bridge" ]; then
    echo "❌ Error: Addon directory not found at $PROJECT_ROOT/addons/ipai_mailgun_bridge"
    exit 1
fi

echo "🔧 Installing addon..."

# Install addon with --stop-after-init
docker exec "$CONTAINER_NAME" odoo \
    -c "$ODOO_CONF" \
    -d "$DB_NAME" \
    -i ipai_mailgun_bridge \
    --stop-after-init

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Installation complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Verification:"
echo "  Run: ./scripts/mailgun/verify-parity.sh"
echo ""
echo "Next steps:"
echo "  1. Configure SMTP: ./scripts/dev/configure-mailgun-smtp.sh"
echo "  2. Test outbound: ./scripts/mailgun/test-outbound-email.sh"
echo "  3. Configure Mailgun routes (production): ./scripts/mailgun/configure-routes.sh"
echo ""
