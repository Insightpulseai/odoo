#!/usr/bin/env bash
# Configure Odoo system parameters for IPAI integration bus

set -euo pipefail

WEBHOOK_URL="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo-webhook"
WEBHOOK_SECRET="${ODOO_WEBHOOK_SECRET:-6900445459d89179a31e3bce61cf2d7f7732425650e17886edbbaec61c40a980}"

echo "=== Configuring Odoo System Parameters ==="
echo ""
echo "Webhook URL: ${WEBHOOK_URL}"
echo "Webhook Secret: ${WEBHOOK_SECRET:0:20}..."
echo ""

# Check if Odoo is running
if ! docker compose ps odoo-core | grep -q "Up"; then
    echo "❌ Odoo container not running. Start with: docker compose up -d odoo-core"
    exit 1
fi

# Configure via Odoo shell
docker compose exec -T odoo-core odoo shell -d odoo_core << EOF
# Set webhook URL
env['ir.config_parameter'].sudo().set_param('ipai.webhook.url', '${WEBHOOK_URL}')
print("✅ Set ipai.webhook.url = ${WEBHOOK_URL}")

# Set webhook secret
env['ir.config_parameter'].sudo().set_param('ipai.webhook.secret', '${WEBHOOK_SECRET}')
print("✅ Set ipai.webhook.secret = ${WEBHOOK_SECRET:0:20}...")

# Commit changes
env.cr.commit()
print("")
print("✅ System parameters configured successfully")

# Verify
url = env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
secret = env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')
print("")
print("Verification:")
print(f"  URL: {url}")
print(f"  Secret: {secret[:20]}... (length: {len(secret)})")
EOF

echo ""
echo "=== Configuration Complete ==="
