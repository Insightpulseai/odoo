#!/usr/bin/env bash
# ==============================================================================
# GOOGLE OAUTH SSO CONFIGURATION FOR ODOO 18 CE
# ==============================================================================
# Configures Google OAuth for "Sign in with Google" functionality
#
# Prerequisites:
#   1. Google Cloud Project with OAuth 2.0 credentials
#   2. Authorized redirect URI: https://erp.insightpulseai.com/auth_oauth/signin
#   3. Odoo module 'auth_oauth' installed
#
# Usage:
#   ./scripts/configure_google_oauth.sh
# ==============================================================================

set -euo pipefail

# === Configuration ===
CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)
DB_NAME="${1:-prod}"

# Google OAuth Credentials (from your JSON)
GOOGLE_CLIENT_ID="1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
GOOGLE_PROJECT_ID="cba-ai"

# Odoo configuration
ODOO_BASE_URL="https://erp.insightpulseai.com"
REDIRECT_URI="${ODOO_BASE_URL}/auth_oauth/signin"

if [[ -z "$CONTAINER_NAME" ]]; then
    echo "❌ ERROR: No running Odoo container found"
    exit 1
fi

echo "=================================================="
echo "GOOGLE OAUTH SSO CONFIGURATION"
echo "=================================================="
echo "Client ID:    ${GOOGLE_CLIENT_ID:0:20}..."
echo "Redirect URI: $REDIRECT_URI"
echo "Database:     $DB_NAME"
echo ""

# === Step 1: Install auth_oauth module ===
echo ">>> [1/5] Checking auth_oauth module..."

MODULE_STATE=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT state FROM ir_module_module WHERE name='auth_oauth' LIMIT 1;" | xargs || echo "not_found")

if [[ "$MODULE_STATE" == "installed" ]]; then
    echo "✓ auth_oauth module already installed"
elif [[ "$MODULE_STATE" == "to install" ]] || [[ "$MODULE_STATE" == "to upgrade" ]]; then
    echo "Installing auth_oauth module..."
    docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" -i auth_oauth --stop-after-init
    echo "✓ auth_oauth module installed"
else
    echo "Installing auth_oauth module..."
    docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -c \
      "UPDATE ir_module_module SET state='to install' WHERE name='auth_oauth';"
    docker exec "$CONTAINER_NAME" odoo -d "$DB_NAME" -u auth_oauth --stop-after-init
    echo "✓ auth_oauth module installed"
fi

# === Step 2: Configure OAuth Provider ===
echo ""
echo ">>> [2/5] Configuring Google OAuth provider..."

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

    # Check if auth_oauth module is available
    if 'auth.oauth.provider' not in env.registry:
        print("❌ ERROR: auth_oauth module not properly installed")
        sys.exit(1)

    # 1. Clean up existing Google OAuth providers
    existing_providers = env['auth.oauth.provider'].search([
        '|',
        ('name', 'ilike', 'google'),
        ('client_id', '=', '$GOOGLE_CLIENT_ID')
    ])

    if existing_providers:
        print(f"Found {len(existing_providers)} existing Google OAuth provider(s)")
        print(f"Updating provider ID: {existing_providers[0].id}")
        provider = existing_providers[0]
        # Deactivate duplicates
        if len(existing_providers) > 1:
            existing_providers[1:].write({'enabled': False})
    else:
        print("Creating new Google OAuth provider...")
        provider = env['auth.oauth.provider'].create({
            'name': 'Google',
        })

    # 2. Configure Google OAuth provider
    provider.write({
        'client_id': '$GOOGLE_CLIENT_ID',
        'secret': '$GOOGLE_CLIENT_SECRET',
        'auth_endpoint': 'https://accounts.google.com/o/oauth2/auth',
        'scope': 'openid email profile',
        'validation_endpoint': 'https://www.googleapis.com/oauth2/v3/userinfo',
        'data_endpoint': None,  # Use validation_endpoint for user info
        'enabled': True,
        'css_class': 'fa fa-google',
        'body': 'Sign in with Google',
    })

    print(f"✓ Google OAuth provider configured (ID: {provider.id})")

    # 3. Ensure web.base.url is set correctly (required for OAuth redirects)
    base_url = env['ir.config_parameter'].get_param('web.base.url')
    if base_url != '$ODOO_BASE_URL':
        print(f"Updating web.base.url: {base_url} → $ODOO_BASE_URL")
        env['ir.config_parameter'].set_param('web.base.url', '$ODOO_BASE_URL')
        env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')

    print("✓ Base URL configured for OAuth")

    cr.commit()
    print("\n>>> SUCCESS: Google OAuth provider configured")
PYTHON_EOF

if [[ $? -ne 0 ]]; then
    echo "❌ OAuth configuration failed"
    exit 1
fi

# === Step 3: Verify database configuration ===
echo ""
echo ">>> [3/5] Verifying OAuth configuration..."

PROVIDER_COUNT=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT COUNT(*) FROM auth_oauth_provider WHERE enabled=true AND client_id='$GOOGLE_CLIENT_ID';" | xargs)

if [[ "$PROVIDER_COUNT" -eq 1 ]]; then
    echo "✓ Google OAuth provider verified in database"
else
    echo "❌ OAuth provider verification failed (found $PROVIDER_COUNT active providers)"
    exit 1
fi

# === Step 4: Test OAuth endpoints ===
echo ""
echo ">>> [4/5] Testing Google OAuth endpoints..."

# Test Google auth endpoint
if curl -sf "https://accounts.google.com/o/oauth2/auth" -o /dev/null; then
    echo "✓ Google auth endpoint reachable"
else
    echo "⚠️  WARNING: Google auth endpoint not reachable (network issue?)"
fi

# Test Google userinfo endpoint
if curl -sf "https://www.googleapis.com/oauth2/v3/userinfo" -o /dev/null; then
    echo "✓ Google userinfo endpoint reachable"
else
    echo "⚠️  WARNING: Google userinfo endpoint not reachable"
fi

# === Step 5: Restart Odoo ===
echo ""
echo ">>> [5/5] Restarting Odoo to apply changes..."

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
echo "✅ GOOGLE OAUTH SSO CONFIGURATION COMPLETED"
echo "=================================================="
echo ""
echo "Configuration Summary:"
echo "  Provider:        Google"
echo "  Client ID:       ${GOOGLE_CLIENT_ID:0:30}..."
echo "  Auth Endpoint:   https://accounts.google.com/o/oauth2/auth"
echo "  Redirect URI:    $REDIRECT_URI"
echo "  Base URL:        $ODOO_BASE_URL"
echo ""
echo "⚠️  IMPORTANT: Verify Google Cloud Console Configuration"
echo ""
echo "Go to: https://console.cloud.google.com/apis/credentials"
echo "Select project: $GOOGLE_PROJECT_ID"
echo "Edit OAuth 2.0 Client ID: ${GOOGLE_CLIENT_ID:0:20}..."
echo ""
echo "Verify Authorized Redirect URIs includes:"
echo "  $REDIRECT_URI"
echo ""
echo "If not present, add it and wait 5 minutes for propagation."
echo ""
echo "Next Steps (Testing):"
echo "  1. Open Chrome Incognito: $ODOO_BASE_URL"
echo "  2. Click 'Sign in with Google' button"
echo "  3. Select your Google account"
echo "  4. Grant permissions"
echo "  5. Verify successful login to Odoo"
echo ""
echo "Troubleshooting:"
echo "  - If redirect_uri_mismatch error: Check Google Cloud Console URIs"
echo "  - If infinite loop: Verify nginx X-Forwarded-Proto = https"
echo "  - If no Google button: Clear browser cache and retry"
echo ""
