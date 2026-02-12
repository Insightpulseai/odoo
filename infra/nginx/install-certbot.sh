#!/usr/bin/env bash
set -euo pipefail

# Install Certbot for HTTPS certificate management
# Target: Ubuntu/Debian on DigitalOcean droplet

DROPLET_IP="178.128.112.214"
DROPLET_USER="root"

echo "🔒 Installing Certbot on ${DROPLET_IP}..."

# Install certbot + nginx plugin
ssh "${DROPLET_USER}@${DROPLET_IP}" bash <<'REMOTE'
set -euo pipefail

echo "📦 Updating package list..."
apt-get update

echo "📦 Installing certbot and nginx plugin..."
apt-get install -y certbot python3-certbot-nginx

echo "✅ Certbot installed:"
certbot --version

echo ""
echo "📋 Next steps:"
echo "   1. Ensure DNS records are propagated (dig +short n8n.insightpulseai.com)"
echo "   2. Ensure nginx is serving HTTP on port 80"
echo "   3. Run: certbot --nginx -d n8n.insightpulseai.com -d superset.insightpulseai.com -d mcp.insightpulseai.com"
REMOTE

echo ""
echo "✅ Certbot installation complete!"
