#!/bin/bash
set -euo pipefail

# Email Authentication Verification Script
# Verifies DNS records, Supabase hook, SMTP connectivity, and Odoo configuration
# Usage: ./scripts/verify_email_auth.sh
# Exit codes: 0=all pass, 1=one or more failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MAILGUN_DOMAIN="mg.insightpulseai.net"
SMTP_HOST="smtp.mailgun.org"
SMTP_PORT="2525"
POSTGRES_URL_NON_POOLING="${POSTGRES_URL_NON_POOLING:-}"

# Track overall status
OVERALL_STATUS=0

# Helper functions
print_check() {
    echo -e "${GREEN}✓${NC} $1"
}

print_fail() {
    echo -e "${RED}✗${NC} $1"
    OVERALL_STATUS=1
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_section() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# 1. DNS Record Verification
print_section "DNS Record Verification"

# Check MX records
echo "Checking MX records for $MAILGUN_DOMAIN..."
MX_RECORDS=$(dig +short MX "$MAILGUN_DOMAIN" | sort)
if echo "$MX_RECORDS" | grep -q "mxa.mailgun.org" && echo "$MX_RECORDS" | grep -q "mxb.mailgun.org"; then
    print_check "MX records exist (mxa.mailgun.org, mxb.mailgun.org)"
else
    print_fail "MX records missing or incorrect"
    echo "  Expected: 10 mxa.mailgun.org, 10 mxb.mailgun.org"
    echo "  Found: $MX_RECORDS"
fi

# Check SPF record
echo "Checking SPF record for $MAILGUN_DOMAIN..."
SPF_RECORD=$(dig +short TXT "$MAILGUN_DOMAIN" | grep "v=spf1" || true)
if echo "$SPF_RECORD" | grep -q "include:mailgun.org"; then
    print_check "SPF record exists with mailgun.org include"
else
    print_fail "SPF record missing or incorrect"
    echo "  Expected: v=spf1 include:mailgun.org ~all"
    echo "  Found: $SPF_RECORD"
fi

# Check DKIM record
echo "Checking DKIM record for pic._domainkey.$MAILGUN_DOMAIN..."
DKIM_RECORD=$(dig +short TXT "pic._domainkey.$MAILGUN_DOMAIN" | tr -d '"' || true)
if echo "$DKIM_RECORD" | grep -q "v=DKIM1" && echo "$DKIM_RECORD" | grep -q "k=rsa"; then
    print_check "DKIM record exists with v=DKIM1 and k=rsa"
else
    print_fail "DKIM record missing or incorrect"
    echo "  Expected: v=DKIM1; k=rsa; p=..."
    echo "  Found: $DKIM_RECORD"
fi

# Check tracking CNAME
echo "Checking tracking CNAME for email.$MAILGUN_DOMAIN..."
TRACKING_CNAME=$(dig +short CNAME "email.$MAILGUN_DOMAIN" || true)
if echo "$TRACKING_CNAME" | grep -q "mailgun.org"; then
    print_check "Tracking CNAME exists (email.$MAILGUN_DOMAIN → mailgun.org)"
else
    print_fail "Tracking CNAME missing or incorrect"
    echo "  Expected: mailgun.org"
    echo "  Found: $TRACKING_CNAME"
fi

# Check DMARC record
echo "Checking DMARC record for _dmarc.$MAILGUN_DOMAIN..."
DMARC_RECORD=$(dig +short TXT "_dmarc.$MAILGUN_DOMAIN" | tr -d '"' || true)
if echo "$DMARC_RECORD" | grep -q "v=DMARC1"; then
    print_check "DMARC record exists"
    # Check policy level
    if echo "$DMARC_RECORD" | grep -q "p=reject"; then
        print_check "  Policy: reject (strictest)"
    elif echo "$DMARC_RECORD" | grep -q "p=quarantine"; then
        print_warn "  Policy: quarantine (consider upgrading to reject after testing)"
    elif echo "$DMARC_RECORD" | grep -q "p=none"; then
        print_warn "  Policy: none (monitoring only, upgrade to quarantine/reject)"
    fi
else
    print_fail "DMARC record missing or incorrect"
    echo "  Expected: v=DMARC1; p=quarantine; ..."
    echo "  Found: $DMARC_RECORD"
fi

# 2. Supabase Custom Access Token Hook Verification
print_section "Supabase Auth Configuration"

if [ -z "$POSTGRES_URL_NON_POOLING" ]; then
    print_warn "POSTGRES_URL_NON_POOLING not set, skipping database checks"
    print_warn "Set this environment variable to enable Supabase hook verification"
else
    echo "Checking custom_access_token_hook function..."
    HOOK_EXISTS=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
        "SELECT COUNT(*) FROM pg_proc WHERE proname = 'custom_access_token_hook';" 2>/dev/null || echo "0")

    if [ "$HOOK_EXISTS" -gt 0 ]; then
        print_check "custom_access_token_hook function exists"

        # Check if hook is enabled in auth.config
        HOOK_ENABLED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
            "SELECT value FROM auth.config WHERE parameter = 'hook.custom_access_token.uri';" 2>/dev/null || echo "")

        if [ -n "$HOOK_ENABLED" ]; then
            print_check "Custom access token hook is configured"
        else
            print_warn "Custom access token hook exists but may not be enabled in auth.config"
            print_warn "Check Supabase Dashboard → Authentication → Hooks → Custom Access Token"
        fi
    else
        print_fail "custom_access_token_hook function not found"
        echo "  Run: psql \$POSTGRES_URL_NON_POOLING < supabase/migrations/5002_auth_jwt_claims.sql"
    fi
fi

# 3. SMTP Connectivity Test
print_section "SMTP Connectivity"

echo "Testing SMTP connection to $SMTP_HOST:$SMTP_PORT..."

# Test SMTP connectivity using Python (more reliable than openssl for SMTP)
SMTP_TEST=$(python3 -c "
import smtplib
import sys

try:
    server = smtplib.SMTP('$SMTP_HOST', $SMTP_PORT, timeout=10)
    server.ehlo()
    if server.has_extn('STARTTLS'):
        server.starttls()
        server.ehlo()
        print('OK')
    else:
        print('NO_STARTTLS')
    server.quit()
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1)

if echo "$SMTP_TEST" | grep -q "OK"; then
    print_check "SMTP connection successful with STARTTLS support"
elif echo "$SMTP_TEST" | grep -q "NO_STARTTLS"; then
    print_warn "SMTP connection successful but STARTTLS not advertised"
else
    print_fail "SMTP connection failed"
    echo "  Error: $SMTP_TEST"
    echo "  Check network connectivity and firewall rules"
fi

# 4. Odoo Configuration Verification
print_section "Odoo Configuration"

if [ -z "$POSTGRES_URL_NON_POOLING" ]; then
    print_warn "Skipping Odoo config checks (POSTGRES_URL_NON_POOLING not set)"
else
    echo "Checking Odoo system parameters..."

    # Check web.base.url
    BASE_URL=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
        "SELECT value FROM ir_config_parameter WHERE key = 'web.base.url';" 2>/dev/null || echo "")

    if [ -n "$BASE_URL" ]; then
        BASE_URL=$(echo "$BASE_URL" | xargs) # trim whitespace
        if echo "$BASE_URL" | grep -q "^https://"; then
            print_check "web.base.url is set to HTTPS: $BASE_URL"
        else
            print_fail "web.base.url is not HTTPS: $BASE_URL"
            echo "  Expected: https://erp.insightpulseai.net"
        fi
    else
        print_fail "web.base.url not set"
        echo "  Run Odoo initialization script to set base URL"
    fi

    # Check web.base.url.freeze
    BASE_URL_FREEZE=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
        "SELECT value FROM ir_config_parameter WHERE key = 'web.base.url.freeze';" 2>/dev/null || echo "")

    if [ -n "$BASE_URL_FREEZE" ]; then
        if echo "$BASE_URL_FREEZE" | grep -qi "true"; then
            print_check "web.base.url.freeze is enabled (prevents URL changes)"
        else
            print_warn "web.base.url.freeze is not enabled"
            echo "  Recommendation: Enable to prevent accidental URL changes"
        fi
    else
        print_warn "web.base.url.freeze not set"
    fi

    # Check mail.default.from (should match Mailgun sender)
    MAIL_DEFAULT_FROM=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
        "SELECT value FROM ir_config_parameter WHERE key = 'mail.default.from';" 2>/dev/null || echo "")

    if [ -n "$MAIL_DEFAULT_FROM" ]; then
        MAIL_DEFAULT_FROM=$(echo "$MAIL_DEFAULT_FROM" | xargs)
        if echo "$MAIL_DEFAULT_FROM" | grep -q "@$MAILGUN_DOMAIN"; then
            print_check "mail.default.from uses Mailgun domain: $MAIL_DEFAULT_FROM"
        else
            print_warn "mail.default.from does not use Mailgun domain: $MAIL_DEFAULT_FROM"
            echo "  Expected: noreply@$MAILGUN_DOMAIN"
        fi
    else
        print_warn "mail.default.from not set"
        echo "  Will use system default (may cause deliverability issues)"
    fi

    # Check mail.catchall.domain
    MAIL_CATCHALL=$(psql "$POSTGRES_URL_NON_POOLING" -t -c \
        "SELECT value FROM ir_config_parameter WHERE key = 'mail.catchall.domain';" 2>/dev/null || echo "")

    if [ -n "$MAIL_CATCHALL" ]; then
        MAIL_CATCHALL=$(echo "$MAIL_CATCHALL" | xargs)
        if [ "$MAIL_CATCHALL" = "$MAILGUN_DOMAIN" ]; then
            print_check "mail.catchall.domain matches Mailgun: $MAIL_CATCHALL"
        else
            print_warn "mail.catchall.domain mismatch: $MAIL_CATCHALL (expected: $MAILGUN_DOMAIN)"
        fi
    else
        print_warn "mail.catchall.domain not set"
    fi
fi

# Summary
print_section "Verification Summary"

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed${NC}"
    echo ""
    echo "Email authentication is properly configured."
    echo "Next steps:"
    echo "  1. Test email flow: ./scripts/test_email_flow.sh"
    echo "  2. Send a real email and check DKIM/SPF/DMARC headers"
    exit 0
else
    echo -e "${RED}✗ One or more checks failed${NC}"
    echo ""
    echo "Review the errors above and:"
    echo "  1. Fix DNS records (see docs/auth/EMAIL_AUTH_SETUP.md)"
    echo "  2. Configure Supabase Auth (see docs/auth/EMAIL_AUTH_SETUP.md)"
    echo "  3. Configure Odoo SMTP (see infra/env/.env.example)"
    exit 1
fi
