#!/usr/bin/env bash
# Verification script for OCA stack deployment
# Run after deploy to ensure everything is healthy
#
# Usage: ./oca-verify.sh [--json]
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed

set -euo pipefail

JSON_OUTPUT=false
[[ "${1:-}" == "--json" ]] && JSON_OUTPUT=true

# Colors (disabled for JSON output)
if [[ "$JSON_OUTPUT" == "false" ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' NC=''
fi

RESULTS=()
ERRORS=0

check() {
  local name="$1"
  local cmd="$2"
  local result
  local status

  if result=$(eval "$cmd" 2>&1); then
    status="pass"
    [[ "$JSON_OUTPUT" == "false" ]] && echo -e "${GREEN}✓${NC} $name"
  else
    status="fail"
    ERRORS=$((ERRORS + 1))
    [[ "$JSON_OUTPUT" == "false" ]] && echo -e "${RED}✗${NC} $name: $result"
  fi

  RESULTS+=("{\"name\":\"$name\",\"status\":\"$status\"}")
}

# -----------------------------------------
# Infrastructure Checks
# -----------------------------------------
[[ "$JSON_OUTPUT" == "false" ]] && echo -e "\n${YELLOW}=== Infrastructure ===${NC}"

check "Docker daemon" \
  "docker info >/dev/null 2>&1"

check "Docker Compose" \
  "docker compose version >/dev/null 2>&1"

check "PostgreSQL container running" \
  "docker compose ps --format json | jq -e '.[] | select(.Name | contains(\"db\")) | select(.State == \"running\")' >/dev/null"

check "Odoo container running" \
  "docker compose ps --format json | jq -e '.[] | select(.Name | contains(\"odoo\")) | select(.State == \"running\")' >/dev/null"

# -----------------------------------------
# Database Checks
# -----------------------------------------
[[ "$JSON_OUTPUT" == "false" ]] && echo -e "\n${YELLOW}=== Database ===${NC}"

check "PostgreSQL accepting connections" \
  "docker compose exec -T db pg_isready -U odoo -d odoo"

check "PostgreSQL version" \
  "docker compose exec -T db psql -U odoo -d odoo -c 'SELECT version();' -t | grep -q 'PostgreSQL'"

check "Odoo database exists" \
  "docker compose exec -T db psql -U odoo -d odoo -c '\\dt' 2>&1 | head -1"

# -----------------------------------------
# Application Checks
# -----------------------------------------
[[ "$JSON_OUTPUT" == "false" ]] && echo -e "\n${YELLOW}=== Application ===${NC}"

check "Odoo HTTP responding" \
  "curl -fsS --max-time 10 http://127.0.0.1:8069/web/login >/dev/null"

check "Odoo health endpoint" \
  "curl -fsS --max-time 10 http://127.0.0.1:8069/web/health >/dev/null"

check "Odoo logs (no critical errors)" \
  "[[ \$(docker compose logs --tail=100 odoo 2>&1 | grep -ciE 'critical|traceback|error' || true) -lt 5 ]]"

# -----------------------------------------
# OCA Module Checks
# -----------------------------------------
[[ "$JSON_OUTPUT" == "false" ]] && echo -e "\n${YELLOW}=== OCA Modules ===${NC}"

check "OCA addons directory exists" \
  "test -d addons/oca"

check "OCA lock file exists" \
  "test -f oca.lock"

check "OCA repos match lock" \
  "make -s verify 2>/dev/null || [[ ! -f oca.lock ]]"

# -----------------------------------------
# TLS/Proxy Checks (if Caddy is running)
# -----------------------------------------
if docker compose ps --format json 2>/dev/null | jq -e '.[] | select(.Name | contains("caddy"))' >/dev/null 2>&1; then
  [[ "$JSON_OUTPUT" == "false" ]] && echo -e "\n${YELLOW}=== TLS Proxy ===${NC}"

  check "Caddy container running" \
    "docker compose ps --format json | jq -e '.[] | select(.Name | contains(\"caddy\")) | select(.State == \"running\")' >/dev/null"

  check "HTTPS responding" \
    "curl -fsS --max-time 10 -k https://127.0.0.1/ >/dev/null 2>&1 || curl -fsS --max-time 10 http://127.0.0.1:80/health >/dev/null"
fi

# -----------------------------------------
# Summary
# -----------------------------------------
if [[ "$JSON_OUTPUT" == "true" ]]; then
  echo "{\"checks\":[$(IFS=,; echo "${RESULTS[*]}")],\"errors\":$ERRORS,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
else
  echo ""
  if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}=== ALL CHECKS PASSED ===${NC}"
  else
    echo -e "${RED}=== $ERRORS CHECK(S) FAILED ===${NC}"
  fi
fi

exit $ERRORS
