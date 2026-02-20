# Claude.ai ↔ n8n MCP Integration - Deployment Guide

## Current Status

✅ **Completed**:
- 9 workflow JSONs created (6 read-only, 3 write-path)
- Claude.ai skill created with connector configuration
- 95+ query examples across 3 categories
- Comprehensive documentation

⏳ **Pending** (Manual Steps Required):
- Import workflows to n8n (API authentication issue - manual UI import recommended)
- Activate workflows in n8n
- Configure Claude.ai custom connector
- Test integration end-to-end

---

## Step 1: Import Workflows to n8n (Manual UI)

Since the n8n API authentication is not working with the provided key, import workflows manually via the n8n web interface:

### Import Process:

1. **Navigate to n8n**: https://n8n.insightpulseai.com
2. **Login** with admin credentials (`devops@insightpulseai.com`)
3. **For each workflow** (01-09):
   - Click **"+"** → **"Import from File"**
   - Select workflow JSON from:
     - **Read-only**: `automations/n8n/workflows/claude-ai-mcp/read-only/`
     - **Write-path**: `automations/n8n/workflows/claude-ai-mcp/write-path/`
   - Click **"Import"**
   - Click **"Activate"** toggle to enable workflow

### Workflow List:

**Read-Only Tools (6)**:
1. `01_mcp_odoo_query.json` - Odoo Query (SOR Read-Only)
2. `02_mcp_supabase_ops.json` - Supabase Ops (SSOT Query)
3. `03_mcp_finance_summary.json` - Finance Summary (Odoo SOR)
4. `04_mcp_infra_health.json` - Infrastructure Health
5. `05_mcp_workflow_monitor.json` - Workflow Monitor
6. `06_mcp_sync_trigger.json` - Sync Trigger (Outbox Pattern)

**Write-Path Tools (3)**:
7. `07_mcp_workflow_manager.json` - Workflow Manager
8. `08_mcp_github_ops.json` - GitHub Operations
9. `09_mcp_artifact_deployer.json` - Artifact Deployer

---

## Step 2: Verify n8n Workflows

After import and activation, verify all workflows are ready:

```bash
# Check if all 9 workflows are listed (requires working API key)
curl -s https://n8n.insightpulseai.com/api/v1/workflows \
  -H "x-n8n-api-key: YOUR_API_KEY" | \
  jq -r '.data[] | select(.name | startswith("MCP Tool:")) | "\(.name) - Active: \(.active)"'
```

Expected output:
```
MCP Tool: Odoo Query (SOR Read-Only) - Active: true
MCP Tool: Supabase Ops (SSOT Query) - Active: true
MCP Tool: Finance Summary (Odoo SOR) - Active: true
MCP Tool: Infrastructure Health - Active: true
MCP Tool: Workflow Monitor - Active: true
MCP Tool: Sync Trigger (Outbox Pattern) - Active: true
MCP Tool: Workflow Manager - Active: true
MCP Tool: GitHub Operations - Active: true
MCP Tool: Artifact Deployer - Active: true
```

---

## Step 3: Configure Claude.ai Custom Connector

### 3.1 Open Claude.ai Settings

1. Go to https://claude.ai
2. Click **Settings** → **Custom Connectors** → **Add Connector**

### 3.2 Paste Connector Configuration

Copy the connector configuration from:
`.claude/superclaude/skills/claude-ai-n8n-connector/connector-config.json`

**Key Configuration**:
```json
{
  "name": "InsightPulse n8n MCP",
  "transport": {
    "type": "sse",
    "url": "https://n8n.insightpulseai.com"
  }
}
```

**IMPORTANT**: Use **base URL only** (`https://n8n.insightpulseai.com`). The n8n MCP connector automatically handles the MCP protocol routing once workflows with MCP Server Trigger nodes are activated.

### 3.3 Add Bearer Token

When prompted for authentication:
- **Type**: Bearer Token
- **Token**: [Get from Supabase Vault or n8n API settings]

The token is stored in Supabase Vault on droplet 178.128.112.214.

---

## Step 4: Test Integration

### 4.1 Test Simple Query

In Claude.ai chat, try:
```
"Query Odoo for recent invoices posted this month"
```

Expected behavior:
- Claude.ai sends request to `odoo_query` tool
- n8n workflow `01_mcp_odoo_query` executes
- Returns JSON with invoice records

### 4.2 Test Infrastructure Health

```
"Check InsightPulseAI infrastructure health for all services"
```

Expected behavior:
- Calls `infra_health` tool with `check='all'`
- n8n workflow `04_mcp_infra_health` checks Odoo, Supabase, n8n, Superset
- Returns health status for each service

### 4.3 Test Sync Trigger (Dry Run)

```
"Trigger a sync of Odoo invoices to Supabase (dry run mode)"
```

Expected behavior:
- Calls `sync_trigger` tool with `sync_type='invoices'` and `dry_run=true`
- n8n workflow `06_mcp_sync_trigger` creates preview without executing
- Returns outbox entry preview

---

## Step 5: Verification Checklist

- [ ] All 9 workflows imported to n8n
- [ ] All 9 workflows activated (toggle ON)
- [ ] n8n MCP Server Trigger nodes configured with `path: "mcp-insightpulse"`
- [ ] n8n environment variables set:
  - `ODOO_URL`, `ODOO_DB`, `ODOO_UID`, `ODOO_API_KEY`
  - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
  - Other required credentials
- [ ] Claude.ai custom connector added with base URL `https://n8n.insightpulseai.com`
- [ ] Bearer token configured in Claude.ai connector
- [ ] Test query returns actual data (not error)
- [ ] Infrastructure health check returns service statuses
- [ ] Sync trigger dry run returns preview

---

## Troubleshooting

### Issue: "MCP server authorization error"

**Cause**: Bearer token missing or incorrect

**Fix**:
1. Get token from Supabase Vault or n8n API settings
2. Update Claude.ai connector authentication
3. Test connection again

### Issue: "Tool not found"

**Cause**: Workflow not activated or MCP Server Trigger node misconfigured

**Fix**:
1. Check workflow is activated in n8n UI
2. Verify MCP Server Trigger node has `path: "mcp-insightpulse"` and `authentication: "bearerAuth"`
3. Restart n8n if needed

### Issue: "Empty response"

**Cause**: Environment variables not set or Odoo/Supabase not accessible

**Fix**:
1. Check n8n environment variables in Settings → Variables
2. Test Odoo connectivity: `curl https://erp.insightpulseai.com/web/webclient/version_info`
3. Test Supabase connectivity: `curl https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/`

---

## Next Steps After Successful Deployment

1. **Create Usage Examples**: Document common query patterns in Claude.ai
2. **Monitor n8n Executions**: Check workflow execution logs for errors
3. **Audit Trail**: All MCP tool calls are logged in n8n execution history
4. **Rate Limiting**: Monitor API usage to avoid hitting n8n/Odoo/Supabase rate limits
5. **Security**: Rotate Bearer tokens quarterly, audit MCP tool access logs

---

## Architecture Reference

See comprehensive documentation:
- **Integration Guide**: `docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`
- **Query Examples**: `.claude/superclaude/skills/claude-ai-n8n-connector/examples/`
- **Workflow README**: `automations/n8n/workflows/claude-ai-mcp/README.md`
- **Setup Guide**: `.claude/superclaude/skills/claude-ai-n8n-connector/setup-guide.md`

---

**Last Updated**: 2026-02-20
**Status**: Manual import required (API auth pending)
