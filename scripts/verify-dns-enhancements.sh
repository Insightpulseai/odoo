#!/usr/bin/env bash
set -euo pipefail

# DNS Enhancement Verification Script
# Purpose: Verify recommended DNS changes for insightpulseai.net
# Usage: ./scripts/verify-dns-enhancements.sh

echo "════════════════════════════════════════════════════════════════"
echo "DNS Enhancement Verification - insightpulseai.net"
echo "════════════════════════════════════════════════════════════════"
echo

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

verify_record() {
    local name=$1
    local command=$2
    local expected=$3

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Checking: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    result=$(eval "$command" 2>/dev/null || echo "")

    if [ -n "$result" ]; then
        if [ -n "$expected" ] && echo "$result" | grep -q "$expected"; then
            echo -e "${GREEN}✅ CONFIGURED${NC}"
            echo "Result: $result"
        else
            echo -e "${YELLOW}⚠️  CONFIGURED (unexpected value)${NC}"
            echo "Result: $result"
            [ -n "$expected" ] && echo "Expected: $expected"
        fi
    else
        echo -e "${RED}❌ NOT CONFIGURED${NC}"
    fi
    echo
}

echo "═══ NEW RECORDS (Recommended Additions) ═══"
echo

verify_record \
    "1. Staging ERP DNS" \
    "dig erp.staging.insightpulseai.net A +short" \
    "178.128.112.214"

verify_record \
    "2. Root SPF" \
    "dig insightpulseai.net TXT +short | grep spf | sed 's/\"//g'" \
    "include:mailgun.org"

verify_record \
    "3. Root DMARC" \
    "dig _dmarc.insightpulseai.net TXT +short | sed 's/\"//g'" \
    "v=DMARC1"

echo "═══ EXISTING RECORDS (Sanity Check - DO NOT CHANGE) ═══"
echo

verify_record \
    "4. Mailgun mg SPF (existing)" \
    "dig mg.insightpulseai.net TXT +short | grep spf | sed 's/\"//g'" \
    "include:mailgun.org"

verify_record \
    "5. Mailgun mg DMARC (existing)" \
    "dig _dmarc.mg.insightpulseai.net TXT +short | sed 's/\"//g'" \
    "v=DMARC1"

verify_record \
    "6. Mailgun mg MX Records (existing)" \
    "dig mg.insightpulseai.net MX +short" \
    "mxa.mailgun.org"

verify_record \
    "7. Root A Record (existing)" \
    "dig insightpulseai.net A +short" \
    "178.128.112.214"

verify_record \
    "8. Production ERP DNS (existing)" \
    "dig erp.insightpulseai.net A +short" \
    "178.128.112.214"

echo "════════════════════════════════════════════════════════════════"
echo "Verification Complete"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Next Steps:"
echo "  1. Review results above"
echo "  2. If records missing (❌), apply changes from docs/infra/DNS_ENHANCEMENT_GUIDE.md"
echo "  3. Wait 5-15 minutes for DNS propagation"
echo "  4. Re-run this script to verify"
echo
