#!/usr/bin/env bash
set -euo pipefail

# Initial DigitalOcean Domain Setup
# Purpose: Create domain in DigitalOcean and add initial DNS records
# Usage: ./scripts/dns/setup-do-domain.sh

DOMAIN="insightpulseai.com"
DROPLET_IP="${DO_DROPLET_IP:-178.128.112.214}"

echo "════════════════════════════════════════════════════════════════"
echo "DigitalOcean Domain Setup: $DOMAIN"
echo "════════════════════════════════════════════════════════════════"
echo

# Check prerequisites
if ! command -v doctl &> /dev/null; then
    echo "❌ ERROR: doctl CLI not found"
    echo "Install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

if ! doctl account get &> /dev/null; then
    echo "❌ ERROR: doctl not authenticated"
    echo "Run: doctl auth init"
    echo "Or: export DIGITALOCEAN_ACCESS_TOKEN='dop_v1_xxxxx'"
    exit 1
fi

echo "✅ Prerequisites OK"
echo "   - doctl: $(doctl version | head -n1)"
echo "   - Account: $(doctl account get --format Email --no-header)"
echo

# Check if domain already exists
echo "─────────────────────────────────────────────────────────────────"
echo "Checking if domain exists..."
echo "─────────────────────────────────────────────────────────────────"

if doctl compute domain list --format Domain --no-header | grep -q "^${DOMAIN}$"; then
    echo "✅ Domain already exists: $DOMAIN"
    echo
else
    echo "Creating domain: $DOMAIN"
    
    if doctl compute domain create "$DOMAIN" --ip-address "$DROPLET_IP"; then
        echo "✅ Domain created successfully"
        echo
    else
        echo "❌ ERROR: Failed to create domain"
        exit 1
    fi
fi

# List current records
echo "─────────────────────────────────────────────────────────────────"
echo "Current DNS Records:"
echo "─────────────────────────────────────────────────────────────────"
doctl compute domain records list "$DOMAIN" --format ID,Type,Name,Data,TTL
echo

echo "════════════════════════════════════════════════════════════════"
echo "Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Next Steps:"
echo "  1. Run: ./scripts/dns/migrate-dns-to-do.sh"
echo "     (Migrate existing Squarespace records)"
echo
echo "  2. Delegate nameservers in Squarespace UI:"
echo "     - ns1.digitalocean.com"
echo "     - ns2.digitalocean.com"
echo "     - ns3.digitalocean.com"
echo
echo "  3. Wait 2-6 hours for propagation"
echo
echo "  4. Run: ./scripts/dns/verify-delegation-complete.sh"
echo
