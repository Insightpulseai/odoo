#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Configure Mailgun SMTP in Odoo (Non-Interactive)
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

# Mailgun configuration from .env
MAILGUN_SMTP_HOST="${SMTP_HOST:-smtp.mailgun.org}"
MAILGUN_SMTP_PORT="${SMTP_PORT:-587}"
MAILGUN_SMTP_LOGIN="${MAILGUN_SMTP_LOGIN:-}"
MAILGUN_SMTP_PASSWORD="${SMTP_PASSWORD:-}"
MAILGUN_WEBHOOK_SIGNING_KEY="${MAILGUN_WEBHOOK_SIGNING_KEY:-}"
ODOO_DEFAULT_FROM_EMAIL="${ODOO_DEFAULT_FROM_EMAIL:-admin@insightpulseai.net}"
ODOO_CATCHALL_DOMAIN="${ODOO_CATCHALL_DOMAIN:-insightpulseai.net}"

echo "════════════════════════════════════════════════════════════════"
echo "Configure Mailgun SMTP in Odoo"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  Database: $DB_NAME"
echo "  SMTP Host: $MAILGUN_SMTP_HOST:$MAILGUN_SMTP_PORT"
echo "  SMTP Login: ${MAILGUN_SMTP_LOGIN:-<not set>}"
echo "  Default From: $ODOO_DEFAULT_FROM_EMAIL"
echo "  Catchall Domain: $ODOO_CATCHALL_DOMAIN"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    echo "   Run: ./scripts/dev/up.sh"
    exit 1
fi

echo "🔧 Configuring SMTP via Odoo shell..."

docker exec -i "$CONTAINER_NAME" odoo \
    -c "$ODOO_CONF" \
    -d "$DB_NAME" \
    --shell <<EOF
# Set system parameters
params = env['ir.config_parameter'].sudo()
params.set_param('ipai_mailgun.default_from', '${ODOO_DEFAULT_FROM_EMAIL}')
params.set_param('mail.catchall.domain', '${ODOO_CATCHALL_DOMAIN}')

# Set webhook signing key (if provided)
if '${MAILGUN_WEBHOOK_SIGNING_KEY}':
    params.set_param('ipai_mailgun.webhook_signing_key', '${MAILGUN_WEBHOOK_SIGNING_KEY}')
    print("✅ Webhook signing key configured")

# Configure SMTP server
smtp = env['ir.mail_server'].sudo().search([('name', '=', 'Mailgun SMTP')], limit=1)
vals = {
    'name': 'Mailgun SMTP',
    'smtp_host': '${MAILGUN_SMTP_HOST}',
    'smtp_port': ${MAILGUN_SMTP_PORT},
    'smtp_encryption': 'starttls',
    'smtp_user': '${MAILGUN_SMTP_LOGIN}',
    'smtp_pass': '${MAILGUN_SMTP_PASSWORD}',
    'active': True,
}

if smtp:
    smtp.write(vals)
    print("✅ SMTP server updated")
else:
    env['ir.mail_server'].sudo().create(vals)
    print("✅ SMTP server created")

print("✅ Mailgun SMTP configuration complete")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Configuration complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Test outbound email: ./scripts/mailgun/test-outbound-email.sh"
echo "  2. Configure Mailgun routes (production only)"
echo ""
