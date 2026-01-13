#!/bin/bash
# fix-nginx-503-services.sh
# Fix nginx 503 errors for OCR, MCP, and Auth services
#
# Usage: ssh root@178.128.112.214 'bash -s' < scripts/fix-nginx-503-services.sh

set -euo pipefail

NGINX_CONF="/opt/odoo-ce/repo/deploy/nginx.conf"
BACKUP_CONF="${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"

echo "=== Fixing nginx 503 Services ==="
echo ""

# Backup current config
echo "1. Backing up nginx.conf..."
cp "$NGINX_CONF" "$BACKUP_CONF"
echo "   Backup: $BACKUP_CONF"
echo ""

# Check if fixes already applied
if grep -q "server ocr-prod:8001" "$NGINX_CONF"; then
    echo "✅ OCR upstream already configured"
else
    echo "2. Adding OCR service upstream and server block..."

    # Find the line with "upstream ocr {" placeholder
    # Replace placeholder with actual configuration
    sed -i '/upstream ocr {/,/}/c\
upstream ocr {\
    server ocr-prod:8001;\
}' "$NGINX_CONF"

    # Replace 503 placeholder with proxy
    sed -i '/server_name ocr\.insightpulseai\.net;/,/}/c\
    server {\
        listen 443 ssl http2;\
        server_name ocr.insightpulseai.net;\
\
        ssl_certificate /etc/letsencrypt/live/www.insightpulseai.net/fullchain.pem;\
        ssl_certificate_key /etc/letsencrypt/live/www.insightpulseai.net/privkey.pem;\
        ssl_protocols TLSv1.2 TLSv1.3;\
        ssl_ciphers HIGH:!aNULL:!MD5;\
\
        location / {\
            proxy_pass http://ocr;\
            proxy_set_header Host $host;\
            proxy_set_header X-Real-IP $remote_addr;\
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
            proxy_set_header X-Forwarded-Proto $scheme;\
            client_max_body_size 100M;\
        }\
    }' "$NGINX_CONF"

    echo "   ✅ OCR service configured"
fi
echo ""

if grep -q "server mcp-prod:3000" "$NGINX_CONF"; then
    echo "✅ MCP upstream already configured"
else
    echo "3. Adding MCP service upstream and server block..."

    sed -i '/upstream mcp {/,/}/c\
upstream mcp {\
    server mcp-prod:3000;\
}' "$NGINX_CONF"

    sed -i '/server_name mcp\.insightpulseai\.net;/,/}/c\
    server {\
        listen 443 ssl http2;\
        server_name mcp.insightpulseai.net;\
\
        ssl_certificate /etc/letsencrypt/live/www.insightpulseai.net/fullchain.pem;\
        ssl_certificate_key /etc/letsencrypt/live/www.insightpulseai.net/privkey.pem;\
        ssl_protocols TLSv1.2 TLSv1.3;\
        ssl_ciphers HIGH:!aNULL:!MD5;\
\
        location / {\
            proxy_pass http://mcp;\
            proxy_set_header Host $host;\
            proxy_set_header X-Real-IP $remote_addr;\
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
            proxy_set_header X-Forwarded-Proto $scheme;\
            \
            # WebSocket support for MCP\
            proxy_http_version 1.1;\
            proxy_set_header Upgrade $http_upgrade;\
            proxy_set_header Connection "upgrade";\
        }\
    }' "$NGINX_CONF"

    echo "   ✅ MCP service configured"
fi
echo ""

if grep -q "server auth-prod:8080" "$NGINX_CONF"; then
    echo "✅ Auth upstream already configured"
else
    echo "4. Adding Auth service upstream and server block..."

    sed -i '/upstream auth {/,/}/c\
upstream auth {\
    server auth-prod:8080;\
}' "$NGINX_CONF"

    sed -i '/server_name auth\.insightpulseai\.net;/,/}/c\
    server {\
        listen 443 ssl http2;\
        server_name auth.insightpulseai.net;\
\
        ssl_certificate /etc/letsencrypt/live/www.insightpulseai.net/fullchain.pem;\
        ssl_certificate_key /etc/letsencrypt/live/www.insightpulseai.net/privkey.pem;\
        ssl_protocols TLSv1.2 TLSv1.3;\
        ssl_ciphers HIGH:!aNULL:!MD5;\
\
        location / {\
            proxy_pass http://auth;\
            proxy_set_header Host $host;\
            proxy_set_header X-Real-IP $remote_addr;\
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
            proxy_set_header X-Forwarded-Proto $scheme;\
        }\
    }' "$NGINX_CONF"

    echo "   ✅ Auth service configured"
fi
echo ""

# Test nginx configuration
echo "5. Testing nginx configuration..."
if docker exec nginx-prod-v2 nginx -t; then
    echo "   ✅ Configuration valid"
else
    echo "   ❌ Configuration invalid - restoring backup"
    cp "$BACKUP_CONF" "$NGINX_CONF"
    exit 1
fi
echo ""

# Reload nginx
echo "6. Reloading nginx (zero downtime)..."
docker exec nginx-prod-v2 nginx -s reload
echo "   ✅ Nginx reloaded"
echo ""

# Verify services
echo "7. Verifying services..."
echo ""

for service in ocr mcp auth; do
    url="https://${service}.insightpulseai.net"
    echo -n "   Testing $url... "

    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")

    if [ "$status" = "503" ]; then
        echo "❌ Still 503"
    elif [ "$status" = "000" ]; then
        echo "❌ Connection failed"
    else
        echo "✅ HTTP $status (service responding)"
    fi
done
echo ""

echo "=== Fix Complete ==="
echo ""
echo "Backup saved: $BACKUP_CONF"
echo "Nginx config: $NGINX_CONF"
echo ""
echo "To rollback if needed:"
echo "  cp $BACKUP_CONF $NGINX_CONF"
echo "  docker exec nginx-prod-v2 nginx -s reload"
