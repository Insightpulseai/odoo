#!/bin/bash
set -euo pipefail

# Odoo CE v0.9.1 - Production Deployment Script
# Target: VPS at 159.223.75.148 (erp.insightpulseai.com)
# Date: 2025-11-25

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Deploying Odoo CE v0.9.1 to Production"
echo "==========================================="

# Configuration
IMAGE_TAG="v0.9.1"
COMPOSE_FILE="deploy/docker-compose.prod.yml"
ENV_FILE="deploy/.env.production"

# Pre-flight checks
echo -e "\n${YELLOW}1. Pre-flight checks...${NC}"

# Check if we're on the VPS
if [[ -f "/etc/hostname" ]]; then
    HOSTNAME=$(cat /etc/hostname)
    if [[ "$HOSTNAME" == "odoo-erp-prod" ]]; then
        echo "✅ Running on production VPS: ${HOSTNAME}"
    else
        echo -e "${YELLOW}⚠️  Not on production VPS (hostname: ${HOSTNAME})${NC}"
        read -p "   Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Check if docker-compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo -e "${RED}❌ ${COMPOSE_FILE} not found!${NC}"
    exit 1
fi
echo "✅ Compose file found: ${COMPOSE_FILE}"

# Check if .env.production exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo -e "${RED}❌ ${ENV_FILE} not found!${NC}"
    echo "   Copy from .env.production.template and fill in real passwords."
    exit 1
fi

# Check if .env.production has real passwords (not placeholders)
if grep -q "CHANGE_ME" "$ENV_FILE"; then
    echo -e "${RED}❌ ${ENV_FILE} contains placeholder passwords!${NC}"
    echo "   Replace CHANGE_ME_* with real passwords before deploying."
    exit 1
fi
echo "✅ Environment file configured: ${ENV_FILE}"

# Check available RAM
AVAILABLE_RAM=$(free -g | awk '/^Mem:/{print $2}')
if [[ "$AVAILABLE_RAM" -lt 8 ]]; then
    echo -e "${YELLOW}⚠️  Only ${AVAILABLE_RAM}GB RAM available. 8GB+ recommended.${NC}"
    read -p "   Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Upgrade VPS RAM with: doctl compute droplet resize odoo-erp-prod --size s-4vcpu-8gb --wait"
        exit 1
    fi
else
    echo "✅ RAM: ${AVAILABLE_RAM}GB (sufficient)"
fi

# Check available disk space
AVAILABLE_DISK=$(df -h / | awk 'NR==2 {print $4}')
echo "✅ Disk space: ${AVAILABLE_DISK} available"

# Backup current deployment
echo -e "\n${YELLOW}2. Backing up current deployment...${NC}"

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup docker-compose
if [[ -f "docker-compose.yml" ]]; then
    cp docker-compose.yml "$BACKUP_DIR/docker-compose.yml.backup"
    echo "✅ Backed up docker-compose.yml"
fi

# Backup database (if postgres is running)
if docker ps | grep -q "odoo-db"; then
    echo "   Creating database backup..."
    docker exec odoo-db pg_dump -U odoo odoo > "$BACKUP_DIR/odoo_db_backup.sql"
    gzip "$BACKUP_DIR/odoo_db_backup.sql"
    echo "✅ Database backed up to ${BACKUP_DIR}/odoo_db_backup.sql.gz"
else
    echo "⚠️  Database container not running, skipping DB backup"
fi

# Pull new image
echo -e "\n${YELLOW}3. Pulling new image...${NC}"

cd "$(dirname "$COMPOSE_FILE")"
docker compose -f "$(basename "$COMPOSE_FILE")" --env-file "$(basename "$ENV_FILE")" pull odoo

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Failed to pull image!${NC}"
    exit 1
fi
echo "✅ Image pulled: ghcr.io/jgtolentino/odoo-ce:${IMAGE_TAG}"

# Stop current Odoo (keep database running)
echo -e "\n${YELLOW}4. Stopping Odoo container...${NC}"

docker compose -f "$(basename "$COMPOSE_FILE")" stop odoo

# Remove old container
docker compose -f "$(basename "$COMPOSE_FILE")" rm -f odoo

echo "✅ Old container removed"

# Start new container
echo -e "\n${YELLOW}5. Starting Odoo ${IMAGE_TAG}...${NC}"

docker compose -f "$(basename "$COMPOSE_FILE")" --env-file "$(basename "$ENV_FILE")" up -d odoo

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Failed to start container!${NC}"
    echo "   Attempting rollback..."
    # Rollback logic here if needed
    exit 1
fi

echo "✅ Container started"

# Wait for startup
echo -e "\n${YELLOW}6. Waiting for Odoo to start...${NC}"
echo -n "   "

for i in {1..30}; do
    if docker compose -f "$(basename "$COMPOSE_FILE")" ps | grep -q "Up (healthy)"; then
        echo -e "\n✅ Odoo is healthy!"
        break
    fi
    echo -n "."
    sleep 2

    if [[ $i -eq 30 ]]; then
        echo -e "\n${RED}❌ Timeout waiting for Odoo to become healthy${NC}"
        echo "   Check logs: docker compose -f ${COMPOSE_FILE} logs odoo"
        exit 1
    fi
done

# Test health endpoint
echo -e "\n${YELLOW}7. Testing health endpoint...${NC}"

if curl -sf http://127.0.0.1:8069/web/health > /dev/null; then
    echo "✅ Health endpoint responding"
else
    echo -e "${RED}❌ Health endpoint not responding${NC}"
    echo "   Check logs: docker compose -f ${COMPOSE_FILE} logs odoo"
    exit 1
fi

# Test web interface
echo -e "\n${YELLOW}8. Testing web interface...${NC}"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8069/web)
if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "302" ]]; then
    echo "✅ Web interface responding (HTTP ${HTTP_CODE})"
else
    echo -e "${YELLOW}⚠️  Web interface returned HTTP ${HTTP_CODE}${NC}"
fi

# Check for errors in logs
echo -e "\n${YELLOW}9. Checking logs for errors...${NC}"

ERROR_COUNT=$(docker compose -f "$(basename "$COMPOSE_FILE")" logs odoo --tail 100 | grep -c "ERROR\|CRITICAL" || echo "0")
if [[ "$ERROR_COUNT" -eq 0 ]]; then
    echo "✅ No errors in recent logs"
else
    echo -e "${YELLOW}⚠️  Found ${ERROR_COUNT} error(s) in logs${NC}"
    echo "   Review logs: docker compose -f ${COMPOSE_FILE} logs odoo --tail 50"
fi

# Cleanup old images
echo -e "\n${YELLOW}10. Cleaning up old images...${NC}"

OLD_IMAGES=$(docker images "ghcr.io/jgtolentino/odoo-ce" --format "{{.ID}} {{.Tag}}" | grep -v "${IMAGE_TAG}" | awk '{print $1}' || echo "")
if [[ -n "$OLD_IMAGES" ]]; then
    echo "$OLD_IMAGES" | xargs -r docker rmi || true
    echo "✅ Old images removed"
else
    echo "✅ No old images to remove"
fi

# Summary
echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""
echo "Deployment Details:"
echo "  Version: ${IMAGE_TAG}"
echo "  Container: odoo-ce"
echo "  Status: $(docker compose -f "$(basename "$COMPOSE_FILE")" ps odoo --format '{{.Status}}')"
echo "  Health: $(docker inspect odoo-ce --format='{{.State.Health.Status}}' 2>/dev/null || echo 'N/A')"
echo ""
echo "Access Points:"
echo "  Local: http://127.0.0.1:8069"
echo "  Public: https://erp.insightpulseai.com (via nginx)"
echo ""
echo "Backup Location:"
echo "  ${BACKUP_DIR}/"
echo ""
echo "Next Steps:"
echo "  1. Run smoke tests: ./scripts/smoketest.sh"
echo "  2. Test in browser: https://erp.insightpulseai.com"
echo "  3. Monitor logs: docker compose -f ${COMPOSE_FILE} logs -f odoo"
echo "  4. Check metrics: docker stats odoo-ce"
echo ""
echo "Rollback (if needed):"
echo "  ./scripts/rollback.sh ${BACKUP_DIR}"
echo ""
