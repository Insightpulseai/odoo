#!/usr/bin/env bash
set -euo pipefail

# Create Preview DNS for Branch Deployments
# Purpose: Auto-create DNS records for feature branch deployments
# Usage: ./scripts/dns/create-preview-dns.sh <branch-name>
# Example: ./scripts/dns/create-preview-dns.sh feature/new-ui
#          Creates: feat-new-ui.insightpulseai.com

DOMAIN="insightpulseai.com"
DROPLET_IP="${DO_DROPLET_IP:-178.128.112.214}"
TTL="${DNS_TTL:-3600}"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <branch-name>"
    echo
    echo "Examples:"
    echo "  $0 feature/new-ui     → feat-new-ui.$DOMAIN"
    echo "  $0 bugfix/login-error → bugfix-login-error.$DOMAIN"
    echo "  $0 main               → preview-main.$DOMAIN"
    exit 1
fi

BRANCH_NAME="$1"

# Check prerequisites
if ! command -v doctl &> /dev/null; then
    echo "❌ ERROR: doctl CLI not found"
    exit 1
fi

if ! doctl account get &> /dev/null; then
    echo "❌ ERROR: doctl not authenticated"
    exit 1
fi

# Sanitize branch name to valid DNS subdomain
# - Convert to lowercase
# - Replace slashes and special chars with hyphens
# - Truncate to 63 characters (DNS limit)
# - Remove leading/trailing hyphens
SUBDOMAIN=$(echo "$BRANCH_NAME" | \
    tr '[:upper:]' '[:lower:]' | \
    sed 's/[^a-z0-9-]/-/g' | \
    sed 's/^-*//;s/-*$//' | \
    cut -c1-63)

# Add prefix for preview environments
if [ "$SUBDOMAIN" = "main" ] || [ "$SUBDOMAIN" = "master" ]; then
    SUBDOMAIN="preview-main"
else
    SUBDOMAIN="preview-$SUBDOMAIN"
fi

FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

echo "════════════════════════════════════════════════════════════════"
echo "Creating Preview DNS Record"
echo "════════════════════════════════════════════════════════════════"
echo "Branch:  $BRANCH_NAME"
echo "DNS:     $FULL_DOMAIN"
echo "IP:      $DROPLET_IP"
echo "TTL:     ${TTL}s"
echo "════════════════════════════════════════════════════════════════"
echo

# Check if record already exists
EXISTING=$(doctl compute domain records list "$DOMAIN" \
    --format Name,Data --no-header | \
    grep "^${SUBDOMAIN}[[:space:]]" || true)

if [ -n "$EXISTING" ]; then
    echo "⚠️  Record already exists:"
    echo "$EXISTING"
    echo
    echo "Updating existing record..."
    
    # Get record ID
    RECORD_ID=$(doctl compute domain records list "$DOMAIN" \
        --format ID,Name --no-header | \
        grep "[[:space:]]${SUBDOMAIN}$" | \
        awk '{print $1}' | head -n 1)
    
    if [ -n "$RECORD_ID" ]; then
        doctl compute domain records update "$DOMAIN" \
            --record-id "$RECORD_ID" \
            --record-data "$DROPLET_IP" \
            --record-ttl "$TTL"
        echo "✅ Updated record ID: $RECORD_ID"
    fi
else
    echo "Creating new DNS record..."
    
    doctl compute domain records create "$DOMAIN" \
        --record-type A \
        --record-name "$SUBDOMAIN" \
        --record-data "$DROPLET_IP" \
        --record-ttl "$TTL"
    
    echo "✅ Created successfully"
fi

echo
echo "════════════════════════════════════════════════════════════════"
echo "Preview Environment Ready!"
echo "════════════════════════════════════════════════════════════════"
echo
echo "URL: https://$FULL_DOMAIN"
echo
echo "DNS propagation: 5-15 minutes (TTL: ${TTL}s)"
echo "Verify: dig $FULL_DOMAIN A +short"
echo
echo "Next steps:"
echo "  1. Wait for DNS propagation"
echo "  2. Configure nginx for this subdomain"
echo "  3. Request SSL certificate (certbot)"
echo
