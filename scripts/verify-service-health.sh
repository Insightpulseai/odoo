#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Service Health Check — Origin + Edge
# =============================================================================
# Two modes:
#   origin — curl localhost ports (run from DO droplet, proves backend health)
#   edge   — curl public FQDNs with WAF bypass headers (run from CI/external)
#
# SSOT: infra/dns/subdomain-registry.yaml
# Exit code: 0 = all pass, 1 = at least one failure
# =============================================================================

DOMAIN="insightpulseai.com"
TIMEOUT=15
PASS=0
FAIL=0
MODE="${MODE:-all}"                            # origin | edge | all
SCOPE="${SCOPE:-production}"                   # production | staging | all
HEALTHCHECK_TOKEN="${HEALTHCHECK_TOKEN:-}"
HEALTHCHECK_UA="${HEALTHCHECK_UA:-healthcheck/prod}"
JSON_OUTPUT=false
QUIET=false

# ─── Service registry ────────────────────────────────────────────────────────
# Format: name|origin_port|health_path|edge_fqdn
# origin URL = http://127.0.0.1:<port><path>
# edge   URL = https://<fqdn><path>
PROD_SERVICES=(
  "erp|8069|/web/health|erp.${DOMAIN}"
  "n8n|5678|/healthz|n8n.${DOMAIN}"
  "ocr|8080|/health|ocr.${DOMAIN}"
  "auth|3000|/.well-known/openid-configuration|auth.${DOMAIN}"
  "superset|8088|/health|superset.${DOMAIN}"
  "mcp|-|/healthz|mcp.${DOMAIN}"
)

STAGING_SERVICES=(
  "stage-erp|8069|/web/health|stage-erp.${DOMAIN}"
  "stage-n8n|5678|/healthz|stage-n8n.${DOMAIN}"
  "stage-ocr|8080|/health|stage-ocr.${DOMAIN}"
  "stage-auth|3000|/.well-known/openid-configuration|stage-auth.${DOMAIN}"
  "stage-superset|8088|/health|stage-superset.${DOMAIN}"
  "stage-mcp|-|/healthz|stage-mcp.${DOMAIN}"
  "stage-api|8000|/api/health|stage-api.${DOMAIN}"
)

# ─── Argument parsing ─────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Modes (where to probe):
  --mode origin   Curl localhost ports (run on droplet)
  --mode edge     Curl public domains with WAF bypass headers (run in CI)
  --mode all      Both origin and edge (default)

Scope (which services):
  --production    Production services only (default)
  --staging       Staging services only
  --all           All active services

Output:
  --json          Machine-readable JSON
  --quiet         Summary only

Environment variables:
  HEALTHCHECK_TOKEN   Shared secret for X-Healthcheck-Token header (edge mode)
  HEALTHCHECK_UA      User-Agent string (default: healthcheck/prod)
  MODE                Same as --mode
  SCOPE               Same as --production/--staging/--all
EOF
  exit 0
}

for arg in "$@"; do
  case "$arg" in
    --mode)        shift_next=mode ;;
    origin|edge|all)
      if [[ "${shift_next:-}" == "mode" ]]; then MODE="$arg"; shift_next=""; fi ;;
    --production)  SCOPE="production" ;;
    --staging)     SCOPE="staging" ;;
    --all)         SCOPE="all" ;;
    --json)        JSON_OUTPUT=true ;;
    --quiet)       QUIET=true ;;
    --help|-h)     usage ;;
  esac
done
# Handle --mode=value syntax
for arg in "$@"; do
  case "$arg" in
    --mode=*) MODE="${arg#--mode=}" ;;
  esac
done

# ─── JSON accumulator ─────────────────────────────────────────────────────────
JSON_RESULTS="[]"

json_append() {
  local service="$1" url="$2" probe="$3" status="$4" latency="$5" result="$6"
  JSON_RESULTS=$(printf '%s' "$JSON_RESULTS" | python3 -c "
import sys, json
arr = json.load(sys.stdin)
arr.append({
  'service': '''$service''',
  'url': '''$url''',
  'probe': '''$probe''',
  'status_code': '''$status''',
  'latency_s': '''$latency''',
  'result': '''$result'''
})
print(json.dumps(arr))
" 2>/dev/null || echo "$JSON_RESULTS")
}

# ─── Curl wrappers ────────────────────────────────────────────────────────────
timestamp() { date -u '+%Y-%m-%d %H:%M:%S UTC'; }

curl_origin() {
  local url="$1"
  curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000"
}

curl_origin_latency() {
  local url="$1"
  curl -s -o /dev/null -w "%{time_total}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "0"
}

curl_edge() {
  local url="$1"
  local -a headers=(-H "User-Agent: ${HEALTHCHECK_UA}")
  if [[ -n "$HEALTHCHECK_TOKEN" ]]; then
    headers+=(-H "X-Healthcheck-Token: ${HEALTHCHECK_TOKEN}")
  fi
  curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "${headers[@]}" "$url" 2>/dev/null || echo "000"
}

curl_edge_latency() {
  local url="$1"
  local -a headers=(-H "User-Agent: ${HEALTHCHECK_UA}")
  if [[ -n "$HEALTHCHECK_TOKEN" ]]; then
    headers+=(-H "X-Healthcheck-Token: ${HEALTHCHECK_TOKEN}")
  fi
  curl -s -o /dev/null -w "%{time_total}" --max-time "$TIMEOUT" "${headers[@]}" "$url" 2>/dev/null || echo "0"
}

# ─── Check dispatcher ─────────────────────────────────────────────────────────
classify() {
  local status="$1"
  case "$status" in
    200|301|302|303) echo "pass" ;;
    000)             echo "timeout" ;;
    *)               echo "fail" ;;
  esac
}

emit() {
  local service="$1" url="$2" probe="$3" status="$4" latency="$5" result="$6"

  if $JSON_OUTPUT; then
    json_append "$service" "$url" "$probe" "$status" "$latency" "$result"
  fi

  if ! $QUIET && ! $JSON_OUTPUT; then
    local tag="[$probe]"
    case "$result" in
      pass)    printf "  ✅ %-15s %-8s %-50s %s (%ss)\n" "$service" "$tag" "$url" "$status" "$latency" ;;
      timeout) printf "  ❌ %-15s %-8s %-50s TIMEOUT\n"  "$service" "$tag" "$url" ;;
      *)       printf "  ❌ %-15s %-8s %-50s %s\n"       "$service" "$tag" "$url" "$status" ;;
    esac
  fi

  case "$result" in
    pass) ((PASS++)) ;;
    *)    ((FAIL++)) ;;
  esac
}

check_service() {
  local entry="$1"
  IFS='|' read -r name port path fqdn <<< "$entry"

  # Origin probe
  if [[ "$MODE" == "origin" || "$MODE" == "all" ]]; then
    if [[ "$port" != "-" ]]; then
      local origin_url="http://127.0.0.1:${port}${path}"
      local status latency result
      status=$(curl_origin "$origin_url")
      latency=$(curl_origin_latency "$origin_url")
      result=$(classify "$status")
      emit "$name" "$origin_url" "origin" "$status" "$latency" "$result"
    fi
  fi

  # Edge probe
  if [[ "$MODE" == "edge" || "$MODE" == "all" ]]; then
    local edge_url="https://${fqdn}${path}"
    local status latency result
    status=$(curl_edge "$edge_url")
    latency=$(curl_edge_latency "$edge_url")
    result=$(classify "$status")
    emit "$name" "$edge_url" "edge" "$status" "$latency" "$result"
  fi
}

# ─── Run ──────────────────────────────────────────────────────────────────────
header() {
  if ! $QUIET && ! $JSON_OUTPUT; then
    echo "=============================================="
    echo "  SERVICE HEALTH CHECK — ${DOMAIN}"
    echo "  Mode: ${MODE} | Scope: ${SCOPE} | $(timestamp)"
    if [[ "$MODE" == "edge" || "$MODE" == "all" ]]; then
      echo "  UA: ${HEALTHCHECK_UA}"
      echo "  Token: ${HEALTHCHECK_TOKEN:+set}${HEALTHCHECK_TOKEN:-NOT SET (expect 403)}"
    fi
    echo "=============================================="
    echo ""
  fi
}

run_checks() {
  local label="$1"
  shift
  local services=("$@")

  if ! $QUIET && ! $JSON_OUTPUT; then
    echo "── ${label} ──"
  fi

  for entry in "${services[@]}"; do
    check_service "$entry"
  done

  if ! $QUIET && ! $JSON_OUTPUT; then
    echo ""
  fi
}

header

case "$SCOPE" in
  production)
    run_checks "Production" "${PROD_SERVICES[@]}"
    ;;
  staging)
    run_checks "Staging" "${STAGING_SERVICES[@]}"
    ;;
  all)
    run_checks "Production" "${PROD_SERVICES[@]}"
    run_checks "Staging" "${STAGING_SERVICES[@]}"
    ;;
esac

# ─── Summary ──────────────────────────────────────────────────────────────────
total=$((PASS + FAIL))

if $JSON_OUTPUT; then
  python3 -c "
import json
results = json.loads('''${JSON_RESULTS}''')
print(json.dumps({
  'timestamp': '$(timestamp)',
  'mode': '${MODE}',
  'scope': '${SCOPE}',
  'total': ${total},
  'pass': ${PASS},
  'fail': ${FAIL},
  'status': 'healthy' if ${FAIL} == 0 else 'degraded',
  'services': results
}, indent=2))
"
else
  echo "=============================================="
  echo "  SUMMARY"
  echo "  Pass: ${PASS} | Fail: ${FAIL} | Total: ${total}"
  if [[ $FAIL -eq 0 ]]; then
    echo "  Status: ALL HEALTHY"
  else
    echo "  Status: DEGRADED (${FAIL} failures)"
  fi
  echo "=============================================="
fi

[[ $FAIL -eq 0 ]]
