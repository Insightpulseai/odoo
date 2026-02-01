#!/usr/bin/env bash
# ==============================================================================
# FIX MISSING "SIGN IN WITH GOOGLE" BUTTON - odoo_core database
# ==============================================================================

set -euo pipefail

CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)
DB_NAME="odoo_core"

if [[ -z "$CONTAINER_NAME" ]]; then
    echo "❌ ERROR: No running Odoo container found"
    exit 1
fi

echo "=================================================="
echo "FIXING MISSING GOOGLE OAUTH BUTTON"
echo "=================================================="
echo "Container: $CONTAINER_NAME"
echo "Database: $DB_NAME"
echo ""

# Step 1: Install auth_oauth module
echo ">>> [1/4] Installing auth_oauth module..."
docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" -i auth_oauth --stop-after-init --no-http

echo "✓ auth_oauth module installed"

# Step 2: Configure Google OAuth provider
echo ""
echo ">>> [2/4] Configuring Google OAuth provider..."

docker exec -i "$CONTAINER_NAME" python3 <<'PYTHON_EOF'
import sys
import odoo
from odoo import api, SUPERUSER_ID

config = odoo.tools.config
config['db_name'] = 'odoo_core'
odoo.service.server.load_server_wide_modules()
registry = odoo.registry('odoo_core')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Google OAuth credentials
    GOOGLE_CLIENT_ID = "1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"

    # Create or update Google OAuth provider
    provider = env['auth.oauth.provider'].search([
        ('client_id', '=', GOOGLE_CLIENT_ID)
    ], limit=1)

    if not provider:
        print("Creating new Google OAuth provider...")
        provider = env['auth.oauth.provider'].create({
            'name': 'Google',
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'auth_endpoint': 'https://accounts.google.com/o/oauth2/auth',
            'scope': 'openid email profile',
            'validation_endpoint': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'enabled': True,
            'css_class': 'fa fa-google',
            'body': 'Sign in with Google',
        })
        print(f"✓ Created provider (ID: {provider.id})")
    else:
        print(f"Updating provider (ID: {provider.id})...")
        provider.write({
            'enabled': True,
            'secret': GOOGLE_CLIENT_SECRET,
        })
        print("✓ Updated provider")

    # Set base URL
    env['ir.config_parameter'].set_param('web.base.url', 'https://erp.insightpulseai.com')
    env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')

    cr.commit()
    print("✓ Configuration saved")
PYTHON_EOF

# Step 3: Regenerate assets
echo ""
echo ">>> [3/4] Regenerating web assets..."
docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" -u web --stop-after-init --no-http

# Step 4: Restart Odoo
echo ""
echo ">>> [4/4] Restarting Odoo..."
docker restart "$CONTAINER_NAME" > /dev/null

echo -n "Waiting for restart"
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
echo "✅ FIX COMPLETED"
echo "=================================================="
echo ""
echo "Clear browser cache and refresh: https://erp.insightpulseai.com"
echo ""
