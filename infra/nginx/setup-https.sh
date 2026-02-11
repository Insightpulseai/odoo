#!/usr/bin/env bash
set -euo pipefail

# Set up HTTPS with Let's Encrypt certbot for n8n, superset, and MCP
# Usage: ./setup-https.sh [--dry-run]

DROPLET_IP="178.128.112.214"
DROPLET_USER="root"
DOMAINS="n8n.insightpulseai.com,superset.insightpulseai.com,mcp.insightpulseai.com"
EMAIL="admin@insightpulseai.com"  # TODO: Update with actual email

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
fi

echo "🔒 Setting up HTTPS with Let's Encrypt..."
echo "   Domains: ${DOMAINS}"
echo "   Email: ${EMAIL}"
echo ""

# Check if certbot is installed
echo "📦 Checking certbot installation..."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "   [DRY RUN] Would check: certbot --version"
else
    if ! ssh "${DROPLET_USER}@${DROPLET_IP}" "command -v certbot >/dev/null 2>&1"; then
        echo "   ⚠️  certbot not found, installing..."
        ssh "${DROPLET_USER}@${DROPLET_IP}" "apt-get update && apt-get install -y certbot python3-certbot-nginx"
        echo "   ✅ certbot installed"
    else
        echo "   ✅ certbot already installed"
    fi
fi

# Obtain SSL certificates
echo ""
echo "🔐 Obtaining SSL certificates..."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "   [DRY RUN] Would run: certbot --nginx -d ${DOMAINS} --non-interactive --agree-tos -m ${EMAIL}"
else
    ssh "${DROPLET_USER}@${DROPLET_IP}" "certbot --nginx -d ${DOMAINS} --non-interactive --agree-tos -m ${EMAIL}"
    echo "   ✅ SSL certificates obtained and configured"
fi

# Test nginx configuration
echo ""
echo "🧪 Testing nginx configuration..."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "   [DRY RUN] Would run: nginx -t"
else
    ssh "${DROPLET_USER}@${DROPLET_IP}" "nginx -t"
fi

# Reload nginx
echo ""
echo "🔄 Reloading nginx..."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "   [DRY RUN] Would run: systemctl reload nginx"
else
    ssh "${DROPLET_USER}@${DROPLET_IP}" "systemctl reload nginx"
    echo "   ✅ nginx reloaded"
fi

# Test auto-renewal
echo ""
echo "🔄 Testing certificate auto-renewal..."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "   [DRY RUN] Would run: certbot renew --dry-run"
else
    ssh "${DROPLET_USER}@${DROPLET_IP}" "certbot renew --dry-run"
    echo "   ✅ Auto-renewal configured and tested"
fi

echo ""
echo "✅ HTTPS setup complete!"
echo ""
echo "📋 Verification:"
echo "   curl -I https://n8n.insightpulseai.com"
echo "   curl -I https://superset.insightpulseai.com"
echo "   curl -I https://mcp.insightpulseai.com"
echo ""
echo "📝 Certificate renewal:"
echo "   Certificates will auto-renew via systemd timer"
echo "   Check status: ssh ${DROPLET_USER}@${DROPLET_IP} 'systemctl status certbot.timer'"
