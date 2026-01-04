#!/usr/bin/env bash
# ==============================================================================
# FIX MISSING "SIGN IN WITH GOOGLE" BUTTON
# ==============================================================================
# Installs and configures auth_oauth module for Google SSO
# ==============================================================================

set -euo pipefail

CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)
DB_NAME="${1:-prod}"

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

# Step 1: Check if auth_oauth module exists
echo ">>> [1/5] Checking auth_oauth module availability..."

MODULE_EXISTS=$(docker exec -i "$CONTAINER_NAME" python3 <<'PYTHON_EOF'
import sys
import odoo
from odoo import api, SUPERUSER_ID

config = odoo.tools.config
config['db_name'] = 'prod'

try:
    odoo.service.server.load_server_wide_modules()
    registry = odoo.registry('prod')
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Check if module exists in filesystem
    module = env['ir.module.module'].search([('name', '=', 'auth_oauth')], limit=1)

    if module:
        print(f"FOUND|{module.state}")
    else:
        print("NOT_FOUND")
PYTHON_EOF
)

if [[ "$MODULE_EXISTS" == "NOT_FOUND" ]]; then
    echo "❌ CRITICAL: auth_oauth module not found in Odoo"
    echo "   This module should be part of Odoo CE standard distribution"
    echo "   Check: /usr/lib/python3/dist-packages/odoo/addons/auth_oauth"
    exit 1
fi

MODULE_STATE=$(echo "$MODULE_EXISTS" | cut -d'|' -f2)
echo "✓ auth_oauth module found (state: $MODULE_STATE)"

# Step 2: Install/Upgrade auth_oauth module
echo ""
echo ">>> [2/5] Installing/Upgrading auth_oauth module..."

if [[ "$MODULE_STATE" == "installed" ]]; then
    echo "Module already installed, upgrading..."
    docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" -u auth_oauth --stop-after-init --no-http
else
    echo "Installing auth_oauth module..."
    docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" -i auth_oauth --stop-after-init --no-http
fi

if [[ $? -eq 0 ]]; then
    echo "✓ auth_oauth module installed successfully"
else
    echo "❌ Failed to install auth_oauth module"
    exit 1
fi

# Step 3: Configure Google OAuth Provider
echo ""
echo ">>> [3/5] Configuring Google OAuth provider..."

docker exec -i "$CONTAINER_NAME" python3 <<'PYTHON_EOF'
import sys
import odoo
from odoo import api, SUPERUSER_ID

config = odoo.tools.config
config['db_name'] = 'prod'
odoo.service.server.load_server_wide_modules()
registry = odoo.registry('prod')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Google OAuth credentials
    GOOGLE_CLIENT_ID = "1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"

    # Find or create Google OAuth provider
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
        print(f"✓ Created Google OAuth provider (ID: {provider.id})")
    else:
        print(f"Updating existing provider (ID: {provider.id})...")
        provider.write({
            'name': 'Google',
            'secret': GOOGLE_CLIENT_SECRET,
            'auth_endpoint': 'https://accounts.google.com/o/oauth2/auth',
            'scope': 'openid email profile',
            'validation_endpoint': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'enabled': True,
            'css_class': 'fa fa-google',
            'body': 'Sign in with Google',
        })
        print("✓ Updated Google OAuth provider")

    # Verify base URL is correct
    base_url = env['ir.config_parameter'].get_param('web.base.url')
    if base_url != 'https://erp.insightpulseai.net':
        print(f"Updating web.base.url: {base_url} → https://erp.insightpulseai.net")
        env['ir.config_parameter'].set_param('web.base.url', 'https://erp.insightpulseai.net')
        env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')
    else:
        print("✓ web.base.url already correct")

    cr.commit()
    print("✓ Configuration saved to database")
PYTHON_EOF

if [[ $? -ne 0 ]]; then
    echo "❌ Failed to configure Google OAuth provider"
    exit 1
fi

# Step 4: Clear assets and restart
echo ""
echo ">>> [4/5] Regenerating web assets..."

docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" -u web --stop-after-init --no-http

echo "✓ Assets regenerated"

# Step 5: Restart Odoo
echo ""
echo ">>> [5/5] Restarting Odoo service..."

docker restart "$CONTAINER_NAME" > /dev/null

echo -n "Waiting for Odoo to restart"
for i in {1..30}; do
    if docker exec "$CONTAINER_NAME" pgrep -f "odoo-bin" > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 1
done

# Verify OAuth provider is active
echo ""
echo ">>> Verifying Google OAuth configuration..."

PROVIDER_ENABLED=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT enabled FROM auth_oauth_provider WHERE client_id='1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl.apps.googleusercontent.com';" | xargs)

if [[ "$PROVIDER_ENABLED" == "t" ]]; then
    echo "✓ Google OAuth provider is active"
else
    echo "❌ Google OAuth provider not active"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ GOOGLE OAUTH BUTTON FIX COMPLETED"
echo "=================================================="
echo ""
echo "Next Steps:"
echo "  1. Open Chrome Incognito: https://erp.insightpulseai.net"
echo "  2. Clear browser cache: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)"
echo "  3. Verify 'Sign in with Google' button appears"
echo "  4. Click button and test login"
echo ""
echo "If button still doesn't appear:"
echo "  - Check browser console (F12) for JavaScript errors"
echo "  - Verify you're accessing: https:// (not http://)"
echo "  - Try different browser (Firefox, Safari)"
echo ""
echo "Troubleshooting:"
echo "  - Check Odoo logs: docker logs $CONTAINER_NAME --tail 50"
echo "  - Verify module: Settings → Apps → Search 'auth_oauth'"
echo "  - Check provider: Settings → Technical → OAuth → Providers"
echo ""
