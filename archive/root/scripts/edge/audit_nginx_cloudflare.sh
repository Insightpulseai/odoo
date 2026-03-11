#!/usr/bin/env bash
# =============================================================================
# audit_nginx_cloudflare.sh — Edge drift audit (nginx + Cloudflare vs SSOT)
# =============================================================================
# Reads ssot/edge/nginx_cloudflare_map.yaml and checks:
#   1. LOCAL: compose nginx service, mounted config paths, effective config
#   2. PROD (optional): SSH to prod host, capture nginx -T, diff key directives
#   3. CLOUDFLARE (optional): API query for DNS/proxy/SSL mode, compare to SSOT
#
# Environment variables (all optional — script degrades gracefully):
#   SSH_HOST        — prod host for nginx -T capture (e.g., root@178.128.112.214)
#   SSH_KEY         — path to SSH private key (default: ~/.ssh/id_rsa)
#   CF_API_TOKEN    — Cloudflare API token (DNS:Read, Zone:Read)
#   CF_ZONE_ID      — Cloudflare zone ID for insightpulseai.com
#
# Usage:
#   bash scripts/edge/audit_nginx_cloudflare.sh              # local-only
#   SSH_HOST=root@178.128.112.214 bash scripts/edge/...      # + prod nginx
#   CF_API_TOKEN=xxx CF_ZONE_ID=yyy bash scripts/edge/...    # + cloudflare
#
# Output:
#   docs/evidence/edge_drift_<timestamp>.md   (human-readable)
#   ssot/edge/drift_report.json               (machine-readable)
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SSOT_FILE="${REPO_ROOT}/ssot/edge/nginx_cloudflare_map.yaml"
TIMESTAMP="$(date +%Y%m%d-%H%M%z)"
EVIDENCE_DIR="${REPO_ROOT}/docs/evidence"
EVIDENCE_FILE="${EVIDENCE_DIR}/edge_drift_${TIMESTAMP}.md"
DRIFT_JSON="${REPO_ROOT}/ssot/edge/drift_report.json"

# Counters
PASS=0
WARN=0
FAIL=0
SKIP=0

# Colors
USE_COLOR=1
if [[ ! -t 1 ]]; then USE_COLOR=0; fi
_c() { if [[ "$USE_COLOR" -eq 1 ]]; then printf '\033[%sm' "$1"; fi; }
_r() { _c "0"; }
ok()   { PASS=$((PASS+1)); printf "  $(_c 32)PASS$(_r)  %s\n" "$*"; }
warn() { WARN=$((WARN+1)); printf "  $(_c 33)WARN$(_r)  %s\n" "$*"; }
fail() { FAIL=$((FAIL+1)); printf "  $(_c 31)FAIL$(_r)  %s\n" "$*"; }
skip() { SKIP=$((SKIP+1)); printf "  $(_c 36)SKIP$(_r)  %s\n" "$*"; }
hdr()  { printf "\n$(_c 1)── %s ──$(_r)\n" "$*"; }

# Evidence buffer
EV_BUF=""
ev() { EV_BUF="${EV_BUF}$*\n"; }

# JSON buffer
JSON_ITEMS=""
json_add() {
  local id="$1" status="$2" detail="$3"
  JSON_ITEMS="${JSON_ITEMS}{\"id\":\"${id}\",\"status\":\"${status}\",\"detail\":\"${detail}\"},"
}

# =============================================================================
# Phase 0: Validate SSOT file exists
# =============================================================================
hdr "Phase 0: SSOT Validation"
ev "# Edge Drift Report — ${TIMESTAMP}"
ev ""
ev "## Phase 0: SSOT Validation"
ev ""

if [[ ! -f "$SSOT_FILE" ]]; then
  fail "SSOT file not found: ${SSOT_FILE}"
  ev "- FAIL: SSOT file missing at \`${SSOT_FILE}\`"
  json_add "SSOT-FILE" "FAIL" "missing"
  # Write minimal output and exit
  printf '%s' "$EV_BUF" > "$EVIDENCE_FILE" 2>/dev/null || true
  exit 1
fi

ok "SSOT file exists: ssot/edge/nginx_cloudflare_map.yaml"
ev "- PASS: SSOT file present"
json_add "SSOT-FILE" "PASS" "exists"

# Quick YAML shape check (hostnames key exists)
if grep -q '^hostnames:' "$SSOT_FILE" 2>/dev/null; then
  ok "SSOT has hostnames section"
  ev "- PASS: hostnames section found"
else
  fail "SSOT missing hostnames section"
  ev "- FAIL: no hostnames section"
  json_add "SSOT-SHAPE" "FAIL" "missing-hostnames"
fi

if grep -q '^failure_modes:' "$SSOT_FILE" 2>/dev/null; then
  ok "SSOT has failure_modes catalog"
  ev "- PASS: failure_modes section found"
else
  warn "SSOT missing failure_modes catalog"
  ev "- WARN: no failure_modes section"
fi

# =============================================================================
# Phase 1: Local nginx (compose service + config paths)
# =============================================================================
hdr "Phase 1: Local Nginx (Compose)"
ev ""
ev "## Phase 1: Local Nginx"
ev ""

COMPOSE_FILE="${REPO_ROOT}/docker-compose.yml"
if [[ -f "$COMPOSE_FILE" ]]; then
  # Check nginx service exists in compose
  if grep -q 'nginx:' "$COMPOSE_FILE" 2>/dev/null; then
    ok "nginx service defined in docker-compose.yml"
    ev "- PASS: nginx service in docker-compose.yml"
    json_add "LOCAL-NGINX-COMPOSE" "PASS" "defined"
  else
    warn "No nginx service in docker-compose.yml"
    ev "- WARN: no nginx service in docker-compose.yml"
    json_add "LOCAL-NGINX-COMPOSE" "WARN" "missing"
  fi
else
  warn "docker-compose.yml not found"
  ev "- WARN: docker-compose.yml not found"
fi

# Check local config paths from SSOT
NGINX_MAIN="${REPO_ROOT}/ipai-platform/nginx/nginx.conf"
NGINX_DEFAULT="${REPO_ROOT}/ipai-platform/nginx/conf.d/default.conf"

if [[ -f "$NGINX_MAIN" ]]; then
  ok "Local nginx.conf: ipai-platform/nginx/nginx.conf"
  ev "- PASS: \`ipai-platform/nginx/nginx.conf\` exists"
  json_add "LOCAL-NGINX-CONF" "PASS" "exists"

  # Extract key directives
  ev ""
  ev "### nginx.conf key directives"
  ev "\`\`\`"
  ev "$(grep -E '(worker_processes|worker_connections|gzip |server_tokens|include)' "$NGINX_MAIN" | sed 's/^/  /')"
  ev "\`\`\`"
else
  fail "Missing: ipai-platform/nginx/nginx.conf"
  ev "- FAIL: \`ipai-platform/nginx/nginx.conf\` missing"
  json_add "LOCAL-NGINX-CONF" "FAIL" "missing"
fi

if [[ -f "$NGINX_DEFAULT" ]]; then
  ok "Local default.conf: ipai-platform/nginx/conf.d/default.conf"
  ev "- PASS: \`ipai-platform/nginx/conf.d/default.conf\` exists"
  json_add "LOCAL-DEFAULT-CONF" "PASS" "exists"

  # Extract key directives
  ev ""
  ev "### default.conf effective config"
  ev "\`\`\`"
  local_server_name=$(grep -m1 'server_name' "$NGINX_DEFAULT" | tr -s ' ' | sed 's/^ //')
  local_upstream=$(grep -m1 'proxy_pass' "$NGINX_DEFAULT" | tr -s ' ' | sed 's/^ //')
  local_listen=$(grep -m1 'listen' "$NGINX_DEFAULT" | tr -s ' ' | sed 's/^ //')
  ev "  ${local_listen}"
  ev "  ${local_server_name}"
  ev "  ${local_upstream}"
  ev "\`\`\`"

  # Check server_name
  if echo "$local_server_name" | grep -q 'localhost'; then
    ok "Local server_name: localhost (correct for dev)"
  else
    warn "Local server_name unexpected: ${local_server_name}"
  fi

  # Check upstream targets
  if grep -q 'odoo:8069' "$NGINX_DEFAULT"; then
    ok "Local upstream: odoo:8069 (compose service name)"
    json_add "LOCAL-UPSTREAM" "PASS" "odoo:8069"
  else
    warn "Local upstream not pointing to odoo:8069"
    json_add "LOCAL-UPSTREAM" "WARN" "unexpected"
  fi

  # Check longpolling upstream
  if grep -q 'odoo:8072' "$NGINX_DEFAULT"; then
    ok "Local longpoll upstream: odoo:8072"
  else
    warn "Local longpoll upstream missing or different from odoo:8072"
  fi

  # Check websocket upgrade headers
  if grep -q 'Upgrade' "$NGINX_DEFAULT" && grep -q 'Connection.*upgrade' "$NGINX_DEFAULT"; then
    ok "WebSocket upgrade headers present (Upgrade + Connection)"
    json_add "LOCAL-WEBSOCKET" "PASS" "headers-present"
  else
    fail "WebSocket upgrade headers missing"
    json_add "LOCAL-WEBSOCKET" "FAIL" "headers-missing"
  fi

  # Check proxy headers
  for header in "X-Forwarded-For" "X-Forwarded-Proto" "X-Real-IP" "Host"; do
    if grep -q "$header" "$NGINX_DEFAULT"; then
      ok "Proxy header: ${header}"
    else
      warn "Missing proxy header: ${header}"
    fi
  done

  # Check client_max_body_size
  if grep -q 'client_max_body_size' "$NGINX_DEFAULT"; then
    body_size=$(grep 'client_max_body_size' "$NGINX_DEFAULT" | tr -s ' ' | sed 's/^ //' | head -1)
    ok "Body size limit: ${body_size}"
  else
    warn "No client_max_body_size set (nginx default 1M)"
  fi
else
  fail "Missing: ipai-platform/nginx/conf.d/default.conf"
  ev "- FAIL: \`ipai-platform/nginx/conf.d/default.conf\` missing"
  json_add "LOCAL-DEFAULT-CONF" "FAIL" "missing"
fi

# =============================================================================
# Phase 1b: Prod nginx vhost inventory (repo configs)
# =============================================================================
hdr "Phase 1b: Prod Nginx Vhost Inventory (Repo)"
ev ""
ev "## Phase 1b: Prod Nginx Vhosts (from repo)"
ev ""

PROD_VHOSTS=(
  "insightpulseai.com:infra/deploy/nginx/insightpulseai.com.conf"
  "ocr.insightpulseai.com:infra/nginx/ocr.insightpulseai.com.conf"
  "n8n.insightpulseai.com:infra/nginx/n8n.insightpulseai.com.conf"
  "mcp.insightpulseai.com:infra/nginx/mcp.insightpulseai.com.conf"
  "plane.insightpulseai.com:infra/nginx/plane.insightpulseai.com.conf"
  "superset.insightpulseai.com:infra/nginx/superset.insightpulseai.com.conf"
)

EXPECTED_HOSTNAMES=(
  "insightpulseai.com"
  "ocr.insightpulseai.com"
  "n8n.insightpulseai.com"
  "mcp.insightpulseai.com"
  "plane.insightpulseai.com"
  "superset.insightpulseai.com"
)

for pair in "${PROD_VHOSTS[@]}"; do
  hostname="${pair%%:*}"
  config="${pair##*:}"
  full_path="${REPO_ROOT}/${config}"

  if [[ -f "$full_path" ]]; then
    ok "Vhost: ${hostname} → ${config}"
    ev "- PASS: \`${config}\` exists for ${hostname}"
    json_add "VHOST-${hostname}" "PASS" "${config}"

    # Check HTTPS support
    if grep -q 'listen 443' "$full_path"; then
      ok "  HTTPS: enabled (listen 443)"
    elif grep -q '# .*listen 443' "$full_path" || grep -q '#.*listen 443' "$full_path"; then
      warn "  HTTPS: commented out (TODO)"
      json_add "VHOST-${hostname}-HTTPS" "WARN" "commented-out"
    else
      warn "  HTTPS: not configured"
      json_add "VHOST-${hostname}-HTTPS" "WARN" "missing"
    fi
  else
    fail "Vhost MISSING: ${hostname} (expected: ${config})"
    ev "- FAIL: no vhost for ${hostname}"
    json_add "VHOST-${hostname}" "FAIL" "missing"
  fi
done

# Note: plane and superset are now included in PROD_VHOSTS above.
# If additional DNS-active subdomains need checking, add them to PROD_VHOSTS.

# =============================================================================
# Phase 2: Prod nginx via SSH (optional)
# =============================================================================
hdr "Phase 2: Prod Nginx via SSH"
ev ""
ev "## Phase 2: Prod Nginx (SSH)"
ev ""

if [[ -n "${SSH_HOST:-}" ]]; then
  SSH_KEY_ARG=""
  if [[ -n "${SSH_KEY:-}" ]]; then
    SSH_KEY_ARG="-i ${SSH_KEY}"
  fi

  ok "SSH_HOST set: ${SSH_HOST}"
  ev "- SSH target: \`${SSH_HOST}\`"

  # Capture nginx -T (full effective config)
  NGINX_T_FILE="${EVIDENCE_DIR}/nginx_T_prod_${TIMESTAMP}.txt"

  if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new \
       ${SSH_KEY_ARG} "${SSH_HOST}" "nginx -T" > "${NGINX_T_FILE}" 2>/dev/null; then
    ok "Captured nginx -T → ${NGINX_T_FILE}"
    ev "- PASS: \`nginx -T\` captured to \`${NGINX_T_FILE}\`"
    json_add "PROD-NGINX-T" "PASS" "captured"

    # Extract server_names from prod
    ev ""
    ev "### Prod server_name directives"
    ev "\`\`\`"
    grep 'server_name' "${NGINX_T_FILE}" | sort -u | sed 's/^/  /' >> /dev/null 2>&1 || true
    ev "$(grep 'server_name' "${NGINX_T_FILE}" | sort -u | sed 's/^/  /')"
    ev "\`\`\`"

    # Check each expected hostname
    for host in "${EXPECTED_HOSTNAMES[@]}"; do
      short="${host%%.*}"
      if grep -q "server_name.*${host}" "${NGINX_T_FILE}" 2>/dev/null; then
        ok "Prod vhost active: ${host}"
        json_add "PROD-VHOST-${short}" "PASS" "active"
      else
        fail "Prod vhost MISSING: ${host}"
        json_add "PROD-VHOST-${short}" "FAIL" "not-in-nginx-T"
      fi
    done

    # Check HTTPS listeners
    https_count=$(grep -c 'listen 443' "${NGINX_T_FILE}" 2>/dev/null || echo "0")
    ok "Prod HTTPS listeners: ${https_count}"
    ev "- HTTPS server blocks: ${https_count}"

  else
    fail "SSH to ${SSH_HOST} failed or nginx -T unavailable"
    ev "- FAIL: SSH connection or nginx -T failed"
    json_add "PROD-NGINX-T" "FAIL" "ssh-failed"
  fi
else
  skip "SSH_HOST not set — skipping prod nginx audit"
  ev "- SKIP: SSH_HOST not set (set SSH_HOST=user@ip to enable)"
  json_add "PROD-NGINX" "SKIP" "no-ssh-host"
fi

# =============================================================================
# Phase 3: Cloudflare API (optional)
# =============================================================================
hdr "Phase 3: Cloudflare DNS/SSL (API)"
ev ""
ev "## Phase 3: Cloudflare"
ev ""

if [[ -n "${CF_API_TOKEN:-}" ]] && [[ -n "${CF_ZONE_ID:-}" ]]; then
  ok "CF_API_TOKEN and CF_ZONE_ID set"
  ev "- Cloudflare zone: \`${CF_ZONE_ID}\`"

  # Fetch DNS records
  CF_DNS_FILE="${EVIDENCE_DIR}/cf_dns_${TIMESTAMP}.json"
  if curl -sf -H "Authorization: Bearer ${CF_API_TOKEN}" \
    "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records?per_page=100" \
    > "${CF_DNS_FILE}" 2>/dev/null; then
    ok "Fetched Cloudflare DNS records → ${CF_DNS_FILE}"
    ev "- PASS: DNS records saved to \`${CF_DNS_FILE}\`"
    json_add "CF-DNS-FETCH" "PASS" "saved"

    # Count records
    if command -v jq >/dev/null 2>&1; then
      total=$(jq '.result | length' "${CF_DNS_FILE}" 2>/dev/null || echo "?")
      ok "Total DNS records: ${total}"
      ev "- Total records: ${total}"

      # Check each SSOT hostname
      ev ""
      ev "### DNS Record Comparison"
      ev ""
      ev "| Hostname | SSOT Type | CF Type | CF Proxied | Match |"
      ev "|----------|-----------|---------|------------|-------|"

      # Parse SSOT hostnames and compare
      while IFS= read -r hostname; do
        hostname=$(echo "$hostname" | tr -d ' "')
        [[ -z "$hostname" ]] && continue

        cf_record=$(jq -r ".result[] | select(.name == \"${hostname}\") | \"\(.type)|\(.proxied)\"" \
          "${CF_DNS_FILE}" 2>/dev/null | head -1)

        if [[ -n "$cf_record" ]]; then
          cf_type="${cf_record%%|*}"
          cf_proxied="${cf_record##*|}"

          # Get SSOT expected type (simplified — grep from SSOT)
          ssot_type=$(grep -A5 "hostname: ${hostname}" "$SSOT_FILE" 2>/dev/null \
            | grep 'dns_type:' | head -1 | awk '{print $2}' || echo "UNKNOWN")

          if [[ "$cf_type" == "$ssot_type" ]]; then
            ok "CF match: ${hostname} (${cf_type}, proxied=${cf_proxied})"
            ev "| ${hostname} | ${ssot_type} | ${cf_type} | ${cf_proxied} | MATCH |"
          else
            fail "CF drift: ${hostname} — SSOT=${ssot_type} CF=${cf_type}"
            ev "| ${hostname} | ${ssot_type} | ${cf_type} | ${cf_proxied} | **DRIFT** |"
            json_add "CF-DRIFT-${hostname}" "FAIL" "ssot=${ssot_type},cf=${cf_type}"
          fi
        fi
      done < <(grep '^\s*- hostname:' "$SSOT_FILE" | awk -F': ' '{print $2}')
    else
      warn "jq not installed — skipping JSON parsing"
      ev "- WARN: jq not available for JSON parsing"
    fi
  else
    fail "Cloudflare API call failed"
    ev "- FAIL: API call failed (check CF_API_TOKEN)"
    json_add "CF-DNS-FETCH" "FAIL" "api-error"
  fi

  # Fetch zone SSL settings
  CF_SSL_FILE="${EVIDENCE_DIR}/cf_ssl_${TIMESTAMP}.json"
  if curl -sf -H "Authorization: Bearer ${CF_API_TOKEN}" \
    "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/settings/ssl" \
    > "${CF_SSL_FILE}" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then
      ssl_mode=$(jq -r '.result.value' "${CF_SSL_FILE}" 2>/dev/null || echo "UNKNOWN")
      ok "CF SSL mode: ${ssl_mode}"
      ev "- CF SSL mode: \`${ssl_mode}\`"

      if [[ "$ssl_mode" == "strict" ]] || [[ "$ssl_mode" == "full" ]]; then
        ok "SSL mode compatible with SSOT (full_strict)"
      else
        fail "SSL mode mismatch — SSOT expects full_strict, CF has ${ssl_mode}"
        json_add "CF-SSL-MODE" "FAIL" "expected=full_strict,actual=${ssl_mode}"
      fi
    fi
  fi
else
  skip "CF_API_TOKEN/CF_ZONE_ID not set — skipping Cloudflare audit"
  ev "- SKIP: CF_API_TOKEN or CF_ZONE_ID not set"
  json_add "CF-AUDIT" "SKIP" "no-credentials"
fi

# =============================================================================
# Phase 4: Summary
# =============================================================================
hdr "Summary"
ev ""
ev "## Summary"
ev ""
ev "| Metric | Count |"
ev "|--------|-------|"
ev "| PASS   | ${PASS} |"
ev "| WARN   | ${WARN} |"
ev "| FAIL   | ${FAIL} |"
ev "| SKIP   | ${SKIP} |"

printf "\n$(_c 1)Results:$(_r) %d pass, %d warn, %d fail, %d skip\n\n" \
  "$PASS" "$WARN" "$FAIL" "$SKIP"

# =============================================================================
# Write outputs
# =============================================================================

# Evidence markdown
mkdir -p "$(dirname "$EVIDENCE_FILE")"
printf '%b' "$EV_BUF" > "$EVIDENCE_FILE"
printf "Evidence: %s\n" "$EVIDENCE_FILE"

# Drift report JSON
# Remove trailing comma from JSON_ITEMS
JSON_ITEMS="${JSON_ITEMS%,}"
mkdir -p "$(dirname "$DRIFT_JSON")"
cat > "$DRIFT_JSON" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "ssot_file": "ssot/edge/nginx_cloudflare_map.yaml",
  "summary": {
    "pass": ${PASS},
    "warn": ${WARN},
    "fail": ${FAIL},
    "skip": ${SKIP}
  },
  "items": [${JSON_ITEMS}]
}
EOF
printf "Drift JSON: %s\n" "$DRIFT_JSON"

exit 0
