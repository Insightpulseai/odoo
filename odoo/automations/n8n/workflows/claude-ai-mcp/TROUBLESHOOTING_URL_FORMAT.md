# Troubleshooting: Claude.ai "Server URL doesn't match expected format"

## Error
```
Server URL doesn't match expected format
```

## Root Cause

Claude.ai expects a specific URL format for MCP servers, but n8n's documentation doesn't specify the exact format needed.

---

## Quick Fix: Check n8n MCP Settings

### Step 1: Find the Official n8n MCP Endpoint

1. **Login to n8n**: https://n8n.insightpulseai.com
2. **Go to Settings** → **MCP Access**
3. **Look for one of these:**
   - "Server URL" field
   - "Endpoint URL" field
   - "MCP Server Address" field
   - "Connection URL" field
4. **Copy the exact URL** shown there

### Step 2: Use That URL in Claude.ai

Paste the exact URL from n8n into Claude.ai's "Server URL" field.

---

## URL Format Candidates (Try in Order)

If n8n MCP Access doesn't show an explicit URL, try these formats:

### Format 1: API Path (Most Common)
```
https://n8n.insightpulseai.com/api/v1/mcp
```

### Format 2: Webhook Path
```
https://n8n.insightpulseai.com/webhook/mcp
```

### Format 3: SSE Endpoint
```
https://n8n.insightpulseai.com/webhook-test/mcp
```

### Format 4: Root with Trailing Slash
```
https://n8n.insightpulseai.com/
```

### Format 5: Port-Specific (if custom port)
```
https://n8n.insightpulseai.com:5678/api/v1/mcp
```

---

## Diagnostic: Test Endpoints

Run this on DO droplet to check which MCP endpoints exist:

```bash
# SSH to droplet
ssh root@178.128.112.214

# Check nginx config for MCP routes
grep -r "mcp" /etc/nginx/sites-enabled/

# Check n8n logs for MCP initialization
journalctl -u n8n --since "1 hour ago" | grep -i "mcp"

# Test endpoints
curl -I https://n8n.insightpulseai.com/api/v1/mcp
curl -I https://n8n.insightpulseai.com/webhook/mcp
curl -I https://n8n.insightpulseai.com/webhook-test/mcp
```

---

## Alternative: Check n8n Environment Variables

n8n might require an environment variable to expose the MCP server:

```bash
# On DO droplet
cat /etc/systemd/system/n8n.service | grep -i "mcp"

# Or check n8n process
ps aux | grep n8n | grep -i "mcp"
```

Look for variables like:
- `N8N_MCP_ENABLED=true`
- `N8N_MCP_PATH=/api/v1/mcp`
- `N8N_MCP_PORT=5678`

---

## Claude.ai URL Format Requirements

Claude.ai MCP connectors typically expect:

1. **HTTPS required** (not HTTP)
2. **Valid SSL certificate**
3. **No auth in URL** (auth handled separately via OAuth2/Bearer)
4. **Specific path** that matches MCP protocol spec

**Examples from other MCP servers**:
- `https://api.example.com/mcp/v1`
- `https://mcp.example.com/`
- `https://example.com/api/mcp`

---

## Fallback: Use MCP Server Trigger Approach

If instance-level MCP isn't working, fall back to the MCP Server Trigger node approach:

1. **Import workflows** with MCP Server Trigger nodes (see DEPLOYMENT_GUIDE.md)
2. **Configure bearer token**
3. **Use per-workflow SSE endpoints**:
   ```
   https://n8n.insightpulseai.com/webhook/mcp-insightpulse
   ```

This uses custom SSE endpoints instead of n8n's built-in MCP server.

---

## Report Back

Once you find the working URL format, please share it so we can:
1. Update DEPLOYMENT_GUIDE_V2.md with correct URL
2. Update QUICK_START_V2.md
3. Document the exact format for future reference

---

**Next Step**: Check n8n → Settings → MCP Access for the official endpoint URL.
