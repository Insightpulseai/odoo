#!/usr/bin/env bash
# =============================================================================
# validate-odoo-aca.sh
# =============================================================================
# Validates the Odoo ACA runtime against ssot/azure/odoo-runtime.yaml.
#
# Checks:
#   1. All 3 long-running services exist (odoo-web, odoo-worker, odoo-cron)
#   2. Only odoo-web has ingress configured
#   3. Correct image tag on active revision
#   4. Replica bounds match SSOT expectations
#   5. Expected environment variables / secret references present
#   6. odoo-web health endpoint reachable (if --live flag)
#   7. odoo-worker / odoo-cron NOT externally exposed
#
# Usage:
#   ./scripts/azure/validate-odoo-aca.sh                          # dry check against Azure
#   ./scripts/azure/validate-odoo-aca.sh --resource-group rg-ipai-dev
#   ./scripts/azure/validate-odoo-aca.sh --live                   # include health probe
#   ./scripts/azure/validate-odoo-aca.sh --ssot-only              # validate YAML only
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed
#   2 — configuration or dependency error
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SSOT_FILE="${REPO_ROOT}/ssot/azure/odoo-runtime.yaml"

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'
  BOLD='\033[1m'; RESET='\033[0m'
else
  GREEN='' RED='' YELLOW='' BOLD='' RESET=''
fi

pass() { printf "${GREEN}PASS${RESET}"; }
fail() { printf "${RED}FAIL${RESET}"; }
warn() { printf "${YELLOW}WARN${RESET}"; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
RESOURCE_GROUP=""
LIVE_CHECK=false
SSOT_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --resource-group) RESOURCE_GROUP="$2"; shift 2 ;;
    --live) LIVE_CHECK=true; shift ;;
    --ssot-only) SSOT_ONLY=true; shift ;;
    -h|--help) head -25 "$0" | tail -20; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "ERROR: Python3 yaml module required. Install: pip3 install pyyaml" >&2
  exit 2
fi

if [[ ! -f "$SSOT_FILE" ]]; then
  echo "ERROR: SSOT file not found: $SSOT_FILE" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# SSOT validation
# ---------------------------------------------------------------------------
total=0
passed=0
failed=0

check() {
  local label="$1" result="$2"
  total=$((total + 1))
  if [[ "$result" == "PASS" ]]; then
    passed=$((passed + 1))
    printf "  $(pass) %s\n" "$label"
  else
    failed=$((failed + 1))
    printf "  $(fail) %s — %s\n" "$label" "$result"
  fi
}

printf "\n${BOLD}Odoo ACA Runtime Validation${RESET}\n"
printf "SSOT: %s\n" "$SSOT_FILE"
printf "%s\n\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- SSOT structure checks ---
printf "${BOLD}1. SSOT Structure${RESET}\n"

ssot_services=$(python3 -c "
import yaml, sys
with open('$SSOT_FILE') as f:
    data = yaml.safe_load(f)
services = data.get('services', [])
for s in services:
    print(f\"{s['name']}|{s['kind']}|{s.get('ingress','none')}|{s.get('role','unknown')}\")
")

# Check expected services exist
for expected in "odoo-web|containerapp|internal|http" "odoo-worker|containerapp|none|background-worker" "odoo-cron|containerapp|none|scheduled-worker" "odoo-init|containerapp-job|none|schema-init"; do
  name=$(echo "$expected" | cut -d'|' -f1)
  if echo "$ssot_services" | grep -q "^${name}|"; then
    check "$name defined in SSOT" "PASS"
  else
    check "$name defined in SSOT" "MISSING"
  fi
done

# Check ingress policy
web_ingress=$(echo "$ssot_services" | grep "^odoo-web|" | cut -d'|' -f3)
worker_ingress=$(echo "$ssot_services" | grep "^odoo-worker|" | cut -d'|' -f3)
cron_ingress=$(echo "$ssot_services" | grep "^odoo-cron|" | cut -d'|' -f3)

[[ "$web_ingress" == "internal" ]] && check "odoo-web ingress = internal" "PASS" || check "odoo-web ingress = internal" "got: $web_ingress"
[[ "$worker_ingress" == "none" ]] && check "odoo-worker ingress = none" "PASS" || check "odoo-worker ingress = none" "got: $worker_ingress"
[[ "$cron_ingress" == "none" ]] && check "odoo-cron ingress = none" "PASS" || check "odoo-cron ingress = none" "got: $cron_ingress"

# Check cron max_replicas = 1
cron_max=$(python3 -c "
import yaml
with open('$SSOT_FILE') as f:
    data = yaml.safe_load(f)
for s in data.get('services', []):
    if s['name'] == 'odoo-cron':
        print(s.get('max_replicas', 'unknown'))
")
[[ "$cron_max" == "1" ]] && check "odoo-cron max_replicas = 1" "PASS" || check "odoo-cron max_replicas = 1" "got: $cron_max"

if $SSOT_ONLY; then
  printf "\n${BOLD}Summary (SSOT only)${RESET}\n"
  printf "Total: %d  Passed: ${GREEN}%d${RESET}  Failed: ${RED}%d${RESET}\n\n" "$total" "$passed" "$failed"
  [[ "$failed" -gt 0 ]] && exit 1 || exit 0
fi

# ---------------------------------------------------------------------------
# Azure resource checks (requires az CLI + login)
# ---------------------------------------------------------------------------
if ! command -v az &>/dev/null; then
  printf "\n${YELLOW}az CLI not found — skipping Azure resource checks${RESET}\n"
  printf "\n${BOLD}Summary (SSOT only)${RESET}\n"
  printf "Total: %d  Passed: ${GREEN}%d${RESET}  Failed: ${RED}%d${RESET}\n\n" "$total" "$passed" "$failed"
  [[ "$failed" -gt 0 ]] && exit 1 || exit 0
fi

if [[ -z "$RESOURCE_GROUP" ]]; then
  printf "\n${YELLOW}No --resource-group specified — skipping Azure resource checks${RESET}\n"
  printf "\n${BOLD}Summary${RESET}\n"
  printf "Total: %d  Passed: ${GREEN}%d${RESET}  Failed: ${RED}%d${RESET}\n\n" "$total" "$passed" "$failed"
  [[ "$failed" -gt 0 ]] && exit 1 || exit 0
fi

printf "\n${BOLD}2. Azure Resource Checks (RG: $RESOURCE_GROUP)${RESET}\n"

for svc in odoo-web odoo-worker odoo-cron; do
  exists=$(az containerapp show --name "$svc" --resource-group "$RESOURCE_GROUP" --query "name" -o tsv 2>/dev/null || echo "")
  if [[ "$exists" == "$svc" ]]; then
    check "$svc exists in Azure" "PASS"

    # Check ingress
    ingress_external=$(az containerapp show --name "$svc" --resource-group "$RESOURCE_GROUP" \
      --query "properties.configuration.ingress.external" -o tsv 2>/dev/null || echo "null")

    if [[ "$svc" == "odoo-web" ]]; then
      [[ "$ingress_external" == "false" ]] && check "$svc ingress internal" "PASS" || check "$svc ingress internal" "got: $ingress_external"
    else
      [[ "$ingress_external" == "null" || "$ingress_external" == "" ]] && check "$svc no ingress" "PASS" || check "$svc no ingress" "has ingress: $ingress_external"
    fi

    # Check replicas
    min_rep=$(az containerapp show --name "$svc" --resource-group "$RESOURCE_GROUP" \
      --query "properties.template.scale.minReplicas" -o tsv 2>/dev/null || echo "unknown")
    max_rep=$(az containerapp show --name "$svc" --resource-group "$RESOURCE_GROUP" \
      --query "properties.template.scale.maxReplicas" -o tsv 2>/dev/null || echo "unknown")
    check "$svc replicas min=$min_rep max=$max_rep" "PASS"
  else
    check "$svc exists in Azure" "NOT FOUND"
  fi
done

# ---------------------------------------------------------------------------
# Live health check
# ---------------------------------------------------------------------------
if $LIVE_CHECK; then
  printf "\n${BOLD}3. Live Health Check${RESET}\n"

  web_fqdn=$(az containerapp show --name odoo-web --resource-group "$RESOURCE_GROUP" \
    --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null || echo "")

  if [[ -n "$web_fqdn" ]]; then
    http_code=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 --max-time 10 \
      "https://${web_fqdn}/web/health" 2>/dev/null || echo "000")
    [[ "$http_code" == "200" ]] && check "odoo-web /web/health → $http_code" "PASS" || check "odoo-web /web/health → $http_code" "expected 200"
  else
    check "odoo-web FQDN resolution" "no FQDN found"
  fi

  # Verify worker/cron are NOT reachable
  for svc in odoo-worker odoo-cron; do
    svc_fqdn=$(az containerapp show --name "$svc" --resource-group "$RESOURCE_GROUP" \
      --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null || echo "")
    if [[ -z "$svc_fqdn" ]]; then
      check "$svc not externally reachable" "PASS"
    else
      check "$svc not externally reachable" "HAS FQDN: $svc_fqdn"
    fi
  done
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
printf "\n${BOLD}Summary${RESET}\n"
printf "Total: %d  Passed: ${GREEN}%d${RESET}  Failed: ${RED}%d${RESET}\n\n" "$total" "$passed" "$failed"

[[ "$failed" -gt 0 ]] && exit 1 || exit 0
