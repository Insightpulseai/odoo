# DNS Setup Guide - ops.insightpulseai.com

Complete guide for configuring Cloudflare DNS to point to Vercel deployment.

---

## Current Status

**Domain**: `insightpulseai.com` (Cloudflare-managed, delegated from Spacesquare)
**Subdomain**: `ops.insightpulseai.com` (needs DNS record)
**Target**: Vercel deployment URL (to be obtained)

**Error**: `DNS_PROBE_FINISHED_NXDOMAIN` - No DNS record exists yet

---

## Step-by-Step Setup

### Step 1: Deploy to Vercel (Get Deployment URL)

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/saas-landing

# Run first-time deployment
./scripts/vercel-first-deploy.sh

# This will:
# 1. Unset placeholder Vercel env vars
# 2. Create new Vercel project interactively
# 3. Deploy and give you the URL
```

**Expected output**:
```
✓ Deployed to production. Run `vercel --prod` to overwrite later.
https://saas-landing-abc123.vercel.app
```

**Copy this URL** - you'll need it for Cloudflare.

---

### Step 2: Add Cloudflare DNS Record

#### Option A: Via Cloudflare Dashboard (Recommended)

1. **Go to Cloudflare Dashboard**:
   - URL: https://dash.cloudflare.com/
   - Login with your credentials

2. **Select Domain**:
   - Click on `insightpulseai.com`

3. **Add DNS Record**:
   - Navigate to: **DNS** → **Records** → **Add record**
   - Fill in:
     - **Type**: `CNAME`
     - **Name**: `ops`
     - **Target**: `saas-landing-abc123.vercel.app` (from Step 1)
     - **Proxy status**: ✅ Proxied (orange cloud icon)
     - **TTL**: Auto
   - Click **Save**

4. **Verify**:
   - Record should appear as: `ops.insightpulseai.com` → `saas-landing-abc123.vercel.app`
   - Status: Proxied (orange cloud)

#### Option B: Via Cloudflare API (Automated)

```bash
# Set your Cloudflare credentials
export CF_API_TOKEN="your-cloudflare-api-token"
export CF_ZONE_ID="your-zone-id"  # For insightpulseai.com

# Get Vercel deployment URL from Step 1
export VERCEL_URL="saas-landing-abc123.vercel.app"

# Create DNS record
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "CNAME",
    "name": "ops",
    "content": "'$VERCEL_URL'",
    "ttl": 1,
    "proxied": true
  }' | jq
```

**Expected response**:
```json
{
  "success": true,
  "result": {
    "id": "...",
    "type": "CNAME",
    "name": "ops.insightpulseai.com",
    "content": "saas-landing-abc123.vercel.app",
    "proxied": true
  }
}
```

---

### Step 3: Add Custom Domain in Vercel

1. **Go to Vercel Dashboard**:
   - URL: https://vercel.com/dashboard
   - Select your project (saas-landing)

2. **Add Custom Domain**:
   - Navigate to: **Settings** → **Domains**
   - Click **Add**
   - Enter: `ops.insightpulseai.com`
   - Click **Add**

3. **Verify Configuration**:
   - Vercel will detect the CNAME record
   - Status should show: ✅ Valid Configuration

---

### Step 4: Wait for DNS Propagation

```bash
# Check DNS propagation (run every 30 seconds)
dig ops.insightpulseai.com

# Expected output:
# ops.insightpulseai.com. 300 IN CNAME saas-landing-abc123.vercel.app.

# Or use online tool:
# https://www.whatsmydns.net/#CNAME/ops.insightpulseai.com
```

**Typical propagation time**: 1-5 minutes (Cloudflare is fast)

---

### Step 5: Deploy to Production with Correct URL

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/saas-landing

# Source secrets
source ~/.zshrc

# Deploy to production (sets NEXT_PUBLIC_APP_URL=https://ops.insightpulseai.com)
./scripts/deploy-production.sh
```

---

### Step 6: Verify Production Deployment

```bash
# Test DNS resolution
curl -sS -I https://ops.insightpulseai.com/ | head -20

# Expected:
# HTTP/2 200
# content-type: text/html

# Test API endpoints
curl -sS -I https://ops.insightpulseai.com/api/invite/list | head -20

# Expected:
# HTTP/2 200
# content-type: application/json
```

---

## DNS Record Details

### CNAME Record Configuration

| Field | Value | Notes |
|-------|-------|-------|
| **Type** | `CNAME` | Canonical name record |
| **Name** | `ops` | Subdomain (becomes ops.insightpulseai.com) |
| **Target** | `saas-landing-abc123.vercel.app` | Vercel deployment URL |
| **TTL** | `Auto` or `300` | Time to live (5 minutes) |
| **Proxy** | ✅ **Proxied** | Orange cloud (Cloudflare proxy) |

### Why CNAME (not A record)?

- Vercel deployments use dynamic IPs
- CNAME automatically follows Vercel's IP changes
- Cloudflare proxy provides DDoS protection, caching, SSL

---

## Existing DNS Records

**Reference**: From CLAUDE.md infrastructure section

| Subdomain | Type | Target | Purpose |
|-----------|------|--------|---------|
| `chat` | A | 178.128.112.214 | Mattermost (deprecated) |
| `n8n` | A | 178.128.112.214 | n8n automation |
| `erp` | A | 178.128.112.214 | Odoo ERP |
| `auth` | A | 178.128.112.214 | Authentication |
| `ocr` | A | 178.128.112.214 | OCR service |
| `superset` | CNAME | superset-nlavf.ondigitalocean.app | BI dashboard |
| `mcp` | CNAME | pulse-hub-web-an645.ondigitalocean.app | MCP server |
| `agent` | CNAME | wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run | AI agent |
| **`ops`** | **CNAME** | **saas-landing-xxx.vercel.app** | **SaaS platform** (NEW) |

---

## Troubleshooting

### "DNS_PROBE_FINISHED_NXDOMAIN"

**Cause**: No DNS record exists for `ops.insightpulseai.com`

**Fix**: Complete Steps 1-3 above

### "Invalid Configuration" in Vercel

**Cause**: DNS record not propagated yet

**Fix**: Wait 5 minutes and refresh Vercel dashboard

### "SSL Error" or "Certificate Invalid"

**Cause**: Vercel hasn't issued SSL cert yet

**Fix**: Wait for Vercel to provision SSL (automatic, 1-5 minutes)

### "Wrong Page Showing"

**Cause**: Cached old DNS or old deployment

**Fix**:
```bash
# Clear browser cache
# Or use incognito mode
# Or wait 5 minutes for cache to expire
```

---

## Cloudflare API Credentials

### Get API Token

1. **Go to**: https://dash.cloudflare.com/profile/api-tokens
2. **Create Token** → **Edit zone DNS** template
3. **Permissions**:
   - Zone → DNS → Edit
   - Zone → Zone → Read
4. **Zone Resources**:
   - Include → Specific zone → `insightpulseai.com`
5. **Create Token** and save it to `~/.zshrc`:

```bash
export CF_API_TOKEN="your-cloudflare-api-token-here"
```

### Get Zone ID

```bash
# List zones to find Zone ID
curl -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" | jq '.result[] | select(.name=="insightpulseai.com") | .id'

# Save to ~/.zshrc
export CF_ZONE_ID="your-zone-id-here"
```

---

## Quick Reference

### One-Command Setup (After Vercel Deploy)

```bash
# Set variables
export VERCEL_URL="saas-landing-abc123.vercel.app"  # From Step 1
export CF_API_TOKEN="your-token"
export CF_ZONE_ID="your-zone-id"

# Create DNS record
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "CNAME",
    "name": "ops",
    "content": "'$VERCEL_URL'",
    "proxied": true
  }' | jq

# Wait 2 minutes for propagation
sleep 120

# Deploy to production
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/templates/saas-landing
source ~/.zshrc
./scripts/deploy-production.sh
```

---

## Related Documentation

- **Deployment**: `DEPLOY.md`
- **Configuration**: `docs/CONFIGURATION.md`
- **Cloudflare Dashboard**: https://dash.cloudflare.com/
- **Vercel Dashboard**: https://vercel.com/dashboard

---

**Last Updated**: 2026-02-12
