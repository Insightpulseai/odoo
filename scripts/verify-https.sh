#!/bin/bash
# HTTPS Verification Script for erp.insightpulseai.net
# Tests if Odoo is correctly generating HTTPS URLs

set -e

SERVER="insightpulse-odoo"
DOMAIN="erp.insightpulseai.net"

echo "==================================="
echo "HTTPS Configuration Verification"
echo "==================================="

echo ""
echo "1. Checking Nginx X-Forwarded-Proto header..."
ssh $SERVER "nginx -T 2>&1 | grep -A 5 'server_name $DOMAIN' | grep 'X-Forwarded-Proto'"

echo ""
echo "2. Checking Odoo proxy_mode setting..."
ssh $SERVER "docker exec odoo-ce grep proxy_mode /etc/odoo/odoo.conf"

echo ""
echo "3. Checking database web.base.url..."
ssh $SERVER 'docker exec -i odoo-ce odoo shell -d odoo --no-http' <<'PYTHON'
base_url = env['ir.config_parameter'].get_param('web.base.url')
freeze = env['ir.config_parameter'].get_param('web.base.url.freeze')
print(f"web.base.url: {base_url}")
print(f"web.base.url.freeze: {freeze}")
PYTHON

echo ""
echo "4. Testing OAuth URL generation..."
echo "Direct to Odoo (should be HTTP - no proxy):"
ssh $SERVER "curl -sL 'http://127.0.0.1:8069/web' | grep -o 'redirect_uri=[^\"&]*' | head -1"

echo ""
echo "With X-Forwarded-Proto header (should be HTTPS):"
ssh $SERVER "curl -H 'X-Forwarded-Proto: https' -H 'X-Forwarded-Host: $DOMAIN' -sL 'http://127.0.0.1:8069/web' | grep -o 'redirect_uri=[^\"&]*' | head -1"

echo ""
echo "Through Nginx HTTPS (should be HTTPS):"
curl -sL "https://$DOMAIN/web" | grep -o 'redirect_uri=[^"&]*' | head -1

echo ""
echo "==================================="
echo "Verification Complete"
echo "==================================="
