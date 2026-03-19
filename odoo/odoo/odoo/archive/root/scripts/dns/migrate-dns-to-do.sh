#!/usr/bin/env bash
set -euo pipefail

# Migrate DNS Records to DigitalOcean
# Purpose: Create all production DNS records in DigitalOcean
# Usage: ./scripts/dns/migrate-dns-to-do.sh

DOMAIN="insightpulseai.com"
DROPLET_IP="${DO_DROPLET_IP:-178.128.112.214}"

echo "════════════════════════════════════════════════════════════════"
echo "Migrating DNS Records to DigitalOcean"
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

echo "Target Domain: $DOMAIN"
echo "Droplet IP: $DROPLET_IP"
echo

# Helper function to create record
create_record() {
    local type=$1
    local name=$2
    local data=$3
    local priority=${4:-}
    local ttl=${5:-3600}
    
    echo "Creating: $type $name → $data"
    
    local cmd="doctl compute domain records create $DOMAIN"
    cmd="$cmd --record-type $type"
    cmd="$cmd --record-name $name"
    cmd="$cmd --record-data \"$data\""
    cmd="$cmd --record-ttl $ttl"
    
    if [ -n "$priority" ]; then
        cmd="$cmd --record-priority $priority"
    fi
    
    if eval "$cmd" &> /dev/null; then
        echo "  ✅ Created"
    else
        echo "  ⚠️  Already exists or error (non-fatal)"
    fi
    echo
}

echo "─────────────────────────────────────────────────────────────────"
echo "Creating A Records (Production Hosts)"
echo "─────────────────────────────────────────────────────────────────"

create_record "A" "erp" "$DROPLET_IP"
create_record "A" "n8n" "$DROPLET_IP"
create_record "A" "mcp" "$DROPLET_IP"
create_record "A" "auth" "$DROPLET_IP"
create_record "A" "superset" "$DROPLET_IP"

echo "─────────────────────────────────────────────────────────────────"
echo "Creating CNAME Records"
echo "─────────────────────────────────────────────────────────────────"

create_record "CNAME" "www" "@"

echo "─────────────────────────────────────────────────────────────────"
echo "Creating Mailgun MX Records (mg subdomain)"
echo "─────────────────────────────────────────────────────────────────"

create_record "MX" "mg" "mxa.mailgun.org." 10
create_record "MX" "mg" "mxb.mailgun.org." 10

echo "─────────────────────────────────────────────────────────────────"
echo "Creating Mailgun TXT Records"
echo "─────────────────────────────────────────────────────────────────"

create_record "TXT" "mg" "v=spf1 include:mailgun.org ~all"
create_record "CNAME" "email.mg" "mailgun.org"

echo "⚠️  IMPORTANT: Mailgun DKIM key must be manually added"
echo "   Record Type: TXT"
echo "   Name: pic._domainkey.mg"
echo "   Value: k=rsa; p=<YOUR_DKIM_PUBLIC_KEY>"
echo "   Get from: Mailgun Dashboard → Sending → Domains"
echo

echo "─────────────────────────────────────────────────────────────────"
echo "Creating Root SPF and DMARC (Recommended)"
echo "─────────────────────────────────────────────────────────────────"

create_record "TXT" "@" "v=spf1 include:mailgun.org ~all"
create_record "TXT" "_dmarc" "v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org"

echo "─────────────────────────────────────────────────────────────────"
echo "Creating CAA Record (Let's Encrypt)"
echo "─────────────────────────────────────────────────────────────────"

create_record "CAA" "@" "0 issue \"letsencrypt.org\""

echo "─────────────────────────────────────────────────────────────────"
echo "Creating Staging Environment (Optional)"
echo "─────────────────────────────────────────────────────────────────"

create_record "A" "erp.staging" "$DROPLET_IP"

echo "════════════════════════════════════════════════════════════════"
echo "Migration Complete!"
echo "════════════════════════════════════════════════════════════════"
echo

# Show final state
echo "Final DNS Records:"
doctl compute domain records list "$DOMAIN" --format Type,Name,Data,Priority,TTL
echo

echo "Next Steps:"
echo "  1. Verify Mailgun DKIM record is added"
echo "  2. Run: ./scripts/dns/verify-do-dns.sh"
echo "  3. Delegate nameservers in Squarespace (see docs)"
echo
