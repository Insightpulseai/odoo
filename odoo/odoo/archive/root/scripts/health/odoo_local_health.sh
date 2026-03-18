#!/usr/bin/env bash
#
# Odoo Local Health Check Script
# Purpose: Deterministic PASS/FAIL health checks for Colima + Odoo development environment
# Usage: ./scripts/health/odoo_local_health.sh [--evidence]
#
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Evidence logging flag
GENERATE_EVIDENCE=false
if [[ "${1:-}" == "--evidence" ]]; then
  GENERATE_EVIDENCE=true
fi

# Evidence directory
TIMESTAMP=$(date +"%Y-%m-%d-%H%M")
EVIDENCE_DIR="../../docs/evidence/local/${TIMESTAMP}"

# Counters
CRITICAL_FAILURES=0
WARNINGS=0

# Evidence log
EVIDENCE_LOG=""

log_pass() {
  echo -e "${GREEN}✅ PASS:${NC} $1"
  EVIDENCE_LOG="${EVIDENCE_LOG}✅ PASS: $1\n"
}

log_fail() {
  echo -e "${RED}❌ FAIL:${NC} $1"
  EVIDENCE_LOG="${EVIDENCE_LOG}❌ FAIL: $1\n"
  ((CRITICAL_FAILURES++))
}

log_warn() {
  echo -e "${YELLOW}⚠️  WARN:${NC} $1"
  EVIDENCE_LOG="${EVIDENCE_LOG}⚠️  WARN: $1\n"
  ((WARNINGS++))
}

log_info() {
  echo -e "ℹ️  INFO: $1"
  EVIDENCE_LOG="${EVIDENCE_LOG}ℹ️  INFO: $1\n"
}

# ============================================================================
# CRITICAL CHECKS (Container Network Health)
# ============================================================================

echo ""
echo "================================"
echo "Container Network Health Checks"
echo "================================"

# Check 1: Odoo HTTP responds on container network
log_info "Checking Odoo HTTP on container network..."
if docker exec odoo-core curl -sf http://localhost:8069/web/health > /dev/null 2>&1; then
  log_pass "Odoo HTTP reachable inside container (http://localhost:8069/web/health)"
else
  log_fail "Odoo HTTP unreachable inside container (http://localhost:8069/web/health)"
fi

# Check 2: DB reachable from Odoo container
log_info "Checking PostgreSQL from Odoo container..."
if docker exec odoo-core pg_isready -h db -p 5432 -U odoo > /dev/null 2>&1; then
  log_pass "PostgreSQL reachable from Odoo container (db:5432)"
else
  log_fail "PostgreSQL unreachable from Odoo container (db:5432)"
fi

# Check 3: Redis reachable from Odoo container
log_info "Checking Redis from Odoo container..."
# Use Python to test Redis connection (redis-cli may not be available in Odoo container)
if docker exec odoo-core python3 -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('redis', 6379)); s.close()" 2>/dev/null; then
  log_pass "Redis reachable from Odoo container (redis:6379)"
else
  log_fail "Redis unreachable from Odoo container (redis:6379)"
fi

# ============================================================================
# CRITICAL CHECKS (Container Status)
# ============================================================================

echo ""
echo "======================"
echo "Container Status Checks"
echo "======================"

# Check 4: All 3 containers running
log_info "Checking container count..."
CONTAINER_COUNT=$(docker ps --filter name=odoo --filter status=running | grep -c odoo || true)
if [[ "${CONTAINER_COUNT}" -eq 3 ]]; then
  log_pass "All 3 Odoo containers running (odoo-core, odoo-db, odoo-redis)"
else
  log_fail "Expected 3 Odoo containers, found ${CONTAINER_COUNT}"
fi

# Check 5: All containers healthy (if health checks defined)
log_info "Checking container health status..."
UNHEALTHY_COUNT=$(docker ps --filter name=odoo --format '{{.Status}}' | grep -v "healthy" | wc -l || true)
if [[ "${UNHEALTHY_COUNT}" -eq 0 ]]; then
  log_pass "All Odoo containers healthy"
else
  log_warn "Some containers may not have health checks or are unhealthy"
fi

# ============================================================================
# CRITICAL CHECKS (Port Forwarding)
# ============================================================================

echo ""
echo "========================"
echo "Port Forwarding Checks"
echo "========================"

# Check 6: TCP port 8069 listening on host
log_info "Checking TCP port 8069..."
if nc -z localhost 8069 2>/dev/null; then
  log_pass "TCP port 8069 listening on host"
else
  log_fail "TCP port 8069 NOT listening on host"
fi

# Check 7: TCP port 8072 listening on host
log_info "Checking TCP port 8072..."
if nc -z localhost 8072 2>/dev/null; then
  log_pass "TCP port 8072 listening on host"
else
  log_fail "TCP port 8072 NOT listening on host"
fi

# ============================================================================
# WARNING CHECKS (Host HTTP Response)
# ============================================================================

echo ""
echo "====================="
echo "Host HTTP Checks"
echo "====================="

# Check 8: Host HTTP response (tolerant of "Empty reply" quirk)
log_info "Checking host HTTP response (curl from macOS host)..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -m 5 http://localhost:8069/web/health 2>&1 || echo "ERROR")

if [[ "${HTTP_STATUS}" == "200" ]]; then
  log_pass "Host HTTP responds correctly (http://localhost:8069/web/health → HTTP ${HTTP_STATUS})"
elif [[ "${HTTP_STATUS}" == "ERROR" ]]; then
  # Check if it's the "Empty reply" quirk
  HTTP_ERROR=$(curl -sf -m 5 http://localhost:8069/web/health 2>&1 || true)
  if echo "${HTTP_ERROR}" | grep -qi "empty reply"; then
    # If container-network health passed, this is acceptable
    if [[ "${CRITICAL_FAILURES}" -eq 0 ]]; then
      log_warn "Host curl shows 'Empty reply' (SSH tunnel quirk, non-blocking if container health passes)"
    else
      log_fail "Host curl shows 'Empty reply' AND container health failed"
    fi
  else
    log_warn "Host HTTP curl failed: ${HTTP_ERROR:-Connection failed}"
  fi
else
  log_warn "Host HTTP returned unexpected status: ${HTTP_STATUS}"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "================================"
echo "Health Check Summary"
echo "================================"
echo "Critical Failures: ${CRITICAL_FAILURES}"
echo "Warnings: ${WARNINGS}"
echo ""

# Generate evidence bundle if requested
if [[ "${GENERATE_EVIDENCE}" == "true" ]]; then
  echo "Generating evidence bundle..."
  mkdir -p "${EVIDENCE_DIR}"

  # Container status
  docker ps --filter name=odoo > "${EVIDENCE_DIR}/container_status.txt"

  # Odoo logs (last 200 lines)
  docker logs odoo-core --tail 200 > "${EVIDENCE_DIR}/odoo_logs.txt" 2>&1 || true

  # Database connectivity
  docker exec odoo-core pg_isready -h db -p 5432 -U odoo > "${EVIDENCE_DIR}/db_connectivity.txt" 2>&1 || true

  # Port forwarding status
  {
    lsof -i :8069 2>&1 || true
    lsof -i :8072 2>&1 || true
    netstat -an | grep -E "8069|8072" || true
  } > "${EVIDENCE_DIR}/port_forwarding.txt"

  # Colima info
  {
    colima version || true
    colima status || true
    colima list || true
  } > "${EVIDENCE_DIR}/colima_info.txt"

  # System info
  {
    sw_vers || true
    docker version || true
    docker compose version || true
  } > "${EVIDENCE_DIR}/system_info.txt"

  # Health check results
  echo -e "${EVIDENCE_LOG}" > "${EVIDENCE_DIR}/health_check_results.txt"

  echo "Evidence bundle created at: ${EVIDENCE_DIR}"
  echo ""
fi

# Exit code
if [[ "${CRITICAL_FAILURES}" -gt 0 ]]; then
  echo -e "${RED}❌ HEALTH CHECK FAILED${NC} (${CRITICAL_FAILURES} critical failures)"
  exit 1
else
  if [[ "${WARNINGS}" -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  HEALTH CHECK PASSED WITH WARNINGS${NC} (${WARNINGS} warnings)"
  else
    echo -e "${GREEN}✅ HEALTH CHECK PASSED${NC}"
  fi
  exit 0
fi
