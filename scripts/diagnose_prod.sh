#!/bin/bash
# =============================================================================
# Production Diagnostics & Recovery Script
# =============================================================================
# Run on: erp.insightpulseai.net (178.128.112.214)
# Usage: ./scripts/diagnose_prod.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() { echo -e "\n${BLUE}=== $1 ===${NC}"; }

COMPOSE_FILE="${COMPOSE_FILE:-/opt/odoo-ce/deploy/docker-compose.prod.yml}"
REPO_DIR="${REPO_DIR:-/opt/odoo-ce}"

echo "============================================="
echo "  Production Diagnostics"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "============================================="

# -----------------------------------------------------------------------------
log_section "1. System Status"
# -----------------------------------------------------------------------------
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo "Disk: $(df -h / | tail -1 | awk '{print $5 " used"}')"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"

# -----------------------------------------------------------------------------
log_section "2. Docker Status"
# -----------------------------------------------------------------------------
if ! command -v docker &> /dev/null; then
    log_error "Docker not installed!"
    exit 1
fi

docker --version
docker compose version 2>/dev/null || docker-compose --version

echo ""
log_info "All containers:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -20

# -----------------------------------------------------------------------------
log_section "3. Odoo Container"
# -----------------------------------------------------------------------------
ODOO_CONTAINER=$(docker ps -a --filter "name=odoo" --format "{{.Names}}" | head -1)

if [ -z "$ODOO_CONTAINER" ]; then
    log_error "No Odoo container found!"

    log_warn "Attempting to start from compose file..."
    if [ -f "$COMPOSE_FILE" ]; then
        cd "$(dirname "$COMPOSE_FILE")"
        docker compose -f "$(basename "$COMPOSE_FILE")" up -d
        sleep 30
        ODOO_CONTAINER=$(docker ps -a --filter "name=odoo" --format "{{.Names}}" | head -1)
    fi
fi

if [ -n "$ODOO_CONTAINER" ]; then
    log_info "Container: $ODOO_CONTAINER"

    STATUS=$(docker inspect -f '{{.State.Status}}' "$ODOO_CONTAINER" 2>/dev/null || echo "unknown")
    echo "Status: $STATUS"

    if [ "$STATUS" != "running" ]; then
        log_error "Container not running!"

        log_warn "Last 50 lines of logs:"
        docker logs "$ODOO_CONTAINER" --tail 50 2>&1 || true

        log_warn "Attempting restart..."
        docker start "$ODOO_CONTAINER" || docker restart "$ODOO_CONTAINER" || true
        sleep 30
    fi

    # Check health
    HEALTH=$(docker inspect -f '{{.State.Health.Status}}' "$ODOO_CONTAINER" 2>/dev/null || echo "no healthcheck")
    echo "Health: $HEALTH"
fi

# -----------------------------------------------------------------------------
log_section "4. PostgreSQL Container"
# -----------------------------------------------------------------------------
PG_CONTAINER=$(docker ps -a --filter "name=postgres\|db\|pg" --format "{{.Names}}" | head -1)

if [ -n "$PG_CONTAINER" ]; then
    log_info "Container: $PG_CONTAINER"
    PG_STATUS=$(docker inspect -f '{{.State.Status}}' "$PG_CONTAINER" 2>/dev/null || echo "unknown")
    echo "Status: $PG_STATUS"

    if [ "$PG_STATUS" == "running" ]; then
        log_info "Testing DB connection..."
        docker exec "$PG_CONTAINER" pg_isready -U odoo 2>/dev/null && log_info "PostgreSQL OK" || log_error "PostgreSQL not ready"
    fi
else
    log_error "No PostgreSQL container found!"
fi

# -----------------------------------------------------------------------------
log_section "5. Network & Ports"
# -----------------------------------------------------------------------------
log_info "Listening ports:"
ss -tlnp 2>/dev/null | grep -E ':8069|:8072|:5432|:80|:443' || netstat -tlnp 2>/dev/null | grep -E ':8069|:8072|:5432|:80|:443' || echo "Could not check ports"

# -----------------------------------------------------------------------------
log_section "6. Nginx Status"
# -----------------------------------------------------------------------------
if systemctl is-active --quiet nginx 2>/dev/null; then
    log_info "Nginx: running"
    nginx -t 2>&1 || true
else
    log_warn "Nginx not running as systemd service, checking container..."
    NGINX_CONTAINER=$(docker ps -a --filter "name=nginx" --format "{{.Names}}" | head -1)
    if [ -n "$NGINX_CONTAINER" ]; then
        log_info "Nginx container: $NGINX_CONTAINER"
        docker inspect -f '{{.State.Status}}' "$NGINX_CONTAINER"
    else
        log_error "No Nginx found!"
    fi
fi

# -----------------------------------------------------------------------------
log_section "7. Local Health Checks"
# -----------------------------------------------------------------------------
log_info "Testing localhost:8069..."
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" --connect-timeout 5 http://localhost:8069/web/health 2>/dev/null || echo "000")
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" == "200" ]; then
    log_info "Odoo responding locally!"
else
    log_error "Odoo not responding on localhost:8069"

    log_warn "Checking if port 8069 is bound..."
    ss -tlnp | grep 8069 || echo "Port 8069 not listening"
fi

log_info "Testing localhost:8072 (longpolling)..."
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" --connect-timeout 5 http://localhost:8072/ 2>/dev/null || echo "000")
echo "HTTP Status: $HTTP_CODE"

# -----------------------------------------------------------------------------
log_section "8. Recent Odoo Logs"
# -----------------------------------------------------------------------------
if [ -n "$ODOO_CONTAINER" ]; then
    log_info "Last 30 lines:"
    docker logs "$ODOO_CONTAINER" --tail 30 2>&1 | grep -v "^$" || true
fi

# -----------------------------------------------------------------------------
log_section "9. SSL Certificate"
# -----------------------------------------------------------------------------
CERT_PATH="/etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem"
if [ -f "$CERT_PATH" ]; then
    EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_PATH" 2>/dev/null | cut -d= -f2)
    log_info "SSL Certificate expires: $EXPIRY"
else
    log_warn "SSL certificate not found at $CERT_PATH"
fi

# -----------------------------------------------------------------------------
log_section "10. Quick Fixes"
# -----------------------------------------------------------------------------
echo ""
echo "If Odoo is down, try:"
echo ""
echo "  # Restart containers"
echo "  cd $REPO_DIR/deploy"
echo "  docker compose -f docker-compose.prod.yml restart"
echo ""
echo "  # Full recreate"
echo "  docker compose -f docker-compose.prod.yml down"
echo "  docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "  # Check logs"
echo "  docker logs odoo-ce --tail 100 -f"
echo ""
echo "  # Restart nginx"
echo "  systemctl restart nginx"
echo ""

# -----------------------------------------------------------------------------
log_section "Summary"
# -----------------------------------------------------------------------------
echo ""
ODOO_OK=false
PG_OK=false
NGINX_OK=false

[ -n "$ODOO_CONTAINER" ] && [ "$(docker inspect -f '{{.State.Status}}' "$ODOO_CONTAINER" 2>/dev/null)" == "running" ] && ODOO_OK=true
[ -n "$PG_CONTAINER" ] && [ "$(docker inspect -f '{{.State.Status}}' "$PG_CONTAINER" 2>/dev/null)" == "running" ] && PG_OK=true
systemctl is-active --quiet nginx 2>/dev/null && NGINX_OK=true

echo "| Component  | Status |"
echo "|------------|--------|"
[ "$ODOO_OK" = true ] && echo "| Odoo       | OK     |" || echo "| Odoo       | DOWN   |"
[ "$PG_OK" = true ] && echo "| PostgreSQL | OK     |" || echo "| PostgreSQL | DOWN   |"
[ "$NGINX_OK" = true ] && echo "| Nginx      | OK     |" || echo "| Nginx      | DOWN   |"

echo ""
echo "============================================="
