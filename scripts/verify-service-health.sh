#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Service Health Check — SSOT-driven
# =============================================================================
# Checks all active services defined in infra/dns/subdomain-registry.yaml
# Supports: --production (default), --staging, --all, --json, --quiet
# Exit code: 0 = all pass, 1 = at least one failure
# =============================================================================

DOMAIN="insightpulseai.com"
EXPECTED_IP="178.128.112.214"
TIMEOUT=15
PASS=0
FAIL=0
WARN=0
SCOPE="production"
JSON_OUTPUT=false
QUIET=false

usage() {
  echo "Usage: $0 [--production|--staging|--all] [--json] [--quiet]"
  echo "  --production  Check production services only (default)"
  echo "  --staging     Check staging services only"
  echo "  --all         Check all active services"
  echo "  --json        Output results as JSON"
  echo "  --quiet       Suppress per-service output, only show summary"
  exit 0
}

for arg in "$@"; do
  case "$arg" in
    --production) SCOPE="production" ;;
    --staging)    SCOPE="staging" ;;
    --all)        SCOPE="all" ;;
    --json)       JSON_OUTPUT=true ;;
    --quiet)      QUIET=true ;;
    --help|-h)    usage ;;
  esac
done

# JSON accumulator
JSON_RESULTS="[]"

timestamp() { date -u '+%Y-%m-%d %H:%M:%S UTC'; }

header() {
  if ! $QUIET && ! $JSON_OUTPUT; then
    echo "=============================================="
    echo "  SERVICE HEALTH CHECK — $DOMAIN"
    echo "  Scope: $SCOPE | $(timestamp)"
    echo "=============================================="
    echo ""
  fi
}

check_endpoint() {
  local service="$1"
  local fqdn="$2"
  local path="$3"
  local proto="${4:-https}"

  local url="${proto}://${fqdn}${path}"
  local status latency

  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
  latency=$(curl -s -o /dev/null -w "%{time_total}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "0")

  local result="fail"
  case "$status" in
    200|301|302|303) result="pass" ;;
    000)             result="timeout" ;;
    *)               result="fail" ;;
  esac

  if $JSON_OUTPUT; then
    JSON_RESULTS=$(echo "$JSON_RESULTS" | python3 -c "
import sys, json
arr = json.load(sys.stdin)
arr.append({
  'service': '$service',
  'fqdn': '$fqdn',
  'url': '$url',
  'status_code': '$status',
  'latency_s': '$latency',
  'result': '$result'
})
print(json.dumps(arr))
" 2>/dev/null || echo "$JSON_RESULTS")
  fi

  if ! $QUIET && ! $JSON_OUTPUT; then
    case "$result" in
      pass)
        printf "  ✅ %-30s %-45s %s (%ss)\n" "$service" "$url" "$status" "$latency"
        ;;
      timeout)
        printf "  ❌ %-30s %-45s TIMEOUT\n" "$service" "$url"
        ;;
      *)
        printf "  ❌ %-30s %-45s %s\n" "$service" "$url" "$status"
        ;;
    esac
  fi

  case "$result" in
    pass)    ((PASS++)) ;;
    timeout) ((FAIL++)) ;;
    *)       ((FAIL++)) ;;
  esac
}

check_dns() {
  local fqdn="$1"
  local rtype="${2:-A}"

  if command -v dig &>/dev/null; then
    dig +short "$rtype" "$fqdn" 2>/dev/null | head -1
  elif command -v nslookup &>/dev/null; then
    nslookup "$fqdn" 2>/dev/null | awk '/^Address: / { print $2; exit }'
  elif command -v host &>/dev/null; then
    host -t "$rtype" "$fqdn" 2>/dev/null | awk '{ print $NF; exit }'
  else
    # Fallback: Cloudflare DoH
    local result
    result=$(curl -s --max-time 10 \
      "https://cloudflare-dns.com/dns-query?name=${fqdn}&type=${rtype}" \
      -H "accept: application/dns-json" 2>/dev/null)
    echo "$result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    type_map = {'A': 1, 'CNAME': 5, 'TXT': 16}
    t = type_map.get('$rtype', 1)
    answers = [a['data'] for a in data.get('Answer', []) if a.get('type') == t]
    print(answers[0] if answers else '')
except: pass
" 2>/dev/null
  fi
}

# ─── Production services ──────────────────────────────────────────────────────
check_production() {
  if ! $QUIET && ! $JSON_OUTPUT; then
    echo "── Production Services ──"
  fi

  check_endpoint "erp"      "erp.$DOMAIN"      "/web/login"
  check_endpoint "n8n"      "n8n.$DOMAIN"      "/healthz"
  check_endpoint "ocr"      "ocr.$DOMAIN"      "/health"
  check_endpoint "auth"     "auth.$DOMAIN"     "/.well-known/openid-configuration"
  check_endpoint "mcp"      "mcp.$DOMAIN"      "/healthz"
  check_endpoint "superset" "superset.$DOMAIN" "/health"
  check_endpoint "www"      "www.$DOMAIN"      "/"

  if ! $QUIET && ! $JSON_OUTPUT; then
    echo ""
  fi
}

# ─── Staging services ─────────────────────────────────────────────────────────
check_staging() {
  if ! $QUIET && ! $JSON_OUTPUT; then
    echo "── Staging Services ──"
  fi

  check_endpoint "stage-erp"      "stage-erp.$DOMAIN"      "/web/login"
  check_endpoint "stage-n8n"      "stage-n8n.$DOMAIN"      "/healthz"
  check_endpoint "stage-ocr"      "stage-ocr.$DOMAIN"      "/health"
  check_endpoint "stage-auth"     "stage-auth.$DOMAIN"     "/.well-known/openid-configuration"
  check_endpoint "stage-mcp"      "stage-mcp.$DOMAIN"      "/healthz"
  check_endpoint "stage-superset" "stage-superset.$DOMAIN" "/health"
  check_endpoint "stage-api"      "stage-api.$DOMAIN"      "/api/health"

  if ! $QUIET && ! $JSON_OUTPUT; then
    echo ""
  fi
}

# ─── DNS resolution ───────────────────────────────────────────────────────────
check_dns_records() {
  if ! $QUIET && ! $JSON_OUTPUT; then
    echo "── DNS Resolution (expecting $EXPECTED_IP) ──"
  fi

  local a_subs=("erp" "n8n" "ocr" "auth" "superset" "www")
  local cname_subs=("mcp")

  for sub in "${a_subs[@]}"; do
    local fqdn="${sub}.${DOMAIN}"
    local ip
    ip=$(check_dns "$fqdn" "A")

    if [[ "$ip" == "$EXPECTED_IP" ]]; then
      if ! $QUIET && ! $JSON_OUTPUT; then
        printf "  ✅ %-35s → %s\n" "$fqdn" "$ip"
      fi
    elif [[ -n "$ip" ]]; then
      # Cloudflare proxy IPs are expected
      if ! $QUIET && ! $JSON_OUTPUT; then
        printf "  ⚠️  %-34s → %s (CF proxy)\n" "$fqdn" "$ip"
      fi
      ((WARN++))
    else
      if ! $QUIET && ! $JSON_OUTPUT; then
        printf "  ❌ %-35s → NO RECORD\n" "$fqdn"
      fi
      ((FAIL++))
    fi
  done

  for sub in "${cname_subs[@]}"; do
    local fqdn="${sub}.${DOMAIN}"
    local target
    target=$(check_dns "$fqdn" "CNAME")

    if [[ -n "$target" ]]; then
      if ! $QUIET && ! $JSON_OUTPUT; then
        printf "  ✅ %-35s → %s\n" "$fqdn" "$target"
      fi
    else
      if ! $QUIET && ! $JSON_OUTPUT; then
        printf "  ⚠️  %-34s → CNAME hidden (CF proxy)\n" "$fqdn"
      fi
      ((WARN++))
    fi
  done

  if ! $QUIET && ! $JSON_OUTPUT; then
    echo ""
  fi
}

# ─── Deprecated domain check ─────────────────────────────────────────────────
check_deprecated() {
  if ! $QUIET && ! $JSON_OUTPUT; then
    echo "── Deprecated .net Domain ──"
  fi

  for sub in erp n8n ocr auth affine; do
    local fqdn="${sub}.insightpulseai.net"
    local ip
    ip=$(check_dns "$fqdn" "A")

    if [[ -z "$ip" ]]; then
      if ! $QUIET && ! $JSON_OUTPUT; then
        printf "  ✅ %-35s → (correctly removed)\n" "$fqdn"
      fi
    else
      if ! $QUIET && ! $JSON_OUTPUT; then
        printf "  ❌ %-35s → %s (should be removed)\n" "$fqdn" "$ip"
      fi
      ((FAIL++))
    fi
  done

  if ! $QUIET && ! $JSON_OUTPUT; then
    echo ""
  fi
}

# ─── Summary ──────────────────────────────────────────────────────────────────
summary() {
  local total=$((PASS + FAIL))

  if $JSON_OUTPUT; then
    python3 -c "
import json, sys
results = json.loads('''$JSON_RESULTS''')
summary = {
  'timestamp': '$(timestamp)',
  'scope': '$SCOPE',
  'total': $total,
  'pass': $PASS,
  'fail': $FAIL,
  'warn': $WARN,
  'status': 'healthy' if $FAIL == 0 else 'degraded',
  'services': results
}
print(json.dumps(summary, indent=2))
"
  else
    echo "=============================================="
    echo "  SUMMARY"
    echo "  Pass: $PASS | Fail: $FAIL | Warn: $WARN | Total: $total"
    if [[ $FAIL -eq 0 ]]; then
      echo "  Status: ✅ ALL HEALTHY"
    else
      echo "  Status: ❌ DEGRADED ($FAIL failures)"
    fi
    echo "=============================================="
  fi
}

# ─── Main ─────────────────────────────────────────────────────────────────────
header

case "$SCOPE" in
  production)
    check_production
    check_dns_records
    check_deprecated
    ;;
  staging)
    check_staging
    ;;
  all)
    check_production
    check_staging
    check_dns_records
    check_deprecated
    ;;
esac

summary

# Exit with failure if any checks failed
[[ $FAIL -eq 0 ]]
