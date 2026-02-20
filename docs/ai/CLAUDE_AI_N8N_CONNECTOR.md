# Claude.ai ↔ n8n MCP Integration

> **Purpose**: Enable Claude.ai web interface to query Odoo SOR data and trigger n8n automation workflows via SSE transport.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Components](#components)
3. [Setup Instructions](#setup-instructions)
4. [Tool Reference](#tool-reference)
5. [Security & Compliance](#security--compliance)
6. [Troubleshooting](#troubleshooting)
7. [Migration Notes](#migration-notes)

---

## Architecture Overview

### System Diagram

```
┌─────────────────┐
│  Claude.ai Web  │
│   (User Query)  │
└────────┬────────┘
         │ HTTPS (SSE)
         │ Authorization: Bearer <token>
         ▼
┌─────────────────┐
│  n8n Workflows  │
│  (9 SSE Tools)  │
└────────┬────────┘
         │
    ┌────┴─────┬────────┬────────────┬─────────┐
    ▼          ▼        ▼            ▼         ▼
┌───────┐  ┌────────┐ ┌──────────┐ ┌──────┐  ┌────────┐
│ Odoo  │  │Supabase│ │ DO Infra │ │GitHub│  │ Slack  │
│ SOR   │  │  SSOT  │ │ (Droplet)│ │ API  │  │Webhook │
└───────┘  └────────┘ └──────────┘ └──────┘  └────────┘
```

### Transport Comparison

| Feature | Python MCP Server | SSE MCP Endpoints |
|---------|------------------|-------------------|
| **Transport** | stdio | Server-Sent Events (SSE) |
| **Auth** | N/A (local only) | Bearer token |
| **Client** | Claude Code CLI | Claude.ai web interface |
| **Use Case** | Local development | Cloud-based integration |
| **Tools** | 6 (workflow CRUD) | 9 (query + deploy) |
| **Location** | `agents/mcp/n8n-mcp/` | `automations/n8n/workflows/claude-ai-mcp/` |

### Key Differences

1. **Python MCP Server** (`server.py`):
   - Used by Claude Code CLI locally
   - stdio transport (standard input/output)
   - No authentication required (local machine only)
   - Focus: n8n workflow management (CRUD operations)

2. **SSE MCP Endpoints** (these workflows):
   - Used by Claude.ai web interface
   - SSE transport (Server-Sent Events over HTTPS)
   - Bearer token authentication required
   - Focus: Odoo/Supabase queries + deployment automation

---

## Components

### Workflow Files

Located at: `/odoo/automations/n8n/workflows/claude-ai-mcp/`

#### Read-Only Tools (01-06)

| File | Tool Name | Purpose | Endpoint |
|------|-----------|---------|----------|
| `01_mcp_odoo_query.json` | `odoo_query` | Query Odoo invoices, partners, products | `/webhook/mcp-odoo-query` |
| `02_mcp_supabase_ops.json` | `supabase_ops` | Execute SQL queries and RPC calls | `/webhook/mcp-supabase-ops` |
| `03_mcp_finance_summary.json` | `finance_summary` | Generate AR/AP aging, cash flow reports | `/webhook/mcp-finance-summary` |
| `04_mcp_infra_health.json` | `infra_health` | Check DigitalOcean droplet health | `/webhook/mcp-infra-health` |
| `05_mcp_workflow_monitor.json` | `workflow_monitor` | Monitor n8n execution status | `/webhook/mcp-workflow-monitor` |
| `06_mcp_sync_trigger.json` | `sync_trigger` | Trigger SSOT/SOR data sync | `/webhook/mcp-sync-trigger` |

#### Write-Path Tools (07-09) — Admin Only

| File | Tool Name | Purpose | Endpoint |
|------|-----------|---------|----------|
| `07_mcp_workflow_manager.json` | `workflow_manager` | Deploy/update n8n workflows | `/webhook/mcp-workflow-manager` |
| `08_mcp_github_ops.json` | `github_ops` | Create issues, PRs, commits | `/webhook/mcp-github-ops` |
| `09_mcp_artifact_deployer.json` | `artifact_deployer` | Deploy to DO App Platform | `/webhook/mcp-artifact-deployer` |

### Claude.ai Skill

Located at: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/`

**Files**:
- `SKILL.md` — Skill definition and usage instructions
- `connector-config.json` — Claude.ai custom connector JSON (9 tools)
- `setup-guide.md` — Step-by-step setup instructions
- `examples/` — Query examples for each tool category

---

## Setup Instructions

### Prerequisites

1. ✅ Access to https://n8n.insightpulseai.com (admin credentials)
2. ✅ Claude.ai account with custom connector feature enabled
3. ✅ Supabase Vault access for secure token storage
4. ✅ n8n workflows repository cloned locally

### Step 1: Import n8n Workflows

1. Navigate to https://n8n.insightpulseai.com
2. Workflows → Import from File
3. Select all 9 JSON files from `automations/n8n/workflows/claude-ai-mcp/`
4. Activate each workflow after import

### Step 2: Generate Bearer Token

```bash
# Generate secure random token
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Store in Supabase Vault
psql $SUPABASE_DB_URL <<SQL
INSERT INTO vault.secrets (name, secret, description)
VALUES (
  'n8n_mcp_bearer_token',
  'YOUR_TOKEN_HERE',
  'Bearer token for Claude.ai → n8n MCP integration'
);
SQL
```

### Step 3: Configure n8n

1. n8n → Settings → Variables
2. Add variable:
   - **Name**: `MCP_BEARER_TOKEN`
   - **Value**: (paste token from Step 2)
3. Save

### Step 4: Test SSE Endpoint

```bash
curl -N -H "Authorization: Bearer YOUR_TOKEN" \
  https://n8n.insightpulseai.com/webhook/mcp-insightpulse/sse
```

**Expected**: SSE event stream with `event: endpoint` message

### Step 5: Configure Claude.ai

1. Claude.ai → Settings → Custom Connectors → Add Connector
2. Paste contents of `connector-config.json`
3. Add bearer token
4. Test connection

### Step 6: End-to-End Test

In Claude.ai chat:
```
List the 5 most recent Odoo invoices posted this month
```

**Expected**: Claude calls `odoo_query` tool and returns formatted results.

**Detailed setup guide**: `/.claude/superclaude/skills/claude-ai-n8n-connector/setup-guide.md`

---

## Tool Reference

### Read-Only Tools

#### `odoo_query`

**Purpose**: Query Odoo System of Record for business data

**Parameters**:
- `model` (required): Odoo model name (e.g., `account.move`, `res.partner`)
- `domain` (optional): Search filter (Odoo domain format)
- `fields` (optional): Fields to retrieve (array of strings)
- `limit` (optional): Max records (default: 100, max: 1000)

**Example queries**:
- "Show recent invoices posted this month"
- "List all customers in Manila"
- "Find products with low stock levels"

**Details**: `/.claude/superclaude/skills/claude-ai-n8n-connector/examples/odoo-query-examples.md`

---

#### `supabase_ops`

**Purpose**: Execute SQL queries or RPC calls on Supabase PostgreSQL

**Parameters**:
- `operation` (required): `sql` or `rpc`
- `query` (required if sql): SQL SELECT statement (read-only)
- `function_name` (required if rpc): RPC function name
- `params` (optional): RPC function parameters (JSON object)

**Example queries**:
- "Show tasks completed in the last 7 days"
- "Get user activity statistics for February"
- "Calculate AR aging buckets"

**Details**: `/.claude/superclaude/skills/claude-ai-n8n-connector/examples/supabase-ops-examples.md`

---

#### `finance_summary`

**Purpose**: Generate finance reports (AR aging, AP aging, cash flow)

**Parameters**:
- `report_type` (required): `ar_aging`, `ap_aging`, `cash_flow`, `reconciliation`, `trial_balance`
- `start_date` (optional): Report start (YYYY-MM-DD)
- `end_date` (optional): Report end (YYYY-MM-DD)
- `currency` (optional): Currency code (default: `PHP`)

**Example queries**:
- "Generate AR aging report for February 2026"
- "Show cash flow summary for Q1"
- "Create trial balance as of today"

---

#### `infra_health`

**Purpose**: Check infrastructure health status (DigitalOcean droplets)

**Parameters**:
- `check_type` (required): `droplet`, `service`, `disk`, `network`, `all`
- `droplet_id` (optional): Specific droplet (default: `odoo-production`)

**Example queries**:
- "Check health of production Odoo droplet"
- "Show disk usage on all servers"
- "Verify network connectivity to Supabase"

---

#### `workflow_monitor`

**Purpose**: Monitor n8n workflow executions and success rates

**Parameters**:
- `action` (required): `list`, `status`, `stats`, `errors`
- `workflow_id` (optional): Specific workflow ID
- `limit` (optional): Max executions (default: 20)

**Example queries**:
- "Show recent n8n workflow executions with errors"
- "Get success rate statistics for invoice sync workflow"
- "List all failed executions today"

---

#### `sync_trigger`

**Purpose**: Trigger SSOT/SOR data synchronization

**Parameters**:
- `sync_type` (required): `full`, `incremental`, `specific_model`
- `model` (optional): Odoo model to sync (if specific_model)
- `direction` (optional): `ssot_to_sor`, `sor_to_ssot`, `bidirectional`

**Example queries**:
- "Trigger incremental sync from Supabase to Odoo"
- "Full sync of invoice data bidirectionally"
- "Sync only the products table from Odoo to Supabase"

---

### Write-Path Tools (Admin Only)

#### `workflow_manager`

**Purpose**: Deploy, update, or delete n8n workflows via API

**Parameters**:
- `action` (required): `create`, `update`, `delete`, `activate`, `deactivate`
- `workflow_id` (optional): Workflow ID (required for update/delete/activate/deactivate)
- `workflow_json` (optional): Workflow definition (required for create/update)

**Security**: Requires admin bearer token with elevated permissions

**Details**: `/.claude/superclaude/skills/claude-ai-n8n-connector/examples/workflow-deployment-examples.md`

---

#### `github_ops`

**Purpose**: Create GitHub issues, pull requests, and commits

**Parameters**:
- `operation` (required): `create_issue`, `create_pr`, `commit`, `merge_pr`
- `repo` (required): Repository name (`owner/repo` format)
- `title` (optional): Issue/PR title
- `body` (optional): Issue/PR body (Markdown supported)
- `files` (optional): Files to commit (array of {path, content})
- `branch` (optional): Branch name (for commit/PR operations)

**Security**: Requires admin bearer token + GitHub PAT

---

#### `artifact_deployer`

**Purpose**: Deploy artifacts to DigitalOcean App Platform

**Parameters**:
- `app_id` (required): DigitalOcean app identifier
- `artifact_url` (required): Docker image URL or git reference
- `environment` (optional): `production`, `staging`, `development` (default: `staging`)
- `force_rebuild` (optional): Force rebuild from source (default: `false`)

**Security**: Requires admin bearer token + DigitalOcean API token

---

## Security & Compliance

### Authentication

**Bearer Token Storage**:
- **Primary**: Supabase Vault (`vault.secrets` table)
- **Backup**: n8n environment variables (encrypted)
- **Never**: Git commits, plain text files, chat logs

**Token Types**:
1. **Standard Token**: Read-only tools (01-06) access
2. **Admin Token**: Full access including write-path tools (07-09)

### Authorization

**Read-Only Tools** (Safe for all users):
- ✅ `odoo_query`
- ✅ `supabase_ops`
- ✅ `finance_summary`
- ✅ `infra_health`
- ✅ `workflow_monitor`
- ✅ `sync_trigger`

**Write-Path Tools** (Admin only):
- 🔒 `workflow_manager`
- 🔒 `github_ops`
- 🔒 `artifact_deployer`

**Access Control**:
- n8n workflows validate bearer token on every request
- Admin tools require separate admin token (higher privileges)
- Audit logging captures all tool invocations

### Audit Logging

**Supabase Table**: `mcp_tool_invocations`

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
```

**Logged Data**:
- Tool name and parameters
- User ID (from bearer token)
- Request/response payloads
- Execution time and status
- Error messages (if failed)

**Retention**: 90 days (configurable)

### Rate Limiting

**Default Limits**:
- **Standard Token**: 60 requests/minute
- **Admin Token**: 120 requests/minute
- **Burst**: 10 requests/second (short duration)

**Exceeded Limit Response**:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

### Compliance

**Data Protection**:
- ✅ GDPR-compliant audit logging
- ✅ PII handling via Row-Level Security (RLS)
- ✅ Encrypted bearer tokens in Vault
- ✅ TLS 1.3 for all HTTPS connections

**Security Best Practices**:
1. **Monthly token rotation** for all bearer tokens
2. **Admin token** separate from standard token
3. **IP allowlist** for write-path endpoints (optional)
4. **Regular audit log reviews** for anomaly detection

---

## Troubleshooting

### Connection Failed in Claude.ai

**Symptoms**:
- "Failed to connect to custom connector"
- Test connection times out

**Solutions**:
1. Verify n8n is accessible: `curl https://n8n.insightpulseai.com/healthcheck`
2. Check bearer token matches Supabase Vault value
3. Ensure workflows are activated in n8n
4. Test SSE endpoint manually with `curl -N`

---

### Tool Execution Failed

**Symptoms**:
- Claude.ai shows "tool execution failed"
- n8n execution log shows error

**Solutions**:
1. Check n8n execution logs: https://n8n.insightpulseai.com/executions
2. Verify Odoo XML-RPC credentials are correct
3. Check Supabase connection string is valid
4. Test workflow manually with sample payload

**Common Errors**:
- `401 Unauthorized`: Bearer token mismatch
- `403 Forbidden`: Admin token required for write-path tool
- `500 Internal Server Error`: Odoo/Supabase connection issue
- `504 Gateway Timeout`: Query took too long (>30s)

---

### Slow Response Times

**Symptoms**:
- Queries take >10 seconds to complete

**Solutions**:
1. Reduce `limit` parameter in queries
2. Add more specific `domain` filters
3. Check n8n droplet resources: `ssh root@178.128.112.214 'htop'`
4. Optimize Odoo queries (add database indexes)

**Performance Benchmarks**:
- `odoo_query`: <5s for 100 records
- `supabase_ops`: <2s for SQL queries
- `finance_summary`: <10s for monthly reports
- `workflow_monitor`: <3s for 20 executions

---

### Unauthorized (401) Error

**Symptoms**:
- Tool call returns 401 status code
- n8n logs show "Invalid bearer token"

**Solutions**:
1. Regenerate bearer token (see Setup Step 2)
2. Update token in Claude.ai connector settings
3. Update token in n8n variables
4. Verify token validation logic in workflows

**Token Validation Flow**:
```
1. Claude.ai sends Authorization: Bearer <token>
2. n8n workflow reads header
3. Compare with MCP_BEARER_TOKEN variable
4. If match → proceed, else → return 401
```

---

## Migration Notes

### From Python MCP Server to SSE Endpoints

**If you're currently using** `agents/mcp/n8n-mcp/server.py`:

#### Coexistence Strategy

Both transport methods can coexist:
- **Local development**: Continue using Python MCP server via Claude Code CLI
- **Cloud usage**: Add SSE endpoints for Claude.ai web interface

#### Equivalent Tools

| Python MCP Server | SSE Workflow |
|------------------|--------------|
| `trigger_workflow` | `sync_trigger` |
| `check_execution` | `workflow_monitor` |
| `list_workflows` | `workflow_monitor` |
| `create_workflow` | `workflow_manager` |
| `update_workflow` | `workflow_manager` |
| `delete_workflow` | `workflow_manager` |

#### Migration Steps

1. **Keep Python MCP server** for local Claude Code CLI usage
2. **Import SSE workflows** for Claude.ai web access
3. **Generate separate bearer token** for SSE authentication
4. **Test both environments** independently
5. **No code changes required** in existing scripts

---

## Maintenance

### Adding New MCP Tools

1. Create new n8n workflow with SSE response format
2. Add tool definition to `connector-config.json`
3. Update this documentation with tool description
4. Deploy workflow to n8n production instance
5. Test with Claude.ai

**Template Workflow Structure**:
```json
{
  "name": "MCP Tool: Your Tool Name",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook Trigger",
      "parameters": {
        "path": "your-tool-endpoint",
        "responseMode": "onReceived"
      }
    },
    {
      "type": "n8n-nodes-base.function",
      "name": "Validate Bearer Token",
      "parameters": {
        "functionCode": "// Token validation logic"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Execute Operation",
      "parameters": {
        "url": "{{ $json.target_url }}",
        "method": "POST"
      }
    },
    {
      "type": "n8n-nodes-base.respondToWebhook",
      "name": "Return SSE Response",
      "parameters": {
        "options": {
          "responseHeaders": {
            "Content-Type": "text/event-stream"
          }
        }
      }
    }
  ]
}
```

### Updating Existing Tools

1. Edit workflow JSON locally
2. Import updated workflow to n8n (overwrites existing)
3. Test with sample Claude.ai query
4. Commit changes to git with changelog

### Token Rotation Schedule

**Monthly rotation** (recommended):
1. Generate new bearer token
2. Update Supabase Vault value
3. Update n8n environment variable
4. Update Claude.ai connector settings
5. Test all tools
6. Deactivate old token after 48-hour grace period

---

## Resources

### Documentation

- **This file**: `/odoo/docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`
- **Skill reference**: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/SKILL.md`
- **Setup guide**: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/setup-guide.md`
- **Workflow README**: `/odoo/automations/n8n/workflows/claude-ai-mcp/README.md`
- **Python MCP server**: `/odoo/agents/mcp/n8n-mcp/README.md`

### Examples

- **Odoo queries**: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/examples/odoo-query-examples.md`
- **Supabase ops**: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/examples/supabase-ops-examples.md`
- **Workflow deployment**: `/odoo/.claude/superclaude/skills/claude-ai-n8n-connector/examples/workflow-deployment-examples.md`

### Support Contacts

- **n8n Admin**: devops@insightpulseai.com
- **Odoo Support**: odoo-support@insightpulseai.com
- **Technical Issues**: GitHub Issues (`Insightpulseai/odoo`)
- **Security Concerns**: security@insightpulseai.com

---

*Last updated: 2026-02-20*
*Document version: 1.0*
*Owner: InsightPulse AI DevOps Team*
