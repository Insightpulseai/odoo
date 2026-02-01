#!/bin/bash
# Diagnose and fix 502 Bad Gateway for Odoo production
# Usage: ./scripts/deploy/diagnose_502.sh [--fix]
set -euo pipefail

DEPLOY_DIR="${DEPLOY_DIR:-/opt/odoo-ce/deploy}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
FIX_MODE="${1:-}"

echo "=== Odoo 502 Diagnostics - $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="

cd "$DEPLOY_DIR" 2>/dev/null || {
    echo "[ERROR] Cannot access $DEPLOY_DIR"
    echo "Set DEPLOY_DIR to your deployment directory"
    exit 1
}

echo ""
echo "--- 1. Container Status ---"
docker compose -f "$COMPOSE_FILE" ps -a 2>/dev/null || docker-compose -f "$COMPOSE_FILE" ps -a

echo ""
echo "--- 2. Odoo Container Logs (last 50 lines) ---"
docker compose -f "$COMPOSE_FILE" logs --tail=50 odoo 2>/dev/null || \
    docker-compose -f "$COMPOSE_FILE" logs --tail=50 odoo 2>/dev/null || \
    docker logs odoo-ce --tail=50 2>/dev/null || \
    echo "[WARN] Cannot retrieve Odoo logs"

echo ""
echo "--- 3. Database Container Status ---"
docker compose -f "$COMPOSE_FILE" logs --tail=20 db 2>/dev/null || \
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 db 2>/dev/null || \
    echo "[INFO] Using external managed database (no local db container)"

echo ""
echo "--- 4. Port Binding Check ---"
echo "Listening on 8069:"
ss -tlnp | grep 8069 || netstat -tlnp | grep 8069 || echo "[WARN] Nothing bound to 8069"
echo ""
echo "Listening on 8072 (longpolling):"
ss -tlnp | grep 8072 || netstat -tlnp | grep 8072 || echo "[INFO] Longpolling port not bound (optional)"

echo ""
echo "--- 5. Nginx Upstream Check ---"
if command -v nginx &>/dev/null; then
    nginx -t 2>&1 || echo "[WARN] nginx config test failed"
fi
curl -sf http://127.0.0.1:8069/web/health && echo "[OK] Odoo health check passed" || echo "[FAIL] Odoo not responding on localhost:8069"

echo ""
echo "--- 6. Docker Network Inspection ---"
docker network ls | grep -E "(odoo|backend)" || echo "[INFO] No odoo network found"

echo ""
echo "--- 7. Resource Usage ---"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | head -10 || echo "[INFO] Stats unavailable"

echo ""
echo "--- 8. Disk Space ---"
df -h / | tail -1

# Fix mode
if [[ "$FIX_MODE" == "--fix" ]]; then
    echo ""
    echo "=== APPLYING FIX ==="

    echo "[1/4] Stopping containers..."
    docker compose -f "$COMPOSE_FILE" down 2>/dev/null || docker-compose -f "$COMPOSE_FILE" down

    echo "[2/4] Pruning stale containers/networks..."
    docker container prune -f
    docker network prune -f

    echo "[3/4] Starting stack..."
    docker compose -f "$COMPOSE_FILE" up -d 2>/dev/null || docker-compose -f "$COMPOSE_FILE" up -d

    echo "[4/4] Waiting for health check (120s max)..."
    for i in {1..24}; do
        if curl -sf http://127.0.0.1:8069/web/health >/dev/null 2>&1; then
            echo "[OK] Odoo is healthy after ${i}x5 seconds"
            break
        fi
        echo "  Waiting... ($i/24)"
        sleep 5
    done

    echo ""
    echo "--- Post-fix Verification ---"
    docker compose -f "$COMPOSE_FILE" ps
    curl -sf http://127.0.0.1:8069/web/health && echo "[OK] Health check passed" || echo "[FAIL] Still unhealthy"
fi

echo ""
echo "=== Diagnostics Complete ==="
echo "To apply automatic fix: $0 --fix"
