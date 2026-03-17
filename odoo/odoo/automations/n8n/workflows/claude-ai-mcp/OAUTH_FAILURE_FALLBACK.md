# OAuth2 Failure → Bearer Token Fallback Plan

## Error Analysis

```
McpAuthorizationError: Your account was authorized but the integration rejected the credentials
Reference: a522be1ed4dbe120
```

**Root Cause**: n8n's instance-level MCP OAuth2 is either:
- Not available in your n8n version
- Not properly configured
- Incompatible with Claude.ai's OAuth2 flow

**Solution**: Use **MCP Server Trigger nodes with Bearer Token** authentication instead.

---

## ✅ Recommended Fallback: Bearer Token Approach

This approach uses per-workflow SSE endpoints with manual bearer token auth (more reliable than instance-level OAuth2).

### Step 1: Generate Bearer Token

**Option A: Use Python (Recommended)**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option B: Use OpenSSL**
```bash
openssl rand -base64 32
```

**Option C: Use Node.js**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**Save the token** - you'll need it for both n8n and Claude.ai!

---

### Step 2: Store Bearer Token in n8n

**Method A: n8n Environment Variable (Recommended)**

1. Login to n8n: https://n8n.insightpulseai.com
2. Go to **Settings** → **Variables**
3. Click **"+ Add Variable"**
4. **Name**: `MCP_BEARER_TOKEN`
5. **Value**: Paste the token from Step 1
6. **Save**

**Method B: Supabase Vault**

```sql
-- Store in Supabase Vault (run in Supabase SQL Editor)
INSERT INTO vault.secrets (name, secret)
VALUES ('n8n_mcp_bearer_token', 'YOUR_TOKEN_HERE')
ON CONFLICT (name) DO UPDATE SET secret = EXCLUDED.secret;
```

---

### Step 3: Import Workflow with MCP Server Trigger Node

I'll create a test workflow with MCP Server Trigger node configured:

**File**: `automations/n8n/workflows/claude-ai-mcp/test/mcp_test_workflow.json`

This workflow will:
- Use MCP Server Trigger node
- Authenticate with bearer token
- Return simple JSON response
- Test Claude.ai connection

---

### Step 4: Configure Claude.ai Connector (Bearer Token)

1. **Open Claude.ai** → **Settings** → **Custom Connectors**
2. **Click "Add Connector"**
3. **Transport Type**: Server-Sent Events (SSE)
4. **Server URL**: `https://n8n.insightpulseai.com/webhook/mcp-test` (from test workflow)
5. **Authentication**: Bearer Token
6. **Token**: Paste the same token from Step 1
7. **Save Connector**

---

### Step 5: Test Connection

In Claude.ai chat:
```
Test the MCP connection
```

Expected response:
```json
{
  "status": "success",
  "message": "MCP Server Trigger test successful",
  "timestamp": "2026-02-20T20:30:00+0800"
}
```

---

## Why This Approach Works

| Issue | Bearer Token Solution |
|-------|----------------------|
| OAuth2 failure | ✅ No OAuth2 required |
| Auth complexity | ✅ Simple bearer token |
| n8n version issues | ✅ Works on any n8n version with webhook support |
| Configuration | ✅ Explicit, deterministic setup |
| Debugging | ✅ Clear error messages |

---

## Full Deployment After Successful Test

Once the test workflow works:

1. **Import all 9 production workflows** (see DEPLOYMENT_GUIDE.md)
2. **Update connector URL** to production endpoint
3. **Verify all tools** are discoverable in Claude.ai
4. **Test each tool** with sample queries

---

## Troubleshooting

### "Invalid bearer token"
- Verify token matches exactly in both n8n variable and Claude.ai connector
- Check for extra spaces or newlines
- Regenerate token and update both locations

### "Endpoint not found"
- Verify workflow is activated in n8n
- Check webhook URL matches Claude.ai connector URL
- Test endpoint manually: `curl -H "Authorization: Bearer YOUR_TOKEN" https://n8n.insightpulseai.com/webhook/mcp-test`

### "Connection timeout"
- Check n8n is accessible: `curl https://n8n.insightpulseai.com/healthcheck`
- Verify nginx reverse proxy is running: `systemctl status nginx` (on DO droplet)
- Check firewall allows HTTPS traffic

---

## Next Steps

1. **I'll create the test workflow** with MCP Server Trigger node
2. **You generate a bearer token** using one of the methods above
3. **Store it in n8n** environment variables
4. **Import the test workflow** to n8n
5. **Configure Claude.ai connector** with bearer token
6. **Test connection** with simple query

Ready to proceed with the test workflow?
