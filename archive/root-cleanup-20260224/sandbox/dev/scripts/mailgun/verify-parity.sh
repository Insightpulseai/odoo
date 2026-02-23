#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Verify Email Parity Pack Installation
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
echo "Email Parity Pack Verification"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Counter for passed/failed checks
PASSED=0
FAILED=0

# Helper function for check results
check_result() {
    local test_name="$1"
    local result="$2"

    if [ "$result" = "0" ]; then
        echo "✅ $test_name"
        ((PASSED++))
    else
        echo "❌ $test_name"
        ((FAILED++))
    fi
}

# 1. Check addon directory exists
echo "📦 Checking addon structure..."
if [ -d "$PROJECT_ROOT/addons/ipai_mailgun_bridge" ]; then
    check_result "Addon directory exists" 0
else
    check_result "Addon directory exists" 1
fi

# 2. Check required files exist
for file in "__manifest__.py" "__init__.py" "controllers/__init__.py" "models/__init__.py" "data/mailgun_parameters.xml" "data/mailgun_catchall_aliases.xml"; do
    if [ -f "$PROJECT_ROOT/addons/ipai_mailgun_bridge/$file" ]; then
        check_result "File exists: $file" 0
    else
        check_result "File exists: $file" 1
    fi
done

# 3. Check environment variables
echo ""
echo "🔧 Checking environment variables..."
for var in MAILGUN_DOMAIN MAILGUN_API_KEY MAILGUN_SMTP_LOGIN SMTP_PASSWORD ODOO_DEFAULT_FROM_EMAIL ODOO_CATCHALL_DOMAIN; do
    if [ -n "${!var:-}" ]; then
        check_result "Variable set: $var" 0
    else
        check_result "Variable set: $var" 1
    fi
done

# 4. Check container is running
echo ""
echo "🐳 Checking Docker container..."
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    check_result "Container running: $CONTAINER_NAME" 0
else
    check_result "Container running: $CONTAINER_NAME" 1
    echo "   Run: ./scripts/dev/up.sh"
fi

# 5. Check addon installed (if container running)
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "📋 Checking addon installation..."

    ADDON_INSTALLED=$(docker exec "$CONTAINER_NAME" odoo \
        -c "$ODOO_CONF" \
        -d "$DB_NAME" \
        --shell <<EOF 2>/dev/null || echo "error"
module = env['ir.module.module'].sudo().search([('name', '=', 'ipai_mailgun_bridge')], limit=1)
if module and module.state == 'installed':
    print("installed")
else:
    print("not_installed")
EOF
)

    if echo "$ADDON_INSTALLED" | grep -q "installed"; then
        check_result "Addon installed in Odoo" 0
    else
        check_result "Addon installed in Odoo" 1
        echo "   Run: docker exec -it $CONTAINER_NAME odoo -d $DB_NAME -i ipai_mailgun_bridge --stop-after-init"
    fi

    # 6. Check SMTP server configured
    echo ""
    echo "📧 Checking SMTP configuration..."

    SMTP_CONFIGURED=$(docker exec "$CONTAINER_NAME" odoo \
        -c "$ODOO_CONF" \
        -d "$DB_NAME" \
        --shell <<EOF 2>/dev/null || echo "error"
smtp = env['ir.mail_server'].sudo().search([('name', '=', 'Mailgun SMTP')], limit=1)
if smtp and smtp.active:
    print("configured")
else:
    print("not_configured")
EOF
)

    if echo "$SMTP_CONFIGURED" | grep -q "configured"; then
        check_result "Mailgun SMTP server configured" 0
    else
        check_result "Mailgun SMTP server configured" 1
        echo "   Run: ./scripts/dev/configure-mailgun-smtp.sh"
    fi

    # 7. Check system parameters
    echo ""
    echo "⚙️  Checking system parameters..."

    for param in "ipai_mailgun.default_from" "mail.catchall.domain"; do
        PARAM_SET=$(docker exec "$CONTAINER_NAME" odoo \
            -c "$ODOO_CONF" \
            -d "$DB_NAME" \
            --shell <<EOF 2>/dev/null || echo "error"
value = env['ir.config_parameter'].sudo().get_param('$param')
if value:
    print("set")
else:
    print("not_set")
EOF
)

        if echo "$PARAM_SET" | grep -q "set"; then
            check_result "Parameter set: $param" 0
        else
            check_result "Parameter set: $param" 1
        fi
    done

    # 8. Check email aliases
    echo ""
    echo "📬 Checking email aliases..."

    for alias in "sales" "projects" "support"; do
        ALIAS_EXISTS=$(docker exec "$CONTAINER_NAME" odoo \
            -c "$ODOO_CONF" \
            -d "$DB_NAME" \
            --shell <<EOF 2>/dev/null || echo "error"
alias = env['mail.alias'].sudo().search([('alias_name', '=', '$alias')], limit=1)
if alias:
    print("exists")
else:
    print("not_exists")
EOF
)

        if echo "$ALIAS_EXISTS" | grep -q "exists"; then
            check_result "Alias exists: $alias@${ODOO_CATCHALL_DOMAIN:-insightpulseai.com}" 0
        else
            check_result "Alias exists: $alias@${ODOO_CATCHALL_DOMAIN:-insightpulseai.com}" 1
        fi
    done
fi

# 9. Check scripts are executable
echo ""
echo "📜 Checking scripts..."
for script in "scripts/dev/configure-mailgun-smtp.sh" "scripts/mailgun/configure-routes.sh" "scripts/mailgun/test-outbound-email.sh"; do
    if [ -x "$PROJECT_ROOT/$script" ]; then
        check_result "Script executable: $script" 0
    else
        check_result "Script executable: $script" 1
    fi
done

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Verification Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All checks passed! Email Parity Pack is ready."
    echo ""
    echo "Next steps:"
    echo "  1. Test outbound email: ./scripts/mailgun/test-outbound-email.sh"
    echo "  2. Configure Mailgun routes (production only): ./scripts/mailgun/configure-routes.sh"
    echo "  3. Verify webhooks accessible (production): curl -I https://erp.insightpulseai.com/mailgun/inbound"
    exit 0
else
    echo "⚠️  Some checks failed. Please review and fix before proceeding."
    exit 1
fi
