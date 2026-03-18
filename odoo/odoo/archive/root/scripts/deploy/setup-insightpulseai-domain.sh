#!/bin/bash
# Setup insightpulseai.com domain with SSL
# This script should be run on the droplet (178.128.112.214)

set -e

DROPLET_IP="178.128.112.214"
DOMAINS="insightpulseai.com,www.insightpulseai.com,erp.insightpulseai.com"
EMAIL="business@insightpulseai.com"

echo "=== InsightPulse AI Domain Setup ==="
echo "Droplet IP: $DROPLET_IP"
echo "Domains: $DOMAINS"
echo ""

# Step 1: Check current certificates
echo "[1/5] Checking existing certificates..."
if [ -d "/etc/letsencrypt/live/insightpulseai.com" ]; then
    echo "Certificate already exists for insightpulseai.com"
    certbot certificates -d insightpulseai.com 2>/dev/null || true
else
    echo "No existing certificate found"
fi

# Step 2: Create certbot webroot directory
echo ""
echo "[2/5] Setting up certbot webroot..."
mkdir -p /var/www/certbot

# Step 3: Stop nginx temporarily for standalone cert generation (if no existing cert)
echo ""
echo "[3/5] Generating/renewing SSL certificate..."

# Check if we need initial cert or renewal
if [ ! -d "/etc/letsencrypt/live/insightpulseai.com" ]; then
    echo "Generating new certificate (standalone mode)..."
    systemctl stop nginx || true

    certbot certonly --standalone \
        -d insightpulseai.com \
        -d www.insightpulseai.com \
        -d erp.insightpulseai.com \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive

    systemctl start nginx || true
else
    echo "Certificate exists, expanding to include all domains..."
    certbot certonly --nginx \
        -d insightpulseai.com \
        -d www.insightpulseai.com \
        -d erp.insightpulseai.com \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive \
        --expand
fi

# Step 4: Deploy nginx config
echo ""
echo "[4/5] Deploying nginx configuration..."

# Backup existing config
if [ -f /etc/nginx/sites-available/erp.insightpulseai.net.conf ]; then
    cp /etc/nginx/sites-available/erp.insightpulseai.net.conf \
       /etc/nginx/sites-available/erp.insightpulseai.net.conf.bak.$(date +%Y%m%d-%H%M%S)
fi

# Copy new config
cp /opt/odoo/repo/infra/deploy/nginx/insightpulseai.com.conf \
   /etc/nginx/sites-available/insightpulseai.com.conf

# Remove old symlink if exists
rm -f /etc/nginx/sites-enabled/erp.insightpulseai.net.conf

# Create new symlink
ln -sf /etc/nginx/sites-available/insightpulseai.com.conf \
       /etc/nginx/sites-enabled/insightpulseai.com.conf

# Test nginx config
echo "Testing nginx configuration..."
nginx -t

# Step 5: Reload nginx
echo ""
echo "[5/5] Reloading nginx..."
systemctl reload nginx

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Verify with:"
echo "  curl -I https://insightpulseai.com/web/health"
echo "  curl -I https://www.insightpulseai.com/"
echo "  curl -I https://erp.insightpulseai.com/"
echo ""
echo "All domains should redirect to https://insightpulseai.com"
