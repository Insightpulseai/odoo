#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Test Outbound Email via Mailgun SMTP
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
TEST_EMAIL_TO="${TEST_EMAIL_TO:-jgtolentino.rn@gmail.com}"
TEST_EMAIL_FROM="${ODOO_DEFAULT_FROM_EMAIL:-admin@insightpulseai.net}"

echo "════════════════════════════════════════════════════════════════"
echo "Test Outbound Email via Mailgun SMTP"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Container: $CONTAINER_NAME"
echo "  Database: $DB_NAME"
echo "  From: $TEST_EMAIL_FROM"
echo "  To: $TEST_EMAIL_TO"
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    echo "   Run: ./scripts/dev/up.sh"
    exit 1
fi

echo "🔧 Creating test email via Odoo shell..."

docker exec -i "$CONTAINER_NAME" odoo \
    -c "$ODOO_CONF" \
    -d "$DB_NAME" \
    --shell <<EOF
# Create test email
mail_vals = {
    'email_from': '${TEST_EMAIL_FROM}',
    'email_to': '${TEST_EMAIL_TO}',
    'subject': 'Parity test: Mailgun SMTP via Odoo 18 CE',
    'body_html': '''
        <p>This is a test email from Odoo 18 CE via Mailgun SMTP.</p>
        <p><strong>Purpose:</strong> Verify EE-parity outbound email functionality.</p>
        <p><strong>Timestamp:</strong> $(date -u +"%Y-%m-%d %H:%M:%S UTC")</p>
        <p><strong>Configuration:</strong></p>
        <ul>
            <li>SMTP Host: smtp.mailgun.org:587</li>
            <li>Encryption: STARTTLS</li>
            <li>Authentication: Mailgun SMTP Login</li>
        </ul>
        <p>If you received this, outbound email is working correctly.</p>
    ''',
}

mail = env['mail.mail'].sudo().create(mail_vals)
mail.send()

print(f"✅ Test email created (ID: {mail.id})")
print(f"   Message-ID: {mail.message_id}")
print(f"   State: {mail.state}")

# Check if sent successfully
if mail.state == 'sent':
    print("✅ Email sent successfully")
elif mail.state == 'exception':
    print(f"❌ Email send failed: {mail.failure_reason}")
else:
    print(f"⚠️  Email state: {mail.state}")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Test email sent!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Verification steps:"
echo "  1. Check inbox: $TEST_EMAIL_TO"
echo "  2. Check Mailgun logs: https://app.mailgun.com/mg/logs"
echo "  3. Verify SPF/DKIM/DMARC headers in received email"
echo "  4. Check for 'delivered' event in Odoo (after webhook fires)"
echo ""
echo "Expected headers in received email:"
echo "  - X-Mailgun-Variables: Mailgun routing info"
echo "  - DKIM-Signature: Domain signature"
echo "  - SPF: PASS (via Mailgun)"
echo ""
