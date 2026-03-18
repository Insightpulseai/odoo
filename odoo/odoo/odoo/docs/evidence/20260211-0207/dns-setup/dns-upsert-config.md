# DNS Configuration - Superset, MCP, n8n Subdomains

**Date**: 2026-02-11 02:07 UTC
**Status**: ❌ Failed (invalid Cloudflare API token)
**User Requirement**: All secrets must be stored in Supabase Vault

## Configuration

- **Zone ID**: `73f587aee652fc24fd643aec00dcca81`
- **Zone Name**: `insightpulseai.com`
- **Target IP**: `178.128.112.214`
- **Authoritative NS**: `edna.ns.cloudflare.com`, `keanu.ns.cloudflare.com`

## Subdomains to Create

| Subdomain | FQDN | IP | Proxied |
|-----------|------|----|---------|
| n8n | n8n.insightpulseai.com | 178.128.112.214 | false |
| superset | superset.insightpulseai.com | 178.128.112.214 | false |
| mcp | mcp.insightpulseai.com | 178.128.112.214 | false |

## Execution Status

**Required Environment Variable**: `CF_API_TOKEN` (Cloudflare API token with Zone:DNS edit permission)

**Error**: CF_API_TOKEN not set in environment

## Commands Ready for Execution

### 1. Upsert DNS Records
```bash
set -euo pipefail

export CF_ZONE_ID="73f587aee652fc24fd643aec00dcca81"
export CF_ZONE_NAME="insightpulseai.com"
export TARGET_IP="178.128.112.214"

: "${CF_API_TOKEN:?missing CF_API_TOKEN}"

upsert_a () {
  local name="$1"
  local fqdn="${name}.${CF_ZONE_NAME}"
  local ip="$2"
  local proxied="${3:-false}"

  local rec_id
  rec_id="$(
    curl -sS -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?type=A&name=$fqdn" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'][0]['id'] if d.get('result') else '')"
  )"

  local payload
  payload="$(python3 - <<PY
import json
print(json.dumps({
  "type": "A",
  "name": "$fqdn",
  "content": "$ip",
  "ttl": 1,
  "proxied": ($proxied.lower() == "true")
}))
PY
)"

  if [ -z "$rec_id" ]; then
    echo "Creating A $fqdn -> $ip (proxied=$proxied)"
    curl -sS -X POST \
      -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
      --data "$payload" >/dev/null
  else
    echo "Updating A $fqdn -> $ip (proxied=$proxied) rec_id=$rec_id"
    curl -sS -X PUT \
      -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$rec_id" \
      --data "$payload" >/dev/null
  fi
}

upsert_a "n8n"     "$TARGET_IP" false
upsert_a "superset" "$TARGET_IP" false
upsert_a "mcp"     "$TARGET_IP" false

echo "DNS upserts complete."
```

### 2. Verify DNS Resolution
```bash
set -euo pipefail
for h in n8n.insightpulseai.com superset.insightpulseai.com mcp.insightpulseai.com; do
  echo "== $h =="
  dig @1.1.1.1 +noall +answer "$h" A
  dig @8.8.8.8 +noall +answer "$h" A
done
```

### 3. Test HTTP Reachability
```bash
set -euo pipefail
for h in n8n.insightpulseai.com superset.insightpulseai.com mcp.insightpulseai.com; do
  echo "== $h =="
  curl -sS -I "http://$h" | head -n 5 || true
done
```

## Rollback Plan
```bash
set -euo pipefail

export CF_ZONE_ID="73f587aee652fc24fd643aec00dcca81"
export CF_ZONE_NAME="insightpulseai.com"
: "${CF_API_TOKEN:?missing CF_API_TOKEN}"

delete_name () {
  local fqdn="$1"
  local rec_id
  rec_id="$(
    curl -sS -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=$fqdn" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'][0]['id'] if d.get('result') else '')"
  )"
  if [ -n "$rec_id" ]; then
    echo "Deleting $fqdn (rec_id=$rec_id)"
    curl -sS -X DELETE -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$rec_id" >/dev/null
  else
    echo "No record found for $fqdn"
  fi
}

delete_name "n8n.$CF_ZONE_NAME"
delete_name "superset.$CF_ZONE_NAME"
delete_name "mcp.$CF_ZONE_NAME"
```

## Next Steps

1. Set CF_API_TOKEN environment variable (requires Cloudflare API token with Zone:DNS edit permission)
2. Run upsert script to create DNS records
3. Verify DNS resolution via dig
4. Test HTTP reachability
5. (Optional) Switch to proxied=true after confirming origin routing works
