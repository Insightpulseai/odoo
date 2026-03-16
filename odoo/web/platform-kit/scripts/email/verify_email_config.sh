#!/usr/bin/env bash
# =============================================================================
# Email Configuration Verification Script
# Domain: insightpulseai.com
# Providers: Mailgun (outbound) + Zoho (inbound)
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="insightpulseai.com"
MG_DOMAIN="mg.insightpulseai.com"
ODOO_URL="${ODOO_URL:-https://erp.insightpulseai.com}"

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}Email Configuration Verification${NC}"
echo -e "${BLUE}Domain: ${DOMAIN}${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARN++))
}

# =============================================================================
# DNS Checks
# =============================================================================
echo -e "${BLUE}--- DNS Records ---${NC}"

# Check MX records (Zoho)
echo -n "Checking MX records for ${DOMAIN}... "
MX_RECORDS=$(dig +short MX ${DOMAIN} 2>/dev/null || echo "")
if echo "$MX_RECORDS" | grep -q "zoho.com"; then
    check_pass "MX records point to Zoho"
else
    check_fail "MX records not pointing to Zoho. Found: $MX_RECORDS"
fi

# Check SPF record
echo -n "Checking SPF record for ${DOMAIN}... "
SPF_RECORD=$(dig +short TXT ${DOMAIN} 2>/dev/null | grep "v=spf1" || echo "")
if echo "$SPF_RECORD" | grep -q "zohomail.com" && echo "$SPF_RECORD" | grep -q "mailgun.org"; then
    check_pass "SPF includes both Zoho and Mailgun"
elif echo "$SPF_RECORD" | grep -q "mailgun.org"; then
    check_warn "SPF includes Mailgun but not Zoho"
elif echo "$SPF_RECORD" | grep -q "zohomail.com"; then
    check_warn "SPF includes Zoho but not Mailgun"
else
    check_fail "SPF record missing or incomplete. Found: $SPF_RECORD"
fi

# Check DMARC record
echo -n "Checking DMARC record... "
DMARC_RECORD=$(dig +short TXT _dmarc.${DOMAIN} 2>/dev/null || echo "")
if echo "$DMARC_RECORD" | grep -q "v=DMARC1"; then
    check_pass "DMARC record exists"
else
    check_warn "DMARC record not found (recommended for email security)"
fi

# Check Mailgun subdomain SPF
echo -n "Checking SPF for ${MG_DOMAIN}... "
MG_SPF=$(dig +short TXT ${MG_DOMAIN} 2>/dev/null | grep "v=spf1" || echo "")
if echo "$MG_SPF" | grep -q "mailgun.org"; then
    check_pass "Mailgun subdomain SPF configured"
else
    check_fail "Mailgun subdomain SPF not found"
fi

# Check Mailgun DKIM
echo -n "Checking DKIM for Mailgun... "
DKIM_RECORD=$(dig +short TXT smtp._domainkey.${MG_DOMAIN} 2>/dev/null || echo "")
if [ -n "$DKIM_RECORD" ]; then
    check_pass "Mailgun DKIM record exists"
else
    check_fail "Mailgun DKIM record not found"
fi

echo ""

# =============================================================================
# Mailgun API Check
# =============================================================================
echo -e "${BLUE}--- Mailgun API ---${NC}"

if [ -n "${MAILGUN_API_KEY:-}" ]; then
    echo -n "Checking Mailgun domain status... "
    MG_STATUS=$(curl -s --user "api:${MAILGUN_API_KEY}" \
        "https://api.mailgun.net/v3/domains/${MG_DOMAIN}" 2>/dev/null || echo "{}")

    if echo "$MG_STATUS" | grep -q '"state": "active"'; then
        check_pass "Mailgun domain is active"
    elif echo "$MG_STATUS" | grep -q '"state":'; then
        STATE=$(echo "$MG_STATUS" | grep -o '"state": "[^"]*"' | cut -d'"' -f4)
        check_warn "Mailgun domain state: $STATE"
    else
        check_fail "Could not verify Mailgun domain status"
    fi

    echo -n "Checking Mailgun sending capability... "
    if echo "$MG_STATUS" | grep -q '"sending_dns_records"'; then
        check_pass "Mailgun sending records configured"
    else
        check_warn "Could not verify Mailgun sending records"
    fi
else
    check_warn "MAILGUN_API_KEY not set - skipping API checks"
fi

echo ""

# =============================================================================
# Odoo Connectivity Check
# =============================================================================
echo -e "${BLUE}--- Odoo Connectivity ---${NC}"

echo -n "Checking Odoo web accessibility... "
ODOO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${ODOO_URL}/web/login" 2>/dev/null || echo "000")
if [ "$ODOO_STATUS" = "200" ]; then
    check_pass "Odoo web is accessible"
elif [ "$ODOO_STATUS" = "302" ] || [ "$ODOO_STATUS" = "303" ]; then
    check_pass "Odoo web is accessible (redirect)"
else
    check_fail "Odoo web not accessible (HTTP $ODOO_STATUS)"
fi

echo ""

# =============================================================================
# SMTP Connectivity Check
# =============================================================================
echo -e "${BLUE}--- SMTP Connectivity ---${NC}"

echo -n "Checking SMTP port 587 (Mailgun)... "
if timeout 5 bash -c "echo >/dev/tcp/smtp.mailgun.org/587" 2>/dev/null; then
    check_pass "SMTP port 587 is reachable"
else
    check_fail "SMTP port 587 is not reachable"
fi

echo -n "Checking SMTP port 465 (Mailgun SSL)... "
if timeout 5 bash -c "echo >/dev/tcp/smtp.mailgun.org/465" 2>/dev/null; then
    check_pass "SMTP port 465 is reachable"
else
    check_warn "SMTP port 465 is not reachable (not required if using 587)"
fi

echo ""

# =============================================================================
# Environment Variables Check
# =============================================================================
echo -e "${BLUE}--- Environment Variables ---${NC}"

REQUIRED_VARS=(
    "MAILGUN_DOMAIN"
    "MAILGUN_API_KEY"
    "MAILGUN_SMTP_LOGIN"
    "MAILGUN_SMTP_PASSWORD"
)

for var in "${REQUIRED_VARS[@]}"; do
    echo -n "Checking $var... "
    if [ -n "${!var:-}" ]; then
        check_pass "$var is set"
    else
        check_fail "$var is not set"
    fi
done

echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}=============================================${NC}"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo -e "${YELLOW}Warnings: $WARN${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Some checks failed. Please review the output above.${NC}"
    exit 1
fi
