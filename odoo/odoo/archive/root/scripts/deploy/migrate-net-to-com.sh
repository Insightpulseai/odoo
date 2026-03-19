#!/bin/bash
# Migrate from .net to .com domains
# Run on droplet (178.128.112.214)
#
# PREREQUISITES:
# 1. Add DNS A records in Squarespace for:
#    - www.insightpulseai.com -> 178.128.112.214
#    - n8n.insightpulseai.com -> 178.128.112.214
#    - mcp.insightpulseai.com -> 178.128.112.214

set -e

DROPLET_IP="178.128.112.214"
EMAIL="business@insightpulseai.com"

echo "=== Migrating from .net to .com ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check DNS
check_dns() {
    local domain=$1
    local ip=$(dig +short $domain 2>/dev/null | head -1)
    if [ "$ip" == "$DROPLET_IP" ]; then
        echo -e "${GREEN}✓${NC} $domain -> $ip"
        return 0
    else
        echo -e "${RED}✗${NC} $domain -> ${ip:-NO RECORD}"
        return 1
    fi
}

# Step 1: Verify DNS records
echo "[1/6] Checking DNS records..."
DNS_OK=true

check_dns "insightpulseai.com" || DNS_OK=false
check_dns "www.insightpulseai.com" || DNS_OK=false
check_dns "n8n.insightpulseai.com" || DNS_OK=false
check_dns "mcp.insightpulseai.com" || DNS_OK=false

if [ "$DNS_OK" = false ]; then
    echo ""
    echo -e "${RED}ERROR: DNS records missing. Please add them in Squarespace:${NC}"
    echo "  Type: A Record"
    echo "  Host: www, n8n, mcp (each separate)"
    echo "  Points to: $DROPLET_IP"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo -e "${GREEN}All DNS records verified!${NC}"

# Step 2: Create certbot directory
echo ""
echo "[2/6] Setting up certbot..."
mkdir -p /var/www/certbot/.well-known/acme-challenge

# Step 3: Create temporary HTTP configs for cert generation
echo ""
echo "[3/6] Creating temporary HTTP configs for cert generation..."

# Temporary config for Let's Encrypt validation
cat > /etc/nginx/sites-available/temp-com-acme.conf << 'ACME'
server {
    listen 80;
    server_name insightpulseai.com www.insightpulseai.com n8n.insightpulseai.com mcp.insightpulseai.com;

    location /.well-known/acme-challenge/ {
        alias /var/www/certbot/.well-known/acme-challenge/;
    }

    location / {
        return 503;
    }
}
ACME

ln -sf /etc/nginx/sites-available/temp-com-acme.conf /etc/nginx/sites-enabled/temp-com-acme.conf
nginx -t && systemctl reload nginx

# Step 4: Generate SSL certificates
echo ""
echo "[4/6] Generating SSL certificates..."

# Generate cert for main domain (insightpulseai.com + www)
certbot certonly --webroot \
    -w /var/www/certbot \
    -d insightpulseai.com \
    -d www.insightpulseai.com \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive \
    --force-renewal || true

# Generate cert for n8n
certbot certonly --webroot \
    -w /var/www/certbot \
    -d n8n.insightpulseai.com \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive \
    --force-renewal || true

# Generate cert for mcp
certbot certonly --webroot \
    -w /var/www/certbot \
    -d mcp.insightpulseai.com \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive \
    --force-renewal || true

# Step 5: Create production nginx configs
echo ""
echo "[5/6] Creating production nginx configs..."

# Main site - insightpulseai.com (Odoo)
cat > /etc/nginx/sites-available/insightpulseai.com.conf << 'NGINX_MAIN'
# insightpulseai.com - Main Odoo ERP
# Replaces: erp.insightpulseai.net

server {
    listen 80;
    server_name insightpulseai.com www.insightpulseai.com;

    location /.well-known/acme-challenge/ {
        alias /var/www/certbot/.well-known/acme-challenge/;
    }

    location / {
        return 301 https://insightpulseai.com$request_uri;
    }
}

# Redirect www to non-www
server {
    listen 443 ssl http2;
    server_name www.insightpulseai.com;

    ssl_certificate /etc/letsencrypt/live/insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/insightpulseai.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    return 301 https://insightpulseai.com$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name insightpulseai.com;

    ssl_certificate /etc/letsencrypt/live/insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/insightpulseai.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    client_max_body_size 100M;
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $host;

    # Odoo main
    location / {
        proxy_pass http://172.18.0.2:8069;
        proxy_redirect off;
    }

    # Odoo longpolling
    location /longpolling {
        proxy_pass http://172.18.0.2:8072;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files caching
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://172.18.0.2:8069;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /web/health {
        proxy_pass http://172.18.0.2:8069;
        access_log off;
    }

    # Mailgun webhook
    location /mailgate/mailgun {
        proxy_pass http://172.18.0.2:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/insightpulseai.com.access.log combined;
    error_log /var/log/nginx/insightpulseai.com.error.log warn;
}
NGINX_MAIN

# n8n.insightpulseai.com
cat > /etc/nginx/sites-available/n8n.insightpulseai.com.conf << 'NGINX_N8N'
# n8n.insightpulseai.com - n8n Automation
# Replaces: n8n.insightpulseai.net

server {
    listen 80;
    server_name n8n.insightpulseai.com;

    location /.well-known/acme-challenge/ {
        alias /var/www/certbot/.well-known/acme-challenge/;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name n8n.insightpulseai.com;

    ssl_certificate /etc/letsencrypt/live/n8n.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/n8n.insightpulseai.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        client_max_body_size 50M;
        proxy_buffering off;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }

    access_log /var/log/nginx/n8n.insightpulseai.com.access.log combined;
    error_log /var/log/nginx/n8n.insightpulseai.com.error.log warn;
}
NGINX_N8N

# mcp.insightpulseai.com
cat > /etc/nginx/sites-available/mcp.insightpulseai.com.conf << 'NGINX_MCP'
# mcp.insightpulseai.com - MCP Coordinator
# Replaces: mcp.insightpulseai.net

server {
    listen 80;
    server_name mcp.insightpulseai.com;

    location /.well-known/acme-challenge/ {
        alias /var/www/certbot/.well-known/acme-challenge/;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name mcp.insightpulseai.com;

    ssl_certificate /etc/letsencrypt/live/mcp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.insightpulseai.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-ID $request_id;
        client_max_body_size 10M;
        proxy_buffering off;
    }

    access_log /var/log/nginx/mcp.insightpulseai.com.access.log combined;
    error_log /var/log/nginx/mcp.insightpulseai.com.error.log warn;
}
NGINX_MCP

# Step 6: Switch nginx configs
echo ""
echo "[6/6] Switching to .com configs..."

# Backup .net configs
mkdir -p /etc/nginx/sites-backup
cp /etc/nginx/sites-available/*.net /etc/nginx/sites-backup/ 2>/dev/null || true

# Remove .net symlinks
rm -f /etc/nginx/sites-enabled/erp.insightpulseai.net
rm -f /etc/nginx/sites-enabled/n8n.insightpulseai.net
rm -f /etc/nginx/sites-enabled/mcp.insightpulseai.net
rm -f /etc/nginx/sites-enabled/www.insightpulseai.net
rm -f /etc/nginx/sites-enabled/temp-com-acme.conf

# Enable .com configs
ln -sf /etc/nginx/sites-available/insightpulseai.com.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/n8n.insightpulseai.com.conf /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/mcp.insightpulseai.com.conf /etc/nginx/sites-enabled/

# Test and reload
echo "Testing nginx configuration..."
nginx -t

echo "Reloading nginx..."
systemctl reload nginx

echo ""
echo -e "${GREEN}=== Migration Complete ===${NC}"
echo ""
echo "New domains:"
echo "  https://insightpulseai.com - Odoo ERP"
echo "  https://n8n.insightpulseai.com - n8n Automation"
echo "  https://mcp.insightpulseai.com - MCP Coordinator"
echo ""
echo "Verify with:"
echo "  curl -I https://insightpulseai.com/web/health"
echo "  curl -I https://n8n.insightpulseai.com"
echo "  curl -I https://mcp.insightpulseai.com"
echo ""
echo ".net configs backed up to: /etc/nginx/sites-backup/"
