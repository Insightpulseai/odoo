#!/usr/bin/env bash
# ==============================================================================
# GMAIL SMTP CONFIGURATION FOR ODOO 18 CE
# ==============================================================================
# Configures Gmail as outgoing email server using App Password
#
# Prerequisites:
#   1. Gmail account with 2FA enabled
#   2. Gmail App Password generated (16 chars, no spaces)
#   3. App Password stored in environment or passed as argument
#
# Usage:
#   ./scripts/configure_gmail_smtp.sh [gmail_user] [app_password]
#   or (interactive):
#   ./scripts/configure_gmail_smtp.sh
# ==============================================================================

set -euo pipefail

# === Configuration ===
CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)
DB_NAME="${3:-prod}"

if [[ -z "$CONTAINER_NAME" ]]; then
    echo "❌ ERROR: No running Odoo container found"
    exit 1
fi

# === Get Gmail Credentials ===
if [[ $# -ge 2 ]]; then
    # Arguments provided
    GMAIL_USER="$1"
    GMAIL_PASS="$2"
else
    # Interactive mode
    echo "=================================================="
    echo "GMAIL SMTP CONFIGURATION"
    echo "=================================================="
    echo ""
    echo "Prerequisites:"
    echo "  1. Gmail account with 2FA enabled"
    echo "  2. App Password generated from: https://myaccount.google.com/apppasswords"
    echo ""

    read -p "Enter your Gmail address: " GMAIL_USER
    read -sp "Enter your Gmail App Password (16 chars): " GMAIL_PASS
    echo ""
fi

# Validate inputs
if [[ -z "$GMAIL_USER" ]] || [[ -z "$GMAIL_PASS" ]]; then
    echo "❌ ERROR: Gmail credentials are required"
    exit 1
fi

# Validate Gmail format
if [[ ! "$GMAIL_USER" =~ ^[a-zA-Z0-9._%+-]+@gmail\.com$ ]]; then
    echo "❌ ERROR: Invalid Gmail address format"
    exit 1
fi

# Validate App Password format (16 chars, alphanumeric)
CLEAN_PASS=$(echo "$GMAIL_PASS" | tr -d ' ')
if [[ ${#CLEAN_PASS} -ne 16 ]]; then
    echo "⚠️  WARNING: App Password should be 16 characters (found ${#CLEAN_PASS})"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo ">>> [1/4] Configuring Gmail SMTP in Odoo..."

# === Python Script to Configure SMTP ===
docker exec -i "$CONTAINER_NAME" python3 <<PYTHON_EOF
import sys
import odoo
from odoo import api, SUPERUSER_ID

# Initialize Odoo environment
DB_NAME = '$DB_NAME'
config = odoo.tools.config
config['db_name'] = DB_NAME

try:
    odoo.service.server.load_server_wide_modules()
    registry = odoo.registry(DB_NAME)
except Exception as e:
    print(f"❌ Failed to initialize Odoo: {e}")
    sys.exit(1)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # 1. Clean up existing Gmail servers (prevent duplicates)
    existing_servers = env['ir.mail_server'].search([
        '|',
        ('smtp_host', '=', 'smtp.gmail.com'),
        ('description', '=', 'Gmail SMTP')
    ])

    if existing_servers:
        print(f"Found {len(existing_servers)} existing Gmail server(s)")
        print(f"Updating server ID: {existing_servers[0].id}")
        server = existing_servers[0]
        # Deactivate duplicates
        if len(existing_servers) > 1:
            existing_servers[1:].write({'active': False})
    else:
        print("Creating new Gmail SMTP server...")
        server = env['ir.mail_server'].create({
            'name': 'Gmail SMTP',
            'description': 'Gmail SMTP (App Password)'
        })

    # 2. Configure Gmail SMTP settings
    server.write({
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 465,
        'smtp_encryption': 'ssl',  # SSL (port 465) is more reliable than STARTTLS (587)
        'smtp_user': '$GMAIL_USER',
        'smtp_pass': '$CLEAN_PASS',
        'sequence': 1,  # Highest priority
        'active': True
    })

    print(f"✓ Gmail SMTP server configured (ID: {server.id})")

    # 3. Set default 'From' address to match Gmail
    env['ir.config_parameter'].set_param('mail.default.from', '$GMAIL_USER')
    env['ir.config_parameter'].set_param('mail.catchall.domain', 'gmail.com')
    env['ir.config_parameter'].set_param('mail.catchall.alias', '$GMAIL_USER')

    print("✓ Default mail parameters configured")

    # 4. Disable other mail servers to prevent conflicts
    other_servers = env['ir.mail_server'].search([
        ('id', '!=', server.id),
        ('active', '=', True)
    ])

    if other_servers:
        print(f"Disabling {len(other_servers)} conflicting mail server(s)")
        other_servers.write({'active': False})

    cr.commit()
    print("\n>>> SUCCESS: Gmail SMTP configured securely")
PYTHON_EOF

if [[ $? -ne 0 ]]; then
    echo "❌ SMTP configuration failed"
    exit 1
fi

echo ""
echo ">>> [2/4] Verifying database configuration..."

# Verify mail server in database
SMTP_HOST=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT smtp_host FROM ir_mail_server WHERE active=true AND sequence=1 LIMIT 1;" | xargs)

if [[ "$SMTP_HOST" == "smtp.gmail.com" ]]; then
    echo "✓ SMTP host verified: smtp.gmail.com"
else
    echo "❌ SMTP host mismatch: $SMTP_HOST"
    exit 1
fi

echo ""
echo ">>> [3/4] Testing SMTP connection..."

# Test SMTP connection
docker exec -i "$CONTAINER_NAME" python3 <<TEST_EOF
import sys
import odoo
from odoo import api, SUPERUSER_ID

config = odoo.tools.config
config['db_name'] = '$DB_NAME'
odoo.service.server.load_server_wide_modules()
registry = odoo.registry('$DB_NAME')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    server = env['ir.mail_server'].search([
        ('smtp_host', '=', 'smtp.gmail.com'),
        ('active', '=', True)
    ], limit=1)

    if not server:
        print("❌ No active Gmail SMTP server found")
        sys.exit(1)

    try:
        # Test connection
        smtp = server.connect()
        smtp.quit()
        print("✓ SMTP connection test successful")
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        sys.exit(1)
TEST_EOF

if [[ $? -ne 0 ]]; then
    echo ""
    echo "⚠️  SMTP connection test failed. Common issues:"
    echo "  1. App Password is incorrect (not your Gmail password)"
    echo "  2. 2FA not enabled on Gmail account"
    echo "  3. App Password revoked or expired"
    echo "  4. Gmail account blocked due to suspicious activity"
    echo ""
    echo "Troubleshooting:"
    echo "  - Generate new App Password: https://myaccount.google.com/apppasswords"
    echo "  - Check Gmail security: https://myaccount.google.com/security"
    echo ""
    exit 1
fi

echo ""
echo ">>> [4/4] Restarting Odoo to apply changes..."

docker restart "$CONTAINER_NAME" > /dev/null

# Wait for Odoo to restart
echo -n "Waiting for Odoo to restart"
for i in {1..30}; do
    if docker exec "$CONTAINER_NAME" pgrep -f "odoo-bin" > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "=================================================="
echo "✅ GMAIL SMTP CONFIGURATION COMPLETED"
echo "=================================================="
echo ""
echo "Configuration Summary:"
echo "  SMTP Host:       smtp.gmail.com"
echo "  SMTP Port:       465 (SSL)"
echo "  SMTP User:       $GMAIL_USER"
echo "  Default From:    $GMAIL_USER"
echo ""
echo "Next Steps:"
echo "  1. Login to Odoo: https://erp.insightpulseai.net"
echo "  2. Go to: Settings → Technical → Email → Outgoing Mail Servers"
echo "  3. Click 'Gmail SMTP' server"
echo "  4. Click 'Test Connection' button"
echo "  5. Verify popup shows 'Connection Test Successful!'"
echo ""
echo "Send Test Email:"
echo "  Settings → Technical → Email → Emails"
echo "  Click 'Create' → Fill recipient → Click 'Send Now'"
echo ""
