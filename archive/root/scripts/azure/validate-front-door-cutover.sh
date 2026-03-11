#!/usr/bin/env bash
# =============================================================================
# validate-front-door-cutover.sh
# =============================================================================
# Validates Azure Front Door cutover status for each hostname.
#
# Reads hostnames from ssot/azure/hostname-cutover-checklist.yaml and performs:
#   1. DNS resolution — checks for *.azurefd.net CNAME or Front Door IP
#   2. Health check  — expects HTTP 200 on the configured health path
#   3. TLS certificate — checks for Azure-managed cert (Microsoft/DigiCert issuer)
#   4. Front Door headers — confirms x-azure-ref / x-fd-* headers present
#   5. Content preview — shows first 20 lines for manual review
#
# Usage:
#   ./scripts/azure/validate-front-door-cutover.sh                   # all hostnames
#   ./scripts/azure/validate-front-door-cutover.sh --hostname erp.insightpulseai.com
#   ./scripts/azure/validate-front-door-cutover.sh --wave wave1-core
#   ./scripts/azure/validate-front-door-cutover.sh --dry-run
#   ./scripts/azure/validate-front-door-cutover.sh --hostname erp.insightpulseai.com --dry-run
#
# Exit codes:
#   0 — all checked hostnames passed
#   1 — one or more hostnames failed
#   2 — configuration or dependency error
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHECKLIST="${REPO_ROOT}/ssot/azure/hostname-cutover-checklist.yaml"

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  CYAN='\033[0;36m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  GREEN='' RED='' YELLOW='' CYAN='' BOLD='' RESET=''
fi

pass() { printf "${GREEN}PASS${RESET}"; }
fail() { printf "${RED}FAIL${RESET}"; }
skip() { printf "${YELLOW}SKIP${RESET}"; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
FILTER_HOSTNAME=""
FILTER_WAVE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hostname)
      FILTER_HOSTNAME="$2"
      shift 2
      ;;
    --wave)
      FILTER_WAVE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      head -25 "$0" | tail -20
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------
for cmd in python3 dig curl openssl; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: Required command '$cmd' not found." >&2
    exit 2
  fi
done

if ! python3 -c "import yaml" 2>/dev/null; then
  echo "ERROR: Python3 yaml module required. Install: pip3 install pyyaml" >&2
  exit 2
fi

if [[ ! -f "$CHECKLIST" ]]; then
  echo "ERROR: Checklist not found: $CHECKLIST" >&2
  echo "Create ssot/azure/hostname-cutover-checklist.yaml first." >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Parse checklist YAML into JSON lines for bash consumption
# ---------------------------------------------------------------------------
parse_checklist() {
  python3 - "$CHECKLIST" "$FILTER_HOSTNAME" "$FILTER_WAVE" <<'PYEOF'
import sys, yaml, json

checklist_path = sys.argv[1]
filter_hostname = sys.argv[2] if len(sys.argv) > 2 else ""
filter_wave = sys.argv[3] if len(sys.argv) > 3 else ""

with open(checklist_path) as f:
    data = yaml.safe_load(f)

waves = data.get("waves", [])

for wave_entry in waves:
    wave_name = wave_entry.get("name", "")
    for entry in wave_entry.get("hostnames", []):
        hostname = entry.get("hostname", "")
        health_path = entry.get("health_check_path", "/")
        enabled = entry.get("enabled", True)

        if not enabled:
            continue
        if filter_hostname and hostname != filter_hostname:
            continue
        if filter_wave and wave_name != filter_wave:
            continue

        print(json.dumps({
            "hostname": hostname,
            "wave": wave_name,
            "health_path": health_path,
            "expected_backend": entry.get("azure_target", ""),
        }))
PYEOF
}

# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------
CURL_TIMEOUT=10
DIG_TIMEOUT=5

check_dns() {
  local hostname="$1"
  local dns_result
  dns_result="$(dig +short "$hostname" +time="$DIG_TIMEOUT" +tries=1 2>/dev/null || true)"

  if [[ -z "$dns_result" ]]; then
    echo "FAIL:no_resolution"
    return
  fi

  # Check for azurefd.net CNAME in the chain
  local cname_chain
  cname_chain="$(dig +short CNAME "$hostname" +time="$DIG_TIMEOUT" +tries=1 2>/dev/null || true)"

  if echo "$cname_chain" | grep -qi 'azurefd\.net'; then
    echo "PASS:${cname_chain}"
    return
  fi

  # Also check full trace for azurefd.net
  local trace
  trace="$(dig +trace "$hostname" +time="$DIG_TIMEOUT" +tries=1 2>/dev/null || true)"
  if echo "$trace" | grep -qi 'azurefd\.net'; then
    echo "PASS:azurefd_in_chain"
    return
  fi

  # Check if resolution points to known Front Door IP ranges
  # Azure Front Door Anycast IPs are not static, but check CNAME chain
  local all_records
  all_records="$(dig +short "$hostname" +time="$DIG_TIMEOUT" +tries=1 2>/dev/null || true)"
  if echo "$all_records" | grep -qi 'azurefd\|afd\|frontdoor'; then
    echo "PASS:${all_records}"
    return
  fi

  echo "FAIL:not_front_door:${dns_result}"
}

check_health() {
  local hostname="$1"
  local health_path="$2"
  local url="https://${hostname}${health_path}"
  local http_code

  http_code="$(curl -s -o /dev/null -w '%{http_code}' \
    --connect-timeout "$CURL_TIMEOUT" \
    --max-time "$CURL_TIMEOUT" \
    "$url" 2>/dev/null || echo "000")"

  if [[ "$http_code" == "200" ]]; then
    echo "PASS:${http_code}"
  elif [[ "$http_code" == "000" ]]; then
    echo "FAIL:timeout"
  else
    echo "FAIL:${http_code}"
  fi
}

check_tls() {
  local hostname="$1"
  local issuer

  issuer="$(echo | openssl s_client -servername "$hostname" -connect "${hostname}:443" 2>/dev/null \
    | openssl x509 -noout -issuer 2>/dev/null || echo "FAIL:connection_error")"

  if [[ "$issuer" == "FAIL:"* ]]; then
    echo "$issuer"
    return
  fi

  # Azure-managed certs are issued by Microsoft or DigiCert
  if echo "$issuer" | grep -qiE 'Microsoft|DigiCert'; then
    echo "PASS:azure_managed"
  else
    # Extract issuer CN for reporting
    local cn
    cn="$(echo "$issuer" | sed 's/.*CN *= *//' | head -1)"
    echo "FAIL:issuer=${cn}"
  fi
}

check_fd_headers() {
  local hostname="$1"
  local headers

  headers="$(curl -sI --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
    "https://${hostname}/" 2>/dev/null || echo "")"

  if [[ -z "$headers" ]]; then
    echo "FAIL:no_response"
    return
  fi

  local fd_ref fd_other
  fd_ref="$(echo "$headers" | grep -ci 'x-azure-ref' || true)"
  fd_other="$(echo "$headers" | grep -ci 'x-fd-' || true)"

  if [[ "$fd_ref" -gt 0 ]] || [[ "$fd_other" -gt 0 ]]; then
    echo "PASS:headers_found"
  else
    echo "FAIL:no_fd_headers"
  fi
}

preview_content() {
  local hostname="$1"
  curl -s --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
    "https://${hostname}/" 2>/dev/null | head -20
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
entries="$(parse_checklist)"

if [[ -z "$entries" ]]; then
  echo "No hostnames matched the filter criteria." >&2
  if [[ -n "$FILTER_HOSTNAME" ]]; then
    echo "  --hostname: $FILTER_HOSTNAME" >&2
  fi
  if [[ -n "$FILTER_WAVE" ]]; then
    echo "  --wave: $FILTER_WAVE" >&2
  fi
  exit 2
fi

total=0
passed=0
failed=0

# Print header
printf "\n${BOLD}Azure Front Door Cutover Validation${RESET}\n"
printf "Checklist: %s\n" "$CHECKLIST"
if [[ -n "$FILTER_HOSTNAME" ]]; then printf "Filter hostname: %s\n" "$FILTER_HOSTNAME"; fi
if [[ -n "$FILTER_WAVE" ]]; then printf "Filter wave: %s\n" "$FILTER_WAVE"; fi
if $DRY_RUN; then printf "${YELLOW}DRY RUN — no checks will be executed${RESET}\n"; fi
printf "%s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf "\n"

# Table header
printf "${BOLD}%-35s %-12s %-12s %-12s %-14s %-8s${RESET}\n" \
  "HOSTNAME" "DNS" "HEALTH" "TLS" "FD_HEADERS" "OVERALL"
printf "%-35s %-12s %-12s %-12s %-14s %-8s\n" \
  "-----------------------------------" "----------" "----------" "----------" "------------" "------"

while IFS= read -r line; do
  hostname="$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['hostname'])")"
  health_path="$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['health_path'])")"
  wave="$(echo "$line" | python3 -c "import sys,json; print(json.load(sys.stdin)['wave'])")"

  total=$((total + 1))

  if $DRY_RUN; then
    printf "%-35s " "$hostname"
    printf "$(skip)%-5s " ""
    printf "$(skip)%-5s " ""
    printf "$(skip)%-5s " ""
    printf "$(skip)%-7s " ""
    printf "$(skip)\n"
    continue
  fi

  # Run checks
  dns_result="$(check_dns "$hostname")"
  health_result="$(check_health "$hostname" "$health_path")"
  tls_result="$(check_tls "$hostname")"
  fd_result="$(check_fd_headers "$hostname")"

  # Determine pass/fail for each
  dns_status="FAIL"; [[ "$dns_result" == PASS:* ]] && dns_status="PASS"
  health_status="FAIL"; [[ "$health_result" == PASS:* ]] && health_status="PASS"
  tls_status="FAIL"; [[ "$tls_result" == PASS:* ]] && tls_status="PASS"
  fd_status="FAIL"; [[ "$fd_result" == PASS:* ]] && fd_status="PASS"

  # Overall
  overall="PASS"
  if [[ "$dns_status" != "PASS" ]] || [[ "$health_status" != "PASS" ]] || \
     [[ "$tls_status" != "PASS" ]] || [[ "$fd_status" != "PASS" ]]; then
    overall="FAIL"
    failed=$((failed + 1))
  else
    passed=$((passed + 1))
  fi

  # Print row
  printf "%-35s " "$hostname"

  if [[ "$dns_status" == "PASS" ]]; then printf "$(pass)%-5s " ""; else printf "$(fail)%-5s " ""; fi
  if [[ "$health_status" == "PASS" ]]; then printf "$(pass)%-5s " ""; else printf "$(fail)%-5s " ""; fi
  if [[ "$tls_status" == "PASS" ]]; then printf "$(pass)%-5s " ""; else printf "$(fail)%-5s " ""; fi
  if [[ "$fd_status" == "PASS" ]]; then printf "$(pass)%-7s " ""; else printf "$(fail)%-7s " ""; fi
  if [[ "$overall" == "PASS" ]]; then printf "$(pass)\n"; else printf "$(fail)\n"; fi

  # Print details on failure
  if [[ "$overall" == "FAIL" ]]; then
    [[ "$dns_status" != "PASS" ]] && printf "  ${RED}dns: %s${RESET}\n" "${dns_result#*:}"
    [[ "$health_status" != "PASS" ]] && printf "  ${RED}health: %s${RESET}\n" "${health_result#*:}"
    [[ "$tls_status" != "PASS" ]] && printf "  ${RED}tls: %s${RESET}\n" "${tls_result#*:}"
    [[ "$fd_status" != "PASS" ]] && printf "  ${RED}fd_headers: %s${RESET}\n" "${fd_result#*:}"
  fi

done <<< "$entries"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
printf "\n${BOLD}Summary${RESET}\n"
printf "Total: %d  Passed: ${GREEN}%d${RESET}  Failed: ${RED}%d${RESET}\n" "$total" "$passed" "$failed"

if $DRY_RUN; then
  printf "${YELLOW}Dry run — no checks were executed.${RESET}\n"
  exit 0
fi

# ---------------------------------------------------------------------------
# Content preview (only on single hostname)
# ---------------------------------------------------------------------------
if [[ -n "$FILTER_HOSTNAME" ]] && ! $DRY_RUN; then
  printf "\n${BOLD}Content Preview (first 20 lines):${RESET}\n"
  printf "${CYAN}---${RESET}\n"
  preview_content "$FILTER_HOSTNAME"
  printf "\n${CYAN}---${RESET}\n"
fi

if [[ "$failed" -gt 0 ]]; then
  exit 1
else
  exit 0
fi
