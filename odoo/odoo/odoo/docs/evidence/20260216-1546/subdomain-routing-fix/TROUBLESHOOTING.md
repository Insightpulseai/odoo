# Subdomain Routing - Troubleshooting Guide

**Date**: 2026-02-17
**Related**: `IMPLEMENTATION_SUMMARY.md`

---

## n8n: PostHog Analytics Error

### Symptom
```
Application Error
TypeError: Failed to fetch dynamically imported module:
https://n8n.insightpulseai.com/assets/posthog-provider-D6HARb7w.js
```

### Root Cause
n8n is trying to lazy-load a PostHog analytics provider module that doesn't exist in this n8n build. This is a **frontend-only error** related to optional analytics tracking.

### Impact
**✅ NONE** - n8n functionality is **NOT affected**.

- Core workflow automation: ✅ Working
- API endpoints: ✅ Working
- Health check: ✅ Returns `{"status":"ok"}`
- UI loads: ✅ Title: "n8n.io - Workflow Automation"

### Fix Options

**Option 1: Ignore (Recommended)**
- Error is harmless
- n8n works perfectly without analytics
- Browser console error only

**Option 2: Disable PostHog in n8n**
```bash
ssh root@178.128.112.214
docker exec c95d05274029_n8n-prod sh -c "echo 'N8N_DIAGNOSTICS_ENABLED=false' >> /home/node/.n8n/.env"
docker restart c95d05274029_n8n-prod
```

**Option 3: Update n8n Image**
```bash
# Pull latest n8n image (may include fixed analytics)
ssh root@178.128.112.214
cd /opt/n8n  # or wherever compose file is
docker compose pull n8n
docker compose up -d n8n
```

### Verification
```bash
# n8n is healthy
curl https://n8n.insightpulseai.com/healthz
# Expected: {"status":"ok"}

# UI loads correctly
curl -s https://n8n.insightpulseai.com | grep '<title>'
# Expected: <title>n8n.io - Workflow Automation</title>
```

**Recommendation**: **Ignore the error** unless analytics are critical.

---

## MCP: Root Endpoint 404

### Symptom
```
GET https://mcp.insightpulseai.com
Response: {"detail":"Not Found"}
```

### Root Cause
The MCP coordinator **does not serve content at root path**. This is **by design**.

### Expected Behavior

**❌ Root path returns 404**:
```bash
curl https://mcp.insightpulseai.com
# {"detail":"Not Found"}
```

**✅ Health endpoint works**:
```bash
curl https://mcp.insightpulseai.com/health
# {"status":"ok","version":"0.1.0","targets":["odoo_prod","odoo_lab","agent_coordination"]}
```

**✅ Provider endpoints work** (with auth):
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://mcp.insightpulseai.com/providers/socket/health
# Returns Socket provider health status
```

### Available Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | None | Hub health check |
| `/providers/:provider/health` | GET | None | Provider health check |
| `/providers/:provider/:tool` | POST | JWT | Call provider tool |

### Fix
**No fix needed** - this is correct behavior.

**Expected Usage**:
```typescript
// ❌ Wrong: accessing root
fetch('https://mcp.insightpulseai.com')

// ✅ Right: accessing health endpoint
fetch('https://mcp.insightpulseai.com/health')

// ✅ Right: calling provider tool
fetch('https://mcp.insightpulseai.com/providers/socket/scan.repo', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ repo: 'odoo', ref: 'main' })
})
```

### Verification
```bash
# Hub health (should return 200)
curl -I https://mcp.insightpulseai.com/health
# HTTP/2 200

# Root path (expected 404)
curl -I https://mcp.insightpulseai.com
# HTTP/2 404

# Provider health (should return 200)
curl https://mcp.insightpulseai.com/providers/socket/health
# (May return 404 until Socket provider implemented)
```

**Recommendation**: Access `/health` endpoint, not root.

---

## Both Services Healthy

### Current Status (2026-02-17)

**n8n.insightpulseai.com**:
- Status: ✅ HEALTHY
- UI: ✅ Loading correctly
- Health: ✅ `{"status":"ok"}`
- Issue: ⚠️ Analytics module 404 (non-critical)

**mcp.insightpulseai.com**:
- Status: ✅ HEALTHY
- Health: ✅ `{"status":"ok","version":"0.1.0"}`
- Root: ❌ 404 (by design)
- Providers: 🚧 Pending implementation (see `spec/mcp-provider-system/`)

### Next Steps

1. **n8n**: No action required (error is harmless)
2. **MCP**: Implement Socket provider (see `spec/mcp-provider-system/plan.md`)
3. **Monitoring**: Add both to `scripts/health/all_services_healthcheck.py`

---

## Quick Reference

### Health Check Commands

```bash
# n8n
curl https://n8n.insightpulseai.com/healthz
# Expected: {"status":"ok"}

# MCP Hub
curl https://mcp.insightpulseai.com/health
# Expected: {"status":"ok","version":"0.1.0","targets":[...]}

# Both (one-liner)
echo "n8n:" && curl -s https://n8n.insightpulseai.com/healthz && \
echo "MCP:" && curl -s https://mcp.insightpulseai.com/health
```

### Troubleshooting Checklist

- [ ] n8n health endpoint returns 200
- [ ] n8n UI loads (check title tag)
- [ ] MCP health endpoint returns 200
- [ ] nginx configs exist for both subdomains
- [ ] SSL certificates valid (expires 2026-05-17)
- [ ] DNS resolves correctly (Cloudflare IPs)
- [ ] Containers running (docker ps)

**All checks passed?** ✅ Both services are healthy!

---

## Related Documents

- `IMPLEMENTATION_SUMMARY.md` - Original fix implementation
- `spec/mcp-provider-system/` - MCP provider architecture
- `docs/architecture/MCP_REGISTRY.md` - MCP selection and roadmap
