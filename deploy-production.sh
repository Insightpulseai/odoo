#!/usr/bin/env bash
# deploy-production.sh - Deploy Odoo CE v0.10.0-marketing-lean-amd64 to production
set -e

SERVER=159.223.75.148
IMAGE=ghcr.io/jgtolentino/odoo-ce:v0.10.0-marketing-lean-amd64
CONTAINER_NAME=odoo-ce

echo "🚀 Deploying Odoo CE Marketing (AMD64) to production..."
echo "Target: $SERVER (erp.insightpulseai.net)"
echo "Image: $IMAGE"
echo ""

ssh root@$SERVER <<'EOSSH'
set -e

IMAGE="ghcr.io/jgtolentino/odoo-ce:v0.10.0-marketing-lean-amd64"
CONTAINER_NAME="odoo-ce"

echo "📦 Pulling AMD64 image..."
docker pull "$IMAGE"

echo "🛑 Stopping old container (if running)..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true

echo "🗑️ Removing old container..."
docker rm "$CONTAINER_NAME" 2>/dev/null || true

echo "🚀 Starting new container (2-module minimalist strategy)..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --network deploy_odoo_backend \
  -p 127.0.0.1:8069:8069 \
  -e HOST=odoo-db \
  -e PORT=5432 \
  -e USER=odoo \
  -e PASSWORD="${DB_PASSWORD:-CHANGE_ME_STRONG_DB_PASSWORD}" \
  -v /var/lib/docker/volumes/deploy_odoo-filestore/_data:/var/lib/odoo \
  -v /var/lib/docker/volumes/deploy_odoo-logs/_data:/var/log/odoo \
  -v /root/odoo-prod/deploy/odoo.conf:/etc/odoo/odoo.conf \
  "$IMAGE"

echo "⏱ Waiting 20s for Odoo to initialize..."
sleep 20

echo ""
echo "✅ Container status:"
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' | grep "$CONTAINER_NAME" || echo "❌ Container not found!"

echo ""
echo "🌐 Health check (localhost:8069):"
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8069/web/health || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ HTTP $HTTP_CODE - Odoo is healthy!"
else
  echo "❌ HTTP $HTTP_CODE - Odoo not responding"
  echo ""
  echo "📋 Last 30 lines of logs:"
  docker logs "$CONTAINER_NAME" --tail=30
  exit 1
fi

echo ""
echo "🎉 Deployment successful!"
echo "🌍 Access at: https://erp.insightpulseai.net"
echo ""
echo "📊 Modules included:"
echo "  - Odoo CE 18.0 (native: accounting, CRM, sales, projects, HR)"
echo "  - 14 OCA repositories (financial tools, project extensions, reporting)"
echo "  - ipai_bir_compliance (BIR 2307 Tax Shield)"
echo "  - ipai_portal_fix (Portal rendering fix)"
echo ""
echo "🔧 Next steps:"
echo "  1. Login at https://erp.insightpulseai.net"
echo "  2. Install ipai_finance_ppm for BIR schedule & task hierarchy"
echo "  3. Configure Keycloak SSO for @omc.com users"
EOSSH

echo ""
echo "✅ Remote deployment completed!"
