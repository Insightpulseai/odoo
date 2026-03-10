#!/usr/bin/env bash
# =============================================================================
# Supabase Health Validation — Azure VM
# =============================================================================
# Checks all Supabase services for health. Returns exit code 1 if any fail.
# Designed to run locally on the VM or remotely via SSH.
#
# Usage:
#   ./health.sh                       # Check all services
#   ./health.sh --remote 1.2.3.4      # Check against remote IP
#   ./health.sh --json                # Output JSON for monitoring
#
# Exit codes:
#   0 = all healthy
#   1 = one or more services unhealthy
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPABASE_DIR="${SCRIPT_DIR}/.."
COMPOSE_FILE="${SUPABASE_DIR}/docker-compose.supabase.yml"
ENV_FILE="${SUPABASE_DIR}/.env.supabase"
HOST="localhost"
JSON_OUTPUT=false
FAILURES=0
TOTAL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote) HOST="$2"; shift 2 ;;
    --json)   JSON_OUTPUT=true; shift ;;
    *)        echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

TIMESTAMP=$(date -Iseconds)

# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------
check_http() {
  local name="$1" url="$2" expected="${3:-200}"
  TOTAL=$((TOTAL + 1))
  local status
  status=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

  if [[ "$status" =~ ^${expected}$ ]] || [[ "$status" =~ ^2[0-9][0-9]$ ]]; then
    if [[ "$JSON_OUTPUT" != "true" ]]; then
      echo "  [OK]    ${name}: HTTP ${status}"
    fi
    echo "${name}:ok:${status}" >> /tmp/supabase-health-$$
  else
    if [[ "$JSON_OUTPUT" != "true" ]]; then
      echo "  [FAIL]  ${name}: HTTP ${status} (expected ${expected})"
    fi
    echo "${name}:fail:${status}" >> /tmp/supabase-health-$$
    FAILURES=$((FAILURES + 1))
  fi
}

check_container() {
  local name="$1"
  TOTAL=$((TOTAL + 1))
  local state
  state=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
    ps --format json "$name" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Health','unknown'))" 2>/dev/null || echo "unknown")

  if [[ "$state" == "healthy" ]]; then
    if [[ "$JSON_OUTPUT" != "true" ]]; then
      echo "  [OK]    container/${name}: ${state}"
    fi
    echo "container/${name}:ok:${state}" >> /tmp/supabase-health-$$
  else
    if [[ "$JSON_OUTPUT" != "true" ]]; then
      echo "  [FAIL]  container/${name}: ${state}"
    fi
    echo "container/${name}:fail:${state}" >> /tmp/supabase-health-$$
    FAILURES=$((FAILURES + 1))
  fi
}

check_disk() {
  TOTAL=$((TOTAL + 1))
  local usage
  usage=$(df -h /opt/supabase 2>/dev/null | awk 'NR==2 {print $5}' | tr -d '%' || echo "0")

  if [[ "$usage" -lt 85 ]]; then
    if [[ "$JSON_OUTPUT" != "true" ]]; then
      echo "  [OK]    disk/data: ${usage}% used"
    fi
    echo "disk/data:ok:${usage}%" >> /tmp/supabase-health-$$
  else
    if [[ "$JSON_OUTPUT" != "true" ]]; then
      echo "  [WARN]  disk/data: ${usage}% used (>85% threshold)"
    fi
    echo "disk/data:warn:${usage}%" >> /tmp/supabase-health-$$
    if [[ "$usage" -ge 95 ]]; then
      FAILURES=$((FAILURES + 1))
    fi
  fi
}

check_postgres_connections() {
  TOTAL=$((TOTAL + 1))
  local conn_count max_conn
  conn_count=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
    exec -T db psql -U postgres -t -A -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null || echo "-1")
  max_conn=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
    exec -T db psql -U postgres -t -A -c "SHOW max_connections;" 2>/dev/null || echo "100")

  if [[ "$conn_count" == "-1" ]]; then
    if [[ "$JSON_OUTPUT" != "true" ]]; then
      echo "  [FAIL]  postgres/connections: cannot connect"
    fi
    echo "postgres/connections:fail:unreachable" >> /tmp/supabase-health-$$
    FAILURES=$((FAILURES + 1))
  else
    local pct=$((conn_count * 100 / max_conn))
    if [[ "$pct" -lt 80 ]]; then
      if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo "  [OK]    postgres/connections: ${conn_count}/${max_conn} (${pct}%)"
      fi
      echo "postgres/connections:ok:${conn_count}/${max_conn}" >> /tmp/supabase-health-$$
    else
      if [[ "$JSON_OUTPUT" != "true" ]]; then
        echo "  [WARN]  postgres/connections: ${conn_count}/${max_conn} (${pct}%)"
      fi
      echo "postgres/connections:warn:${conn_count}/${max_conn}" >> /tmp/supabase-health-$$
    fi
  fi
}

# ---------------------------------------------------------------------------
# Run checks
# ---------------------------------------------------------------------------
rm -f /tmp/supabase-health-$$

if [[ "$JSON_OUTPUT" != "true" ]]; then
  echo "Supabase Health Check — ${TIMESTAMP}"
  echo "Host: ${HOST}"
  echo "---"
  echo "HTTP endpoints:"
fi

BASE="http://${HOST}:8000"

check_http "kong/gateway"       "${BASE}/"
check_http "auth/health"        "${BASE}/auth/v1/health"
check_http "rest/ready"         "${BASE}/rest/v1/"
check_http "storage/status"     "${BASE}/storage/v1/status"

if [[ "$JSON_OUTPUT" != "true" ]]; then
  echo ""
  echo "Container health (docker):"
fi

if [[ "$HOST" == "localhost" ]] || [[ "$HOST" == "127.0.0.1" ]]; then
  check_container "db"
  check_container "kong"
  check_container "auth"
  check_container "rest"
  check_container "realtime"
  check_container "storage"
  check_container "analytics"

  if [[ "$JSON_OUTPUT" != "true" ]]; then
    echo ""
    echo "Resource checks:"
  fi

  check_disk
  check_postgres_connections
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
if [[ "$JSON_OUTPUT" == "true" ]]; then
  echo "{"
  echo "  \"timestamp\": \"${TIMESTAMP}\","
  echo "  \"host\": \"${HOST}\","
  echo "  \"total\": ${TOTAL},"
  echo "  \"failures\": ${FAILURES},"
  echo "  \"status\": \"$(if [[ $FAILURES -eq 0 ]]; then echo 'healthy'; else echo 'unhealthy'; fi)\","
  echo "  \"checks\": ["
  local first=true
  while IFS=: read -r name status detail; do
    if [[ "$first" != "true" ]]; then echo ","; fi
    echo -n "    {\"name\": \"${name}\", \"status\": \"${status}\", \"detail\": \"${detail}\"}"
    first=false
  done < /tmp/supabase-health-$$
  echo ""
  echo "  ]"
  echo "}"
else
  echo ""
  echo "---"
  if [[ "$FAILURES" -eq 0 ]]; then
    echo "Result: ALL HEALTHY (${TOTAL} checks passed)"
  else
    echo "Result: UNHEALTHY (${FAILURES}/${TOTAL} checks failed)"
  fi
fi

rm -f /tmp/supabase-health-$$

exit $FAILURES
