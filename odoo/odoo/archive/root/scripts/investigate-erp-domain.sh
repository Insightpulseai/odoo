#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# ERP Domain Investigation Script
# =============================================================================
# Purpose: Investigate what's serving erp.insightpulseai.com and locate nginx config
# Server: nginx-prod-v2 (178.128.112.214)
# Issue: Currently serving Mattermost/TBWA content instead of Odoo
# =============================================================================

SERVER="178.128.112.214"
USER="${SSH_USER:-root}"
DOMAIN="erp.insightpulseai.com"

echo "=== ERP Domain Investigation ==="
echo "Server: $USER@$SERVER"
echo "Domain: $DOMAIN"
echo

# =============================================================================
# STEP 1: Connect and verify nginx
# =============================================================================
echo "--- Step 1: Verify nginx installation ---"
ssh "$USER@$SERVER" << 'EOF'
nginx -v
systemctl status nginx --no-pager | head -5
EOF
echo

# =============================================================================
# STEP 2: Find vhost configuration
# =============================================================================
echo "--- Step 2: Search for vhost configuration ---"
ssh "$USER@$SERVER" << EOF
echo "Searching for $DOMAIN in nginx configs..."
grep -Rni "$DOMAIN" /etc/nginx /etc/nginx/sites-* /etc/nginx/conf.d 2>/dev/null || echo "No config found for $DOMAIN"
EOF
echo

# =============================================================================
# STEP 3: Check what's being served
# =============================================================================
echo "--- Step 3: Check current upstream/docroot ---"
ssh "$USER@$SERVER" << 'EOF'
echo "Checking for proxy_pass or root directives:"
if [ -f /etc/nginx/sites-enabled/erp.conf ]; then
    grep -nE "root|proxy_pass|upstream" /etc/nginx/sites-enabled/erp.conf | head -20
elif [ -f /etc/nginx/conf.d/erp.insightpulseai.com.conf ]; then
    grep -nE "root|proxy_pass|upstream" /etc/nginx/conf.d/erp.insightpulseai.com.conf | head -20
else
    echo "⚠️  Could not find vhost config - checking nginx -T dump:"
    nginx -T 2>/dev/null | grep -A 30 "server_name.*erp.insightpulseai.com" | head -40
fi
EOF
echo

# =============================================================================
# STEP 4: Test local Odoo connection
# =============================================================================
echo "--- Step 4: Test if Odoo is running locally ---"
ssh "$USER@$SERVER" << 'EOF'
echo "Testing Odoo on port 8069:"
curl -v -H "Host: erp.insightpulseai.com" http://127.0.0.1:8069/web/login 2>&1 | head -20 || echo "❌ Odoo not accessible at 127.0.0.1:8069"
EOF
echo

# =============================================================================
# STEP 5: Check what HTTPS returns
# =============================================================================
echo "--- Step 5: Check what HTTPS is currently serving ---"
ssh "$USER@$SERVER" << 'EOF'
echo "Current HTTPS response (local check):"
curl -vk https://erp.insightpulseai.com/ 2>&1 | head -30
EOF
echo

# =============================================================================
# STEP 6: Check Docker containers
# =============================================================================
echo "--- Step 6: Check running Docker containers ---"
ssh "$USER@$SERVER" << 'EOF'
echo "Checking for Odoo containers:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}" | grep -i odoo || echo "No Odoo containers running"
echo
echo "All running containers:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
EOF
echo

# =============================================================================
# Summary
# =============================================================================
echo "=== Investigation Complete ==="
echo
echo "Next steps:"
echo "1. Review the vhost config location from Step 2"
echo "2. Check if it points to correct upstream (Step 3)"
echo "3. Verify Odoo is running (Step 4, Step 6)"
echo "4. If needed, update nginx config to proxy to Odoo"
echo
echo "To deploy the correct nginx config:"
echo "  scp deploy/nginx/erp.insightpulseai.com.conf $USER@$SERVER:/etc/nginx/sites-available/"
echo "  ssh $USER@$SERVER 'ln -sf /etc/nginx/sites-available/erp.insightpulseai.com.conf /etc/nginx/sites-enabled/ && nginx -t && systemctl reload nginx'"
