#!/usr/bin/env bash
set -euo pipefail

# Verify DigitalOcean DNS Configuration
# Purpose: Check that all expected DNS records exist in DigitalOcean
# Usage: ./scripts/dns/verify-do-dns.sh

DOMAIN="insightpulseai.com"

echo "════════════════════════════════════════════════════════════════"
echo "DigitalOcean DNS Verification: $DOMAIN"
echo "════════════════════════════════════════════════════════════════"
echo

# Check prerequisites
if ! command -v doctl &> /dev/null; then
    echo "❌ ERROR: doctl CLI not found"
    exit 1
fi

if ! doctl account get &> /dev/null; then
    echo "❌ ERROR: doctl not authenticated"
    exit 1
fi

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get all records
RECORDS=$(doctl compute domain records list "$DOMAIN" --format Type,Name,Data,Priority --no-header)

check_record() {
    local type=$1
    local name=$2
    local expected=$3
    
    if echo "$RECORDS" | grep -q "^${type}[[:space:]]*${name}[[:space:]].*${expected}"; then
        echo -e "${GREEN}✅ $type $name → $expected${NC}"
        return 0
    else
        echo -e "${RED}❌ $type $name → $expected (NOT FOUND)${NC}"
        return 1
    fi
}

echo "─────────────────────────────────────────────────────────────────"
echo "Production A Records:"
echo "─────────────────────────────────────────────────────────────────"

check_record "A" "@" "178.128.112.214"
check_record "A" "erp" "178.128.112.214"
check_record "A" "n8n" "178.128.112.214"
check_record "A" "mcp" "178.128.112.214"
check_record "A" "auth" "178.128.112.214"
check_record "A" "superset" "178.128.112.214"
echo

echo "─────────────────────────────────────────────────────────────────"
echo "CNAME Records:"
echo "─────────────────────────────────────────────────────────────────"

check_record "CNAME" "www" "@"
echo

echo "─────────────────────────────────────────────────────────────────"
echo "Mailgun MX Records:"
echo "─────────────────────────────────────────────────────────────────"

check_record "MX" "mg" "mxa.mailgun.org"
check_record "MX" "mg" "mxb.mailgun.org"
echo

echo "─────────────────────────────────────────────────────────────────"
echo "Mailgun TXT Records:"
echo "─────────────────────────────────────────────────────────────────"

check_record "TXT" "mg" "spf1"
check_record "CNAME" "email.mg" "mailgun.org"
echo

echo "─────────────────────────────────────────────────────────────────"
echo "Root SPF/DMARC:"
echo "─────────────────────────────────────────────────────────────────"

check_record "TXT" "@" "spf1"
check_record "TXT" "_dmarc" "DMARC1"
echo

echo "─────────────────────────────────────────────────────────────────"
echo "CAA Record:"
echo "─────────────────────────────────────────────────────────────────"

check_record "CAA" "@" "letsencrypt"
echo

echo "════════════════════════════════════════════════════════════════"
echo "Full DNS Record List:"
echo "════════════════════════════════════════════════════════════════"

doctl compute domain records list "$DOMAIN" --format Type,Name,Data,Priority,TTL

echo
echo "════════════════════════════════════════════════════════════════"
echo "Verification Complete"
echo "════════════════════════════════════════════════════════════════"
