# Claude.ai ↔ n8n MCP Integration

> **Purpose**: SSE-based MCP tools enabling Claude.ai web interface to query Odoo/Supabase data and trigger n8n workflows.

---

## 🚀 Deployment Status

⏳ **Current Phase**: Workflows created, awaiting manual import to n8n

**Completed**:
- ✅ 9 workflow JSONs created (6 read-only + 3 write-path)
- ✅ Claude.ai skill with connector configuration
- ✅ 95+ query examples across 3 categories
- ✅ Comprehensive documentation

**Next Steps**:
- ⏳ Import workflows to n8n via web UI (manual)
- ⏳ Activate all 9 workflows
- ⏳ Configure Claude.ai custom connector with base URL
- ⏳ Test integration end-to-end

👉 **See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete setup instructions**

**Note**: n8n API import attempted but encountered authentication issues. Manual UI import is recommended.

---

## Architecture Overview

```
Claude.ai Web
    ↓ (SSE + Bearer auth)
n8n Webhook Endpoints
    ↓
Odoo / Supabase / DigitalOcean / GitHub
```

### Transport Comparison

| Feature | Python MCP Server (`server.py`) | SSE MCP Endpoints (these workflows) |
|---------|--------------------------------|-------------------------------------|
| **Transport** | stdio | Server-Sent Events (SSE) |
| **Auth** | N/A (local only) | Bearer token |
| **Client** | Claude Code CLI | Claude.ai web interface |
| **Use Case** | Local development | Cloud-based Claude.ai integration |
| **Tools** | 6 (trigger, check, list, create, update, delete) | 9 (query, ops, deploy) |

---

## Workflow Categories

### Read-Only Tools (01-06)

Query Odoo SOR data and infrastructure status without modifications.

| Workflow | Purpose | Endpoint |
|----------|---------|----------|
| `01_mcp_odoo_query.json` | Query Odoo invoices, partners, products via XML-RPC | `/webhook/mcp-odoo-query` |
| `02_mcp_supabase_ops.json` | Execute Supabase SQL queries and RPC calls | `/webhook/mcp-supabase-ops` |
| `03_mcp_finance_summary.json` | Generate finance summaries from Odoo SOR | `/webhook/mcp-finance-summary` |
| `04_mcp_infra_health.json` | Check DigitalOcean droplet and service health | `/webhook/mcp-infra-health` |
| `05_mcp_workflow_monitor.json` | Monitor n8n workflow execution status | `/webhook/mcp-workflow-monitor` |
| `06_mcp_sync_trigger.json` | Trigger SSOT/SOR sync workflows | `/webhook/mcp-sync-trigger` |

### Write-Path Tools (07-09)

Deploy workflows, create GitHub artifacts, and manage automation infrastructure.

| Workflow | Purpose | Endpoint |
|----------|---------|----------|
| `07_mcp_workflow_manager.json` | Deploy and manage n8n workflows via API | `/webhook/mcp-workflow-manager` |
| `08_mcp_github_ops.json` | Create GitHub issues, PRs, and commits | `/webhook/mcp-github-ops` |
| `09_mcp_artifact_deployer.json` | Deploy artifacts to DigitalOcean App Platform | `/webhook/mcp-artifact-deployer` |

---

## Setup Instructions

### 1. Import Workflows to n8n

1. Navigate to https://n8n.insightpulseai.com
2. Workflows → Import from File
3. Select all 9 JSON files
4. Activate each workflow after import

### 2. Configure Bearer Token

**Option A: Supabase Vault (recommended)**

```sql
-- Store bearer token in Supabase Vault
INSERT INTO vault.secrets (name, secret)
VALUES ('n8n_mcp_bearer_token', 'YOUR_SECURE_TOKEN_HERE');
```

**Option B: n8n Environment Variable**

1. n8n → Settings → Variables
2. Add `MCP_BEARER_TOKEN` with secure random value

### 3. Generate Bearer Token

```bash
# Generate secure random token
openssl rand -hex 32

# Or use Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Test SSE Endpoint

```bash
# Test SSE connection
curl -N -H "Authorization: Bearer YOUR_TOKEN" \
  https://n8n.insightpulseai.com/webhook/mcp-insightpulse/sse
```

Expected: SSE event stream with `event: endpoint` message

---

## Security Considerations

### Authentication

- **Bearer token required** for all endpoints
- Token stored in Supabase Vault (never committed to git)
- n8n validates token on every request

### Authorization

- **Read-only tools** (01-06): Safe for general use
- **Write-path tools** (07-09): Restricted to admin users only

### Audit Logging

All MCP tool invocations are logged to:
- n8n execution logs (webhook activity)
- Supabase audit table (`mcp_tool_invocations`)

### Rate Limiting

- **Default**: 60 requests/minute per bearer token
- **Burst**: 10 requests/second

---

## Integration with Claude.ai

See the skill directory for complete setup:
- **Skill**: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/`
- **Connector Config**: `connector-config.json`
- **Setup Guide**: `setup-guide.md`

---

## Troubleshooting

### SSE Connection Fails

**Symptom**: `curl` times out or returns 401

**Solutions**:
1. Verify bearer token matches n8n configuration
2. Check workflow is activated in n8n
3. Verify n8n URL is accessible: `curl https://n8n.insightpulseai.com/healthcheck`

### Tool Invocation Returns Error

**Symptom**: Claude.ai shows "tool execution failed"

**Solutions**:
1. Check n8n execution logs for error details
2. Verify credentials (Odoo XML-RPC, Supabase, GitHub)
3. Test workflow manually in n8n with sample payload

### Workflow Not Found

**Symptom**: 404 error from n8n webhook

**Solutions**:
1. Verify workflow is imported and activated
2. Check webhook path matches connector config
3. Ensure n8n is running: `systemctl status n8n` (on DO droplet)

---

## Migration from Python MCP Server

If migrating from `agents/mcp/n8n-mcp/server.py`:

### Coexistence Strategy

Both transport methods can coexist:
- **Local development**: Use Python MCP server via stdio
- **Cloud usage**: Use SSE endpoints via Claude.ai

### Equivalent Tools

| Python MCP Tool | SSE Workflow Equivalent |
|----------------|------------------------|
| `trigger_workflow` | `06_mcp_sync_trigger.json` |
| `check_execution` | `05_mcp_workflow_monitor.json` |
| `list_workflows` | `05_mcp_workflow_monitor.json` |
| `create_workflow` | `07_mcp_workflow_manager.json` |
| `update_workflow` | `07_mcp_workflow_manager.json` |
| `delete_workflow` | `07_mcp_workflow_manager.json` |

---

## Maintenance

### Adding New MCP Tools

1. Create new n8n workflow with SSE response format
2. Add tool definition to `connector-config.json`
3. Update this README with tool description
4. Deploy workflow to n8n production instance

### Updating Existing Tools

1. Edit workflow JSON locally
2. Import updated workflow to n8n
3. Test with sample Claude.ai query
4. Commit changes to git with changelog

---

*Last updated: 2026-02-20*
*Owner: InsightPulse AI DevOps Team*
