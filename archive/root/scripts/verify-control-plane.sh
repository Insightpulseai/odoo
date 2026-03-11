#!/usr/bin/env bash
# Verify Supabase Control Plane health
# Checks job queue, service health, and n8n connectivity
#
# Usage:
#   ./scripts/verify-control-plane.sh              # Run all checks
#   ./scripts/verify-control-plane.sh --json       # Output JSON
#   ./scripts/verify-control-plane.sh --alert      # Exit 1 if unhealthy

set -euo pipefail

# Configuration
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"
N8N_URL="${N8N_URL:-http://localhost:5678}"
JSON_OUTPUT=false
ALERT_MODE=false

# Parse args
for arg in "$@"; do
  case "$arg" in
    --json) JSON_OUTPUT=true ;;
    --alert) ALERT_MODE=true ;;
  esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Results
declare -A RESULTS

check() {
  local name="$1"
  local status="$2"
  local message="$3"

  RESULTS["$name"]="$status|$message"

  if [[ "$JSON_OUTPUT" == "false" ]]; then
    case "$status" in
      pass) echo -e "${GREEN}✓${NC} $name: $message" ;;
      warn) echo -e "${YELLOW}⚠${NC} $name: $message" ;;
      fail) echo -e "${RED}✗${NC} $name: $message" ;;
    esac
  fi
}

# -----------------------------------------
# Check Supabase connectivity
# -----------------------------------------
check_supabase() {
  if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_KEY" ]]; then
    check "supabase_config" "fail" "SUPABASE_URL or SUPABASE_KEY not set"
    return
  fi

  local response
  response=$(curl -s -w "\n%{http_code}" -H "apikey: $SUPABASE_KEY" \
    "${SUPABASE_URL}/rest/v1/" 2>/dev/null || echo -e "\n000")

  local http_code
  http_code=$(echo "$response" | tail -1)

  if [[ "$http_code" == "200" ]]; then
    check "supabase_api" "pass" "PostgREST reachable (HTTP $http_code)"
  else
    check "supabase_api" "fail" "PostgREST unreachable (HTTP $http_code)"
  fi
}

# -----------------------------------------
# Check job queue health
# -----------------------------------------
check_job_queue() {
  if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_KEY" ]]; then
    return
  fi

  local response
  response=$(curl -s -H "apikey: $SUPABASE_KEY" -H "Authorization: Bearer $SUPABASE_KEY" \
    "${SUPABASE_URL}/rest/v1/rpc/get_queue_depth" 2>/dev/null || echo "[]")

  if [[ "$response" == "[]" || -z "$response" ]]; then
    check "job_queue" "pass" "Queue empty or function not available"
    return
  fi

  local queued processing dlq
  queued=$(echo "$response" | jq '[.[].queued // 0] | add // 0' 2>/dev/null || echo "0")
  processing=$(echo "$response" | jq '[.[].processing // 0] | add // 0' 2>/dev/null || echo "0")
  dlq=$(echo "$response" | jq '[.[].dlq_unresolved // 0] | add // 0' 2>/dev/null || echo "0")

  if [[ "$dlq" -gt 10 ]]; then
    check "job_queue_dlq" "fail" "Dead letter queue critical: $dlq unresolved"
  elif [[ "$dlq" -gt 0 ]]; then
    check "job_queue_dlq" "warn" "Dead letter queue: $dlq unresolved"
  else
    check "job_queue_dlq" "pass" "No unresolved DLQ items"
  fi

  if [[ "$queued" -gt 100 ]]; then
    check "job_queue_depth" "fail" "Queue depth critical: $queued queued"
  elif [[ "$queued" -gt 50 ]]; then
    check "job_queue_depth" "warn" "Queue depth elevated: $queued queued"
  else
    check "job_queue_depth" "pass" "Queue depth normal: $queued queued, $processing processing"
  fi
}

# -----------------------------------------
# Check service health summary
# -----------------------------------------
check_services() {
  if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_KEY" ]]; then
    return
  fi

  local response
  response=$(curl -s -H "apikey: $SUPABASE_KEY" -H "Authorization: Bearer $SUPABASE_KEY" \
    "${SUPABASE_URL}/rest/v1/rpc/get_health_summary" 2>/dev/null || echo "{}")

  if [[ -z "$response" || "$response" == "{}" || "$response" == "null" ]]; then
    check "services_health" "warn" "Health summary not available"
    return
  fi

  local overall healthy unhealthy offline
  overall=$(echo "$response" | jq -r '.[0].overall_status // "unknown"' 2>/dev/null || echo "unknown")
  healthy=$(echo "$response" | jq -r '.[0].healthy_count // 0' 2>/dev/null || echo "0")
  unhealthy=$(echo "$response" | jq -r '.[0].unhealthy_count // 0' 2>/dev/null || echo "0")
  offline=$(echo "$response" | jq -r '.[0].offline_count // 0' 2>/dev/null || echo "0")

  case "$overall" in
    healthy)
      check "services_health" "pass" "All services healthy ($healthy total)"
      ;;
    degraded)
      check "services_health" "warn" "Some services degraded ($unhealthy unhealthy)"
      ;;
    unhealthy)
      check "services_health" "fail" "Services unhealthy: $unhealthy unhealthy, $offline offline"
      ;;
    *)
      check "services_health" "warn" "Unknown status: $overall"
      ;;
  esac
}

# -----------------------------------------
# Check n8n connectivity
# -----------------------------------------
check_n8n() {
  local response
  response=$(curl -s -w "\n%{http_code}" "${N8N_URL}/healthz" 2>/dev/null || echo -e "\n000")

  local http_code
  http_code=$(echo "$response" | tail -1)

  if [[ "$http_code" == "200" ]]; then
    check "n8n_health" "pass" "n8n reachable at ${N8N_URL}"
  else
    check "n8n_health" "fail" "n8n unreachable (HTTP $http_code)"
  fi
}

# -----------------------------------------
# Output JSON
# -----------------------------------------
output_json() {
  echo "{"
  echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"checks\": {"

  local first=true
  for name in "${!RESULTS[@]}"; do
    local value="${RESULTS[$name]}"
    local status="${value%%|*}"
    local message="${value#*|}"

    [[ "$first" == "false" ]] && echo ","
    first=false

    echo -n "    \"$name\": {\"status\": \"$status\", \"message\": \"$message\"}"
  done

  echo ""
  echo "  },"

  # Overall status
  local overall="pass"
  for name in "${!RESULTS[@]}"; do
    local status="${RESULTS[$name]%%|*}"
    if [[ "$status" == "fail" ]]; then
      overall="fail"
      break
    elif [[ "$status" == "warn" && "$overall" != "fail" ]]; then
      overall="warn"
    fi
  done

  echo "  \"overall\": \"$overall\""
  echo "}"
}

# -----------------------------------------
# Main
# -----------------------------------------
main() {
  if [[ "$JSON_OUTPUT" == "false" ]]; then
    echo "Control Plane Health Check"
    echo "=========================="
    echo ""
  fi

  check_supabase
  check_job_queue
  check_services
  check_n8n

  if [[ "$JSON_OUTPUT" == "true" ]]; then
    output_json
  else
    echo ""
    echo "=========================="
  fi

  # Determine exit code
  if [[ "$ALERT_MODE" == "true" ]]; then
    for name in "${!RESULTS[@]}"; do
      local status="${RESULTS[$name]%%|*}"
      if [[ "$status" == "fail" ]]; then
        exit 1
      fi
    done
  fi
}

main
