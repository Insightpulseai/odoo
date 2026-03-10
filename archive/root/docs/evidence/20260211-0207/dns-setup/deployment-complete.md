# DNS Deployment Complete - n8n, Superset, MCP

**Date**: 2026-02-11 02:13 UTC
**Status**: ✅ DNS Records Created

## Deployment Summary

### DNS Records Created

| Subdomain | FQDN | IP | Status |
|-----------|------|----|--------|
| n8n | n8n.insightpulseai.com | 178.128.112.214 | ✅ Created |
| superset | superset.insightpulseai.com | 178.128.112.214 | ✅ Created |
| mcp | mcp.insightpulseai.com | 178.128.112.214 | ✅ Created |

**Cloudflare Zone**: 73f587aee652fc24fd643aec00dcca81
**Record Type**: A (non-proxied, DNS-only)
**TTL**: Auto (1 = automatic)

### Cloudflare API Token

**Token**: `mBi1r4mVrShjrckJ9v8btNMk5MWpJA4cZJ9T2q8_`
**Type**: Account API Token
**Permissions**: Read all resources + DNS Edit
**IP Allowlist**: ✅ 130.105.68.4 added (resolved IP restriction issue)

**Supabase Vault Storage**: ⚠️ Pending (connection issue)
```sql
-- Store after fixing Supabase connection
SELECT vault.create_secret(
  'CLOUDFLARE_API_TOKEN',
  'mBi1r4mVrShjrckJ9v8btNMk5MWpJA4cZJ9T2q8_',
  'Cloudflare API token for DNS - Account token with IP allowlist'
);
```

## Verification Results

### Cloudflare API Verification
```bash
✅ Zone access: Success
✅ DNS list: Success (5 existing records)
✅ DNS create: Success (test record)
✅ n8n record: 178.128.112.214
✅ superset record: 178.128.112.214
✅ mcp record: 178.128.112.214
```

### DNS Resolution
**Status**: ⏳ Propagating (records exist, resolver cache updating)

**Cloudflare Nameservers**: edna.ns.cloudflare.com, keanu.ns.cloudflare.com
**Propagation Time**: Typically 1-5 minutes

**Immediate verification** (bypass local cache):
```bash
dig @1.1.1.1 +short n8n.insightpulseai.com
dig @1.1.1.1 +short superset.insightpulseai.com
dig @1.1.1.1 +short mcp.insightpulseai.com
```

Expected output: `178.128.112.214` for all three

### HTTP Service Status

**Test Method**: Direct IP with Host header (bypasses DNS)

| Service | Status | Response | Next Step |
|---------|--------|----------|-----------|
| superset | ✅ Working | HTTP 302 redirect | DNS propagation only |
| n8n | ⚠️ Not configured | HTTP 404 | Configure nginx vhost |
| mcp | ⚠️ Not configured | HTTP 404 | Configure nginx vhost |

**superset.insightpulseai.com**:
```
HTTP/1.1 302 FOUND
Server: nginx/1.29.4
```
✅ Application running and responding

**n8n.insightpulseai.com**:
```
HTTP/1.1 404 Not Found
Server: nginx/1.29.4
```
⚠️ Nginx responding but no vhost config or app not running

**mcp.insightpulseai.com**:
```
HTTP/1.1 404 Not Found
Server: nginx/1.29.4
```
⚠️ Nginx responding but no vhost config or app not running

## Next Steps

### 1. Wait for DNS Propagation (1-5 minutes)
```bash
# Check resolution every 30 seconds
watch -n 30 'dig +short n8n.insightpulseai.com superset.insightpulseai.com mcp.insightpulseai.com'
```

### 2. Configure n8n Nginx Vhost
```bash
ssh root@178.128.112.214

# Create nginx config
cat > /etc/nginx/sites-available/n8n.insightpulseai.com <<'EOF'
server {
    listen 80;
    server_name n8n.insightpulseai.com;

    location / {
        proxy_pass http://localhost:5678;  # n8n default port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable and reload
ln -sf /etc/nginx/sites-available/n8n.insightpulseai.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 3. Configure MCP Nginx Vhost
```bash
ssh root@178.128.112.214

# Create nginx config (adjust port as needed)
cat > /etc/nginx/sites-available/mcp.insightpulseai.com <<'EOF'
server {
    listen 80;
    server_name mcp.insightpulseai.com;

    location / {
        proxy_pass http://localhost:3000;  # Adjust port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable and reload
ln -sf /etc/nginx/sites-available/mcp.insightpulseai.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 4. Setup HTTPS (Optional)
```bash
ssh root@178.128.112.214

# Install certbot if not present
apt-get update && apt-get install -y certbot python3-certbot-nginx

# Generate certificates
certbot --nginx -d n8n.insightpulseai.com -d superset.insightpulseai.com -d mcp.insightpulseai.com

# Auto-renewal already configured via certbot
```

## Commands Used

### DNS Creation
```bash
export CF_API_TOKEN="mBi1r4mVrShjrckJ9v8btNMk5MWpJA4cZJ9T2q8_"
export CF_ZONE_ID="73f587aee652fc24fd643aec00dcca81"
export CF_ZONE_NAME="insightpulseai.com"
export TARGET_IP="178.128.112.214"

# Upsert function created all three A records
# See: docs/evidence/20260211-0207/dns-setup/dns-upsert-config.md
```

### Verification
```bash
# Cloudflare API
curl -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=superset.insightpulseai.com"

# DNS resolution
dig @1.1.1.1 +short superset.insightpulseai.com

# HTTP test (bypass DNS)
curl -I -H "Host: superset.insightpulseai.com" http://178.128.112.214
```

## Rollback Procedure

```bash
export CF_API_TOKEN="mBi1r4mVrShjrckJ9v8btNMk5MWpJA4cZJ9T2q8_"
export CF_ZONE_ID="73f587aee652fc24fd643aec00dcca81"

delete_record() {
  local fqdn="$1"
  local rec_id=$(curl -sS -H "Authorization: Bearer $CF_API_TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=$fqdn" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'][0]['id'] if d.get('result') else '')")

  if [ -n "$rec_id" ]; then
    curl -X DELETE -H "Authorization: Bearer $CF_API_TOKEN" \
      "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$rec_id"
  fi
}

delete_record "n8n.insightpulseai.com"
delete_record "superset.insightpulseai.com"
delete_record "mcp.insightpulseai.com"
```

## Evidence Files

| File | Purpose |
|------|---------|
| `dns-upsert-config.md` | Complete upsert script and commands |
| `token-validation-failed.md` | Initial token issues (resolved) |
| `token-permissions-issue.md` | First token permission problems (resolved) |
| `ip-restriction-issue.md` | IP allowlist blocking (resolved) |
| `deployment-complete.md` | This file - successful deployment |

## Issues Resolved

1. ✅ Invalid token (expired from ~/.zshrc)
2. ✅ Token permissions insufficient (first user token)
3. ✅ IP restriction blocking 130.105.68.4
4. ✅ Account vs User token confusion
5. ✅ DNS record creation successful

## Summary

**DNS Setup**: ✅ Complete (all 3 records created and confirmed in Cloudflare)
**DNS Propagation**: ⏳ In progress (1-5 minutes typical)
**Superset HTTP**: ✅ Working (302 redirect, app responding)
**n8n HTTP**: ⚠️ Needs nginx vhost configuration
**MCP HTTP**: ⚠️ Needs nginx vhost configuration

**Token Management**: ⚠️ Functional but not yet stored in Supabase Vault (pending Supabase connection fix)
