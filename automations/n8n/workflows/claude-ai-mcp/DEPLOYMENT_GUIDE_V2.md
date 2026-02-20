# Claude.ai ↔ n8n MCP Integration - Deployment Guide (Instance-Level MCP)

> **Updated**: 2026-02-20 - Using n8n's built-in instance-level MCP server (simpler approach)

## Architecture Overview

n8n provides a **built-in instance-level MCP server** that exposes workflows as tools without requiring special trigger nodes. This is simpler than the per-workflow MCP Server Trigger approach.

```
Claude.ai Web
    ↓ (OAuth2 via built-in MCP connector)
n8n Instance-Level MCP Server
    ↓
Selected Workflows (marked "Available in MCP")
    ↓
Odoo / Supabase / DigitalOcean / GitHub
```

**Key Benefits**:
- ✅ No special trigger nodes required (use regular webhook/schedule/manual triggers)
- ✅ OAuth2 authentication handled automatically by n8n
- ✅ One connection covers all enabled workflows
- ✅ Workflows can be toggled on/off for MCP access individually

---

## Prerequisites

1. **n8n accessible at**: `https://n8n.insightpulseai.com` with valid SSL
2. **nginx reverse proxy configured** with SSE support (`proxy_buffering off`)
3. **Workflows already exist** in n8n (import if needed)
4. **n8n version** supports MCP (check instance version)

---

## Step 1: Enable MCP Access in n8n

### 1.1 Enable Instance-Level MCP Feature

1. Login to n8n: https://n8n.insightpulseai.com
2. Go to **Settings** → **MCP Access**
3. **Enable** the MCP feature toggle
4. Save settings

### 1.2 Mark Workflows as MCP-Available

**Option A: Per-Workflow Setting**

For each workflow you want to expose to Claude.ai:

1. Open the workflow in n8n editor
2. Click **"..."** menu (top-right) → **Settings**
3. Scroll to **MCP** section
4. Toggle **"Available in MCP"** → ON
5. Click **Save**
6. **Activate** workflow if not already active

**Option B: Bulk Enable via MCP Access Page**

1. Go to **Settings** → **MCP Access**
2. Click **"Enable workflows"**
3. Search and select workflows to expose
4. Click **"Enable selected"**

### 1.3 Recommended Workflows to Enable

Enable all 9 workflows for complete Claude.ai integration:

**Read-Only (Safe for General Use)**:
- [ ] `MCP Tool: Odoo Query (SOR Read-Only)`
- [ ] `MCP Tool: Supabase Ops (SSOT Query)`
- [ ] `MCP Tool: Finance Summary (Odoo SOR)`
- [ ] `MCP Tool: Infrastructure Health`
- [ ] `MCP Tool: Workflow Monitor`
- [ ] `MCP Tool: Sync Trigger (Outbox Pattern)`

**Write-Path (Admin Only)**:
- [ ] `MCP Tool: Workflow Manager` (admin only)
- [ ] `MCP Tool: GitHub Operations` (admin only)
- [ ] `MCP Tool: Artifact Deployer` (admin only)

---

## Step 2: Configure Claude.ai Custom Connector

### 2.1 Add n8n Connector in Claude.ai

1. Open https://claude.ai
2. Go to **Settings** → **Custom Connectors**
3. Click **"Add Connector"**

### 2.2 Paste Base URL

In the **Server URL** field, enter:

```
https://n8n.insightpulseai.com
```

**Important**: Use **base URL only** (no path suffix). n8n's built-in MCP server handles routing automatically.

### 2.3 Complete OAuth2 Authentication

1. Click **"Continue"**
2. n8n will prompt for OAuth2 authorization
3. **Authorize** Claude.ai to access your n8n instance
4. Connection status should show **"Connected"**

### 2.4 Verify Connected Workflows

In Claude.ai connector settings, you should see all MCP-enabled workflows listed as available tools.

---

## Step 3: Test Integration

### 3.1 Test Read-Only Query

In Claude.ai chat:

```
Query Odoo for invoices posted in February 2026
```

**Expected Behavior**:
- Claude.ai calls `odoo_query` tool via n8n MCP
- n8n executes "MCP Tool: Odoo Query" workflow
- Returns JSON with invoice records

### 3.2 Test Infrastructure Health Check

```
Check InsightPulseAI infrastructure health for all services
```

**Expected Behavior**:
- Claude.ai calls `infra_health` tool
- n8n executes "MCP Tool: Infrastructure Health" workflow
- Returns status for Odoo, Supabase, n8n, Superset

### 3.3 Test Sync Trigger (Dry Run)

```
Trigger a sync of Odoo invoices to Supabase in dry run mode
```

**Expected Behavior**:
- Claude.ai calls `sync_trigger` tool with `dry_run=true`
- n8n creates outbox preview without executing
- Returns preview JSON

---

## Step 4: Security & Access Control

### 4.1 MCP Access Scopes

n8n's instance-level MCP provides these security controls:

1. **Workflow-Level Toggle**: Only explicitly enabled workflows are exposed
2. **OAuth2 Authentication**: Automatic authentication via n8n's built-in flow
3. **User-Level Permissions**: Respects n8n user roles and workflow ownership
4. **Audit Logging**: All MCP calls logged in n8n execution history

### 4.2 Recommended Workflow Visibility

| Workflow Category | MCP Visibility | Rationale |
|-------------------|----------------|-----------|
| Read-Only Tools | ✅ Enabled | Safe for general Claude.ai users |
| Write-Path Tools | ⚠️ Admin Only | Requires elevated permissions |
| Internal Automation | ❌ Disabled | Should not be exposed to MCP |

### 4.3 Binary Data Limitation

**Important**: n8n MCP does not support binary input/output. Workflows that process files, images, or PDFs may not work correctly via MCP.

**Workaround**: Use URL-based file access instead of binary uploads.

---

## Comparison: Instance-Level vs MCP Server Trigger Nodes

| Feature | Instance-Level MCP (Recommended) | MCP Server Trigger Nodes |
|---------|----------------------------------|--------------------------|
| **Setup Complexity** | ✅ Simple (OAuth2 + toggle) | ❌ Complex (per-workflow SSE) |
| **Authentication** | ✅ OAuth2 (automatic) | ❌ Bearer token (manual) |
| **Workflow Changes** | ✅ None (use existing triggers) | ❌ Must add MCP trigger node |
| **Tool Discovery** | ✅ Automatic | ❌ Manual connector config |
| **Management** | ✅ Centralized (MCP Access page) | ❌ Per-workflow configuration |
| **OAuth2 Scope** | ✅ Supported | ❌ Not supported |
| **Binary Data** | ❌ Not supported | ❌ Not supported |

**Recommendation**: Use **instance-level MCP** (this guide) for all new integrations.

---

## Troubleshooting

### Issue: "Connection failed" in Claude.ai

**Cause**: n8n instance not reachable or SSL issues

**Fix**:
1. Verify n8n accessible: `curl https://n8n.insightpulseai.com/healthcheck`
2. Check SSL certificate is valid
3. Verify nginx reverse proxy is running: `systemctl status nginx` (on DO droplet)

### Issue: "Workflow not found" in MCP tool list

**Cause**: Workflow not marked "Available in MCP" or not activated

**Fix**:
1. Open workflow in n8n → Settings → toggle "Available in MCP"
2. Ensure workflow is **Activated** (green toggle in workflow list)
3. Refresh Claude.ai connector connection

### Issue: "OAuth2 authorization failed"

**Cause**: n8n OAuth2 configuration issue or network problem

**Fix**:
1. Check n8n OAuth2 settings in Settings → API
2. Verify redirect URLs are configured correctly
3. Try disconnecting and reconnecting Claude.ai connector

### Issue: "Tool execution failed"

**Cause**: Workflow error, missing credentials, or network issue

**Fix**:
1. Check n8n execution logs for detailed error
2. Verify credentials (Odoo XML-RPC, Supabase, GitHub tokens)
3. Test workflow manually in n8n with sample input
4. Check environment variables in n8n Settings → Variables

### Issue: "SSE support not working"

**Cause**: nginx reverse proxy buffering enabled

**Fix**:
1. Edit nginx config: `/etc/nginx/sites-available/n8n.insightpulseai.com`
2. Add `proxy_buffering off;` to location block
3. Reload nginx: `sudo systemctl reload nginx`

---

## Verification Checklist

- [ ] n8n MCP Access feature enabled
- [ ] 9 workflows marked "Available in MCP"
- [ ] All workflows activated (green toggle)
- [ ] Claude.ai connector added with base URL
- [ ] OAuth2 authentication completed
- [ ] Test query returns actual data
- [ ] n8n execution logs show successful runs
- [ ] Infrastructure health check returns service statuses
- [ ] Sync trigger dry run returns preview

---

## Migration from MCP Server Trigger Nodes

If you previously implemented MCP Server Trigger nodes, migrate to instance-level MCP:

### Migration Steps:

1. **Remove MCP Server Trigger nodes** from workflows
2. **Add regular triggers** (webhook, schedule, manual)
3. **Enable "Available in MCP"** for each workflow
4. **Test workflows** manually in n8n first
5. **Enable in Claude.ai** via OAuth2 connector
6. **Verify** tool discovery in Claude.ai

### Benefits of Migration:

- ✅ Simpler architecture (no custom trigger nodes)
- ✅ Automatic OAuth2 authentication
- ✅ Centralized management via MCP Access page
- ✅ Better error handling and logging
- ✅ Easier to add/remove workflows from MCP

---

## Next Steps After Successful Deployment

1. **Monitor Execution Logs**: Check n8n execution history for errors
2. **Usage Analytics**: Track which tools are most frequently called
3. **Security Audit**: Review OAuth2 scopes and workflow visibility
4. **Rate Limiting**: Monitor API usage to avoid hitting limits
5. **Documentation**: Create internal guide for common Claude.ai queries
6. **Training**: Educate team on available MCP tools and best practices

---

## References

- **n8n MCP Documentation**: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.mcpserver/
- **Claude.ai Custom Connectors**: https://claude.ai/settings/custom-connectors
- **OAuth2 Setup Guide**: n8n Settings → API → OAuth2
- **Workflow Examples**: `automations/n8n/workflows/claude-ai-mcp/examples/`

---

**Status**: Instance-level MCP approach (recommended)
**Last Updated**: 2026-02-20
**Owner**: InsightPulse AI DevOps Team
