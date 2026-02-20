# Claude.ai → n8n MCP Connector Setup Guide

> **Complete step-by-step setup for enabling Claude.ai web interface to query Odoo SOR data and trigger n8n workflows.**

---

## Prerequisites

Before starting, ensure you have:

- ✅ Access to https://n8n.insightpulseai.com (admin credentials)
- ✅ Access to Claude.ai account (custom connector feature enabled)
- ✅ Access to Supabase Vault (for secure token storage)
- ✅ n8n workflows repository cloned locally (`/odoo/automations/n8n/workflows/`)

---

## Step 1: Import n8n Workflows

### 1.1 Locate Workflow Files

Workflows are located at:
```
/odoo/automations/n8n/workflows/claude-ai-mcp/
├── read-only/
│   ├── 01_mcp_odoo_query.json
│   ├── 02_mcp_supabase_ops.json
│   ├── 03_mcp_finance_summary.json
│   ├── 04_mcp_infra_health.json
│   ├── 05_mcp_workflow_monitor.json
│   └── 06_mcp_sync_trigger.json
└── write-path/
    ├── 07_mcp_workflow_manager.json
    ├── 08_mcp_github_ops.json
    └── 09_mcp_artifact_deployer.json
```

### 1.2 Import via n8n UI

1. Navigate to https://n8n.insightpulseai.com
2. Click **Workflows** in left sidebar
3. Click **Import from File** button
4. Select `01_mcp_odoo_query.json`
5. Review workflow structure
6. Click **Import**
7. Repeat for all 9 workflow files

**Tip**: Import in numerical order to maintain logical grouping.

### 1.3 Activate Workflows

After importing each workflow:

1. Open the workflow in n8n editor
2. Click **Activate** toggle in top-right corner
3. Verify webhook URL is displayed (e.g., `/webhook/mcp-odoo-query`)
4. Test workflow execution manually (optional)

---

## Step 2: Generate Bearer Token

### 2.1 Generate Secure Random Token

Use one of these methods:

**Option A: OpenSSL**
```bash
openssl rand -hex 32
```

**Option B: Python**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option C: Node.js**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Save the output** — you'll need it in the next steps.

Example output: `a8f2c3d7e9b1f4a6c8d2e5f3a7b9c1d4e6f8a2b4c6d8e1f3a5b7c9d1e3f5a7b9`

### 2.2 Store Token in Supabase Vault

**Method A: SQL Query (Recommended)**

1. Open Supabase SQL Editor: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/sql
2. Run this query:

```sql
INSERT INTO vault.secrets (name, secret, description)
VALUES (
  'n8n_mcp_bearer_token',
  'YOUR_TOKEN_FROM_STEP_2.1',
  'Bearer token for Claude.ai → n8n MCP integration'
)
ON CONFLICT (name) DO UPDATE SET
  secret = EXCLUDED.secret,
  updated_at = NOW();
```

3. Verify insertion:

```sql
SELECT name, description, created_at
FROM vault.secrets
WHERE name = 'n8n_mcp_bearer_token';
```

**Method B: Supabase CLI**

```bash
# Set environment variable
export N8N_MCP_TOKEN="YOUR_TOKEN_FROM_STEP_2.1"

# Insert into Vault
supabase secrets set n8n_mcp_bearer_token="$N8N_MCP_TOKEN" \
  --project-ref spdtwktxdalcfigzeqrz
```

### 2.3 Configure n8n to Validate Token

1. Open n8n → **Settings** → **Variables**
2. Add new variable:
   - **Name**: `MCP_BEARER_TOKEN`
   - **Value**: (paste token from Step 2.1)
   - **Type**: `String`
3. Click **Save**

4. Update each workflow to validate bearer token:
   - Open workflow in editor
   - Add **HTTP Request** node at start of workflow
   - Configure validation logic (check `Authorization` header)

**Note**: Token validation logic should already be present in imported workflows. Verify it exists.

---

## Step 3: Test SSE Endpoint

### 3.1 Test Connection

```bash
# Test SSE endpoint with curl
curl -N -H "Authorization: Bearer YOUR_TOKEN" \
  https://n8n.insightpulseai.com/webhook/mcp-insightpulse/sse
```

**Expected output**:
```
event: endpoint
data: {"url": "https://n8n.insightpulseai.com/webhook/mcp-insightpulse/sse"}

event: keepalive
data: {"timestamp": "2026-02-20T12:34:56Z"}
```

### 3.2 Test Individual Tool

```bash
# Test odoo_query tool
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "odoo_query",
    "params": {
      "model": "res.partner",
      "domain": "[[\\"is_company\\", \\"=\\", true]]",
      "fields": ["name", "email"],
      "limit": 5
    }
  }' \
  https://n8n.insightpulseai.com/webhook/mcp-odoo-query
```

**Expected output**: JSON array of Odoo partner records

---

## Step 4: Configure Claude.ai Custom Connector

### 4.1 Access Custom Connectors

1. Log in to Claude.ai
2. Click **Settings** (gear icon, bottom-left)
3. Navigate to **Custom Connectors** tab
4. Click **Add Connector** button

### 4.2 Paste Connector Configuration

1. Copy contents of `connector-config.json`
2. Paste into Claude.ai connector configuration field
3. Review configuration summary

**Verify these values**:
- **Transport URL**: `https://n8n.insightpulseai.com/webhook/mcp-insightpulse/sse`
- **Authentication**: Bearer token
- **Tool count**: 9 tools

### 4.3 Add Bearer Token

1. In the **Authentication** section, click **Add Token**
2. Paste bearer token from Step 2.1
3. Click **Save**

### 4.4 Test Connection

1. Click **Test Connection** button
2. Wait for SSE handshake to complete
3. Verify status shows "Connected ✅"

**If connection fails**, see Troubleshooting section below.

---

## Step 5: Test End-to-End Integration

### 5.1 Simple Read-Only Query

In Claude.ai chat, type:

```
List the 5 most recent Odoo invoices posted this month
```

**Expected behavior**:
1. Claude.ai calls `odoo_query` tool
2. n8n workflow executes
3. Results returned to Claude.ai
4. Claude.ai formats response as table

**Example response**:

| Invoice # | Partner | Date | Amount |
|-----------|---------|------|--------|
| INV/2026/00123 | Acme Corp | 2026-02-15 | ₱125,000 |
| INV/2026/00124 | Beta LLC | 2026-02-16 | ₱98,500 |
| ... | ... | ... | ... |

### 5.2 Finance Summary Query

```
Generate an AR aging report for February 2026
```

**Expected**: Claude.ai calls `finance_summary` tool and returns aging buckets.

### 5.3 Infrastructure Health Check

```
Check the health status of the Odoo production droplet
```

**Expected**: Claude.ai calls `infra_health` tool and returns CPU/memory/disk metrics.

---

## Step 6: Security Hardening

### 6.1 Restrict Write-Path Tools (Admin Only)

**Option A: Token-Based Access Control**

1. Generate separate admin token:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Store in Supabase Vault:
   ```sql
   INSERT INTO vault.secrets (name, secret, description)
   VALUES (
     'n8n_mcp_admin_token',
     'YOUR_ADMIN_TOKEN',
     'Admin-only bearer token for write-path MCP tools'
   );
   ```

3. Update write-path workflows to validate admin token:
   - Open `07_mcp_workflow_manager.json`
   - Modify token validation node
   - Accept both regular and admin tokens for read ops
   - Require admin token for write ops

**Option B: IP Allowlist**

Configure n8n firewall to restrict write-path endpoints:

```bash
# SSH to n8n droplet
ssh root@178.128.112.214

# Edit firewall rules
ufw allow from CLAUDE_AI_IP to any port 5678
```

### 6.2 Enable Audit Logging

Create Supabase table for MCP audit logs:

```sql
CREATE TABLE mcp_tool_invocations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tool_name TEXT NOT NULL,
  user_id TEXT,
  request_params JSONB,
  response_data JSONB,
  execution_time_ms INTEGER,
  status TEXT CHECK (status IN ('success', 'error')),
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE mcp_tool_invocations ENABLE ROW LEVEL SECURITY;

-- Admin-only access
CREATE POLICY "Admin read access" ON mcp_tool_invocations
  FOR SELECT USING (auth.jwt()->>'role' = 'admin');
```

### 6.3 Configure Rate Limiting

Add rate limiting to n8n workflows:

1. Install n8n rate limit plugin (if not present)
2. Configure limits per token:
   - **Standard token**: 60 requests/minute
   - **Admin token**: 120 requests/minute
3. Return `429 Too Many Requests` when exceeded

---

## Troubleshooting

### Issue: "Connection failed" in Claude.ai

**Symptoms**:
- Claude.ai shows "Failed to connect to custom connector"
- Test connection times out

**Solutions**:
1. Verify n8n is accessible: `curl https://n8n.insightpulseai.com/healthcheck`
2. Check bearer token matches Supabase Vault value
3. Ensure workflows are activated in n8n
4. Test SSE endpoint manually (Step 3.1)

---

### Issue: "Tool execution failed"

**Symptoms**:
- Claude.ai calls tool but returns error
- n8n execution log shows error

**Solutions**:
1. Check n8n execution logs: https://n8n.insightpulseai.com/executions
2. Verify Odoo XML-RPC credentials are correct
3. Check Supabase connection string is valid
4. Test workflow manually with sample payload

---

### Issue: "Unauthorized" (401 error)

**Symptoms**:
- Tool call returns 401 status code

**Solutions**:
1. Regenerate bearer token (Step 2)
2. Update token in Claude.ai connector settings
3. Update token in n8n variables
4. Verify token validation logic in workflows

---

### Issue: Slow response times

**Symptoms**:
- Queries take >10 seconds to complete

**Solutions**:
1. Reduce `limit` parameter in queries
2. Add more specific `domain` filters
3. Check n8n droplet resources: `ssh root@178.128.112.214 'htop'`
4. Optimize Odoo queries (add database indexes)

---

## Next Steps

### For End Users

1. **Explore examples**: See `examples/` directory for query templates
2. **Learn Odoo models**: Review Odoo documentation for available models
3. **Create custom queries**: Combine tools for complex workflows

### For Admins

1. **Monitor audit logs**: Regularly review `mcp_tool_invocations` table
2. **Rotate bearer tokens**: Monthly token rotation for security
3. **Optimize workflows**: Profile n8n executions for performance bottlenecks
4. **Add new tools**: Extend MCP with custom n8n workflows

---

## Support

### Documentation

- **Main docs**: `/odoo/docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`
- **Skill reference**: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/SKILL.md`
- **Workflow README**: `/odoo/automations/n8n/workflows/claude-ai-mcp/README.md`

### Contacts

- **n8n Admin**: devops@insightpulseai.com
- **Odoo Support**: odoo-support@insightpulseai.com
- **Technical Issues**: GitHub Issues (Insightpulseai/odoo)

---

*Setup guide version: 1.0*
*Last updated: 2026-02-20*
