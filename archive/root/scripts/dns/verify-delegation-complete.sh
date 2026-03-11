#!/usr/bin/env bash
set -euo pipefail

# Verify DNS Delegation is Complete
# Purpose: Check that nameservers are delegated to DigitalOcean
# Usage: ./scripts/dns/verify-delegation-complete.sh

DOMAIN="insightpulseai.com"

echo "════════════════════════════════════════════════════════════════"
echo "DNS Delegation Verification: $DOMAIN"
echo "════════════════════════════════════════════════════════════════"
echo

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if dig is available
if ! command -v dig &> /dev/null; then
    echo "❌ ERROR: dig command not found"
    echo "Install: sudo apt-get install dnsutils"
    exit 1
fi

echo "─────────────────────────────────────────────────────────────────"
echo "Checking Nameservers:"
echo "─────────────────────────────────────────────────────────────────"

NAMESERVERS=$(dig "$DOMAIN" NS +short | sort)

echo "$NAMESERVERS"
echo

# Check if DigitalOcean nameservers are present
if echo "$NAMESERVERS" | grep -q "digitalocean.com"; then
    echo -e "${GREEN}✅ Delegation to DigitalOcean COMPLETE${NC}"
    DELEGATED=1
else
    echo -e "${RED}❌ Delegation NOT complete${NC}"
    echo "Current nameservers are not DigitalOcean"
    echo
    echo "Expected nameservers:"
    echo "  - ns1.digitalocean.com"
    echo "  - ns2.digitalocean.com"
    echo "  - ns3.digitalocean.com"
    echo
    echo "Action required:"
    echo "  1. Log into Squarespace"
    echo "  2. Go to: Domains → $DOMAIN → DNS Settings"
    echo "  3. Change nameservers to DigitalOcean"
    echo "  4. Wait 2-6 hours for propagation"
    DELEGATED=0
fi

echo

if [ $DELEGATED -eq 1 ]; then
    echo "─────────────────────────────────────────────────────────────────"
    echo "Verifying DNS Records (via public DNS):"
    echo "─────────────────────────────────────────────────────────────────"
    
    verify_dns() {
        local name=$1
        local type=$2
        local expected=$3
        
        echo "Checking: $type $name"
        result=$(dig "$name" "$type" +short | head -n 1)
        
        if [ -n "$result" ] && echo "$result" | grep -q "$expected"; then
            echo -e "  ${GREEN}✅ $result${NC}"
        elif [ -n "$result" ]; then
            echo -e "  ${YELLOW}⚠️  $result (unexpected)${NC}"
        else
            echo -e "  ${RED}❌ Not found${NC}"
        fi
        echo
    }
    
    verify_dns "insightpulseai.com" "A" "178.128.112.214"
    verify_dns "erp.insightpulseai.com" "A" "178.128.112.214"
    verify_dns "n8n.insightpulseai.com" "A" "178.128.112.214"
    verify_dns "mg.insightpulseai.com" "MX" "mailgun.org"
    verify_dns "insightpulseai.com" "TXT" "spf1"
fi

echo "════════════════════════════════════════════════════════════════"
echo "Verification Complete"
echo "════════════════════════════════════════════════════════════════"
echo

if [ $DELEGATED -eq 1 ]; then
    echo -e "${GREEN}✅ DNS delegation is complete and working!${NC}"
    echo
    echo "You can now:"
    echo "  • Manage DNS via: doctl compute domain"
    echo "  • Automate with: scripts/dns/*.sh"
    echo "  • Version control: Terraform (infra/terraform/dns.tf)"
else
    echo -e "${YELLOW}⚠️  Delegation not yet complete${NC}"
    echo
    echo "If you just changed nameservers:"
    echo "  • Wait 2-6 hours for DNS propagation"
    echo "  • Run this script again to verify"
    echo
    echo "Monitor propagation: https://dnschecker.org"
fi

echo
