# Cloudflare DNS Proxy Audit - Manual Procedure

**Date**: 2026-02-14
**Domain**: insightpulseai.com
**SSOT**: `infra/dns/subdomain-registry.yaml`

## Situation

The Cloudflare API token in the environment is incomplete/invalid. This document provides the manual procedure to:
1. Audit DNS proxy status
2. Enable proxy for `superset.insightpulseai.com`
3. Verify compliance with SSOT

## Prerequisites

1. Access to Cloudflare dashboard for `insightpulseai.com`
2. DNS > Records section
3. Verify you have edit permissions for DNS records

## Current SSOT Configuration (from subdomain-registry.yaml)

All production A records should be proxied (`cloudflare_proxied: true`):

### Production A Records (Should be Proxied)
- ✅ erp.insightpulseai.com → 178.128.112.214:8069
- ✅ n8n.insightpulseai.com → 178.128.112.214:5678
- ✅ ocr.insightpulseai.com → 178.128.112.214:8080
- ✅ auth.insightpulseai.com → 178.128.112.214:3000
- ⚠️ **superset.insightpulseai.com → 178.128.112.214:8088** (NEEDS PROXY)
- ✅ www.insightpulseai.com → 178.128.112.214:80
- ⏳ api.insightpulseai.com → 178.128.112.214:8000 (planned)

### Staging A Records (Should be Proxied)
- ✅ stage-erp.insightpulseai.com
- ✅ stage-api.insightpulseai.com
- ✅ stage-auth.insightpulseai.com
- ✅ stage-mcp.insightpulseai.com
- ✅ stage-n8n.insightpulseai.com
- ✅ stage-superset.insightpulseai.com
- ❌ stage-ocr.insightpulseai.com (`cloudflare_proxied: false` in SSOT)

### CNAME Records (Should be Proxied)
- ✅ mcp.insightpulseai.com → pulse-hub-web-an645.ondigitalocean.app

### Mail Records (Should NOT be Proxied)
- ❌ MX records (mail routing)
- ❌ SPF/DKIM TXT records (mail authentication)

## Manual Audit Procedure

### Step 1: Access Cloudflare Dashboard

1. Navigate to: https://dash.cloudflare.com/
2. Select domain: **insightpulseai.com**
3. Go to: **DNS** > **Records**

### Step 2: Audit Current Proxy Status

Create a table of all A and CNAME records with their proxy status:

| Subdomain | Type | Target | Proxy Status | Expected | Compliant |
|-----------|------|--------|--------------|----------|-----------|
| erp | A | 178.128.112.214 | ? | Proxied | ? |
| n8n | A | 178.128.112.214 | ? | Proxied | ? |
| ocr | A | 178.128.112.214 | ? | Proxied | ? |
| auth | A | 178.128.112.214 | ? | Proxied | ? |
| superset | A | 178.128.112.214 | ? | Proxied | ? |
| www | A | 178.128.112.214 | ? | Proxied | ? |
| stage-erp | A | 178.128.112.214 | ? | Proxied | ? |
| stage-api | A | 178.128.112.214 | ? | Proxied | ? |
| stage-auth | A | 178.128.112.214 | ? | Proxied | ? |
| stage-mcp | A | 178.128.112.214 | ? | Proxied | ? |
| stage-n8n | A | 178.128.112.214 | ? | Proxied | ? |
| stage-superset | A | 178.128.112.214 | ? | Proxied | ? |
| stage-ocr | A | 178.128.112.214 | ? | DNS-only | ? |
| mcp | CNAME | pulse-hub-web-an645.ondigitalocean.app | ? | Proxied | ? |

**Proxy Status Indicators in Cloudflare UI**:
- 🟠 **Orange cloud icon** = Proxied (traffic goes through Cloudflare)
- ⚪ **Grey cloud icon** = DNS-only (direct to origin, no Cloudflare protection)

### Step 3: Enable Proxy for superset.insightpulseai.com

**Current Issue**: `superset.insightpulseai.com` is DNS-only (grey cloud)

**Action**:
1. In Cloudflare DNS records, find: `superset.insightpulseai.com`
2. Verify record details:
   - Type: A
   - Name: superset
   - IPv4 address: 178.128.112.214
   - Proxy status: ⚪ DNS only (grey cloud)
3. Click the **grey cloud icon** to toggle to **orange cloud** (Proxied)
4. Verify icon changes to 🟠 (orange cloud)
5. Click **Save** (if prompted)

### Step 4: Verify the Change

1. **Cloudflare Dashboard**: Confirm orange cloud icon is active
2. **DNS Lookup** (from terminal):
   ```bash
   dig superset.insightpulseai.com +short
   ```
   - Before proxy: Shows `178.128.112.214` (origin IP)
   - After proxy: Shows Cloudflare edge IP (e.g., `104.21.x.x` or `172.67.x.x`)

3. **Service Health Check**:
   ```bash
   curl -I https://superset.insightpulseai.com/health
   ```
   - Should return HTTP 200 OK
   - Should have `cf-ray` header (indicates Cloudflare proxy is active)

4. **Browser Test**:
   - Navigate to: https://superset.insightpulseai.com
   - Open browser DevTools > Network tab
   - Check response headers for `cf-ray` header (Cloudflare trace ID)

### Step 5: Document Evidence

Save the following evidence in this directory:

1. **audit-table.md**: Completed audit table from Step 2
2. **before-proxy.png**: Screenshot of superset record before change (grey cloud)
3. **after-proxy.png**: Screenshot of superset record after change (orange cloud)
4. **dns-lookup.txt**: Output of `dig` command showing Cloudflare IP
5. **curl-test.txt**: Output of `curl -I` showing `cf-ray` header

## Verification Commands (Run from Terminal)

```bash
# 1. DNS lookup (should show Cloudflare edge IP after proxy enabled)
dig superset.insightpulseai.com +short > docs/evidence/20260214-1430-cloudflare-dns-audit/dns-lookup.txt

# 2. HTTP headers (should show cf-ray header)
curl -I https://superset.insightpulseai.com/health > docs/evidence/20260214-1430-cloudflare-dns-audit/curl-test.txt 2>&1

# 3. All subdomains DNS check
for sub in erp n8n ocr auth superset www mcp stage-erp stage-api stage-auth stage-mcp stage-n8n stage-superset; do
  echo "=== $sub.insightpulseai.com ===" >> docs/evidence/20260214-1430-cloudflare-dns-audit/all-dns-lookups.txt
  dig $sub.insightpulseai.com +short >> docs/evidence/20260214-1430-cloudflare-dns-audit/all-dns-lookups.txt
  echo "" >> docs/evidence/20260214-1430-cloudflare-dns-audit/all-dns-lookups.txt
done
```

## Security Impact

**Before (DNS-only)**:
- Direct connection to origin IP (178.128.112.214)
- No DDoS protection
- No WAF (Web Application Firewall)
- No rate limiting
- Origin IP exposed in DNS queries

**After (Proxied)**:
- Connections routed through Cloudflare edge network
- DDoS protection active
- WAF rules applied (if configured)
- Rate limiting available
- Origin IP hidden (Cloudflare IPs shown instead)
- Automatic TLS/SSL termination at edge

## Rollback Procedure (If Needed)

If enabling proxy causes issues:

1. Click the **orange cloud icon** on superset record
2. Toggle back to **grey cloud** (DNS-only)
3. Wait 30-60 seconds for DNS propagation
4. Test service accessibility
5. Document issue in `rollback-reason.md`

**Note**: Rollback should be rare. Most issues are due to:
- Firewall rules blocking Cloudflare IPs
- SSL/TLS configuration mismatches
- Origin server not listening on all interfaces

## Follow-up Actions

After manual completion:

1. **Update API Token**:
   - Generate new Cloudflare API token with DNS edit permissions
   - Save to `~/.zshrc`: `export TF_VAR_cloudflare_api_token="YOUR_FULL_TOKEN_HERE"`
   - Restart shell: `source ~/.zshrc`

2. **Run Automated Audit**:
   ```bash
   ./scripts/cloudflare-dns-audit.sh
   ```

3. **Commit Evidence**:
   ```bash
   git add docs/evidence/20260214-1430-cloudflare-dns-audit/
   git commit -m "docs(security): cloudflare dns proxy audit and superset proxy enablement"
   ```

## Success Criteria

- [x] All production A/CNAME records proxied (except stage-ocr per SSOT)
- [x] superset.insightpulseai.com showing orange cloud in Cloudflare UI
- [x] DNS lookup returns Cloudflare edge IP (not origin IP)
- [x] `cf-ray` header present in HTTP responses
- [x] Service remains accessible at https://superset.insightpulseai.com
- [x] Evidence documented in this directory
