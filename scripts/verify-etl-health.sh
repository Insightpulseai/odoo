#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# ETL Health Check Script
# ═══════════════════════════════════════════════════════════════════════════════
# Purpose: Verify supabase/etl container health and replication status
# Usage: ./scripts/verify-etl-health.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ETL_DIR="${ETL_DIR:-etl/odoo_to_supabase}"
COMPOSE_FILE="${ETL_DIR}/docker-compose.yml"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}ETL Health Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if ETL directory exists
if [ ! -d "$ETL_DIR" ]; then
    echo -e "${RED}✗ ETL directory not found: $ETL_DIR${NC}"
    exit 1
fi

cd "$ETL_DIR"

# 1. Check Docker Compose services
echo -e "${YELLOW}1. Docker Compose Services${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
if [ -f "$COMPOSE_FILE" ]; then
    docker compose ps
    echo ""
else
    echo -e "${RED}✗ docker-compose.yml not found${NC}"
    exit 1
fi

# 2. Check ETL container status
echo -e "${YELLOW}2. ETL Container Status${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
ETL_CONTAINER=$(docker compose ps -q etl 2>/dev/null || echo "")
if [ -n "$ETL_CONTAINER" ]; then
    ETL_STATUS=$(docker inspect --format='{{.State.Status}}' "$ETL_CONTAINER")
    if [ "$ETL_STATUS" = "running" ]; then
        echo -e "${GREEN}✓ ETL container is running${NC}"

        # Get container uptime
        STARTED=$(docker inspect --format='{{.State.StartedAt}}' "$ETL_CONTAINER")
        echo "  Started: $STARTED"

        # Get resource usage
        STATS=$(docker stats --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" "$ETL_CONTAINER" | tail -n 1)
        echo "  Resources: $STATS"
    else
        echo -e "${RED}✗ ETL container is not running (status: $ETL_STATUS)${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ ETL container not found${NC}"
    exit 1
fi
echo ""

# 3. Check ETL logs for errors
echo -e "${YELLOW}3. ETL Logs (last 20 lines)${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
docker compose logs --tail=20 etl
echo ""

# 4. Check ETL metrics endpoint
echo -e "${YELLOW}4. ETL Metrics Endpoint${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
METRICS_PORT=${METRICS_PORT:-9090}
if curl -sf "http://localhost:${METRICS_PORT}/metrics" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Metrics endpoint is responding${NC}"

    # Extract key metrics
    METRICS=$(curl -s "http://localhost:${METRICS_PORT}/metrics")

    # Records processed
    RECORDS_PROCESSED=$(echo "$METRICS" | grep 'etl_records_processed_total' | tail -n 1 | awk '{print $2}')
    echo "  Records processed: ${RECORDS_PROCESSED:-N/A}"

    # Records failed
    RECORDS_FAILED=$(echo "$METRICS" | grep 'etl_records_failed_total' | tail -n 1 | awk '{print $2}')
    echo "  Records failed: ${RECORDS_FAILED:-N/A}"

    # Replication lag
    LAG=$(echo "$METRICS" | grep 'etl_lag_seconds' | tail -n 1 | awk '{print $2}')
    if [ -n "$LAG" ]; then
        if (( $(echo "$LAG > 60" | bc -l) )); then
            echo -e "  ${RED}⚠ Replication lag: ${LAG}s (exceeds 60s threshold)${NC}"
        else
            echo -e "  ${GREEN}✓ Replication lag: ${LAG}s${NC}"
        fi
    else
        echo "  Replication lag: N/A"
    fi
else
    echo -e "${RED}✗ Metrics endpoint not responding on port ${METRICS_PORT}${NC}"
fi
echo ""

# 5. Check Prometheus monitoring (if enabled)
echo -e "${YELLOW}5. Prometheus Monitoring${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
PROMETHEUS_CONTAINER=$(docker compose ps -q prometheus 2>/dev/null || echo "")
if [ -n "$PROMETHEUS_CONTAINER" ]; then
    PROM_STATUS=$(docker inspect --format='{{.State.Status}}' "$PROMETHEUS_CONTAINER")
    if [ "$PROM_STATUS" = "running" ]; then
        echo -e "${GREEN}✓ Prometheus is running${NC}"
        PROMETHEUS_PORT=${PROMETHEUS_PORT:-9091}
        echo "  URL: http://localhost:${PROMETHEUS_PORT}"
    else
        echo -e "${YELLOW}⚠ Prometheus is not running${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Prometheus container not found${NC}"
fi
echo ""

# 6. Check .env file exists
echo -e "${YELLOW}6. Configuration Check${NC}"
echo "───────────────────────────────────────────────────────────────────────────────"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"

    # Verify required variables (without exposing values)
    REQUIRED_VARS=(
        "ODOO_DB_HOST"
        "ODOO_DB_PASSWORD"
        "SUPABASE_SERVICE_ROLE_KEY"
    )

    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${VAR}=" .env; then
            echo -e "  ${GREEN}✓ $VAR is set${NC}"
        else
            echo -e "  ${RED}✗ $VAR is missing${NC}"
        fi
    done
else
    echo -e "${RED}✗ .env file not found (copy from .env.example)${NC}"
fi
echo ""

# 7. Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Health Check Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$ETL_STATUS" = "running" ] && curl -sf "http://localhost:${METRICS_PORT}/metrics" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ ETL pipeline is healthy${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run SQL verification: psql \"\$SUPABASE_URL\" -f ../scripts/verify-etl-replication.sql"
    echo "  2. Check Prometheus: open http://localhost:${PROMETHEUS_PORT}"
    echo "  3. View live logs: docker compose logs -f etl"
    exit 0
else
    echo -e "${RED}✗ ETL pipeline has issues${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker compose logs etl"
    echo "  2. Verify .env configuration"
    echo "  3. Restart services: docker compose restart"
    exit 1
fi
