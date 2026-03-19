---
name: claude-ai-n8n-connector
description: Claude.ai custom connector for querying Odoo SOR data and triggering n8n automation workflows via SSE transport
license: MIT
allowed-tools: []
---

# Claude.ai → n8n MCP Connector

> **Purpose**: Enable Claude.ai web interface users to query InsightPulse AI's Odoo System of Record (SOR) and trigger automation workflows through n8n webhooks.

---

## What This Skill Does

This skill provides Claude.ai users with **9 specialized tools** for:

1. **Odoo SOR Queries** (`odoo_query`): Fetch invoices, partners, products, and business data
2. **Supabase Operations** (`supabase_ops`): Execute SQL queries and RPC calls
3. **Finance Summaries** (`finance_summary`): Generate AR/AP aging, cash flow reports
4. **Infrastructure Health** (`infra_health`): Check DigitalOcean droplet status
5. **Workflow Monitoring** (`workflow_monitor`): Track n8n execution status
6. **Sync Triggers** (`sync_trigger`): Initiate SSOT/SOR data synchronization
7. **Workflow Management** (`workflow_manager`): Deploy/update n8n workflows
8. **GitHub Operations** (`github_ops`): Create issues, PRs, and commits
9. **Artifact Deployment** (`artifact_deployer`): Deploy to DigitalOcean App Platform

---

## When to Use This Skill

### Automatic Activation

This skill auto-activates when you mention:

- **Odoo queries**: "invoices posted this month", "customer list", "product catalog"
- **Finance reports**: "AR aging", "cash flow", "outstanding invoices"
- **Infrastructure**: "server health", "droplet status", "service uptime"
- **Automation**: "n8n workflows", "trigger sync", "deploy workflow"
- **GitHub**: "create issue", "open PR", "commit code"

### Manual Activation

Explicitly invoke the skill:

```
Use the claude-ai-n8n-connector skill to query Odoo invoices
```

---

## Prerequisites

### 1. n8n Workflows Deployed

All 9 workflows must be imported and activated at https://n8n.insightpulseai.com:

- `01_mcp_odoo_query.json`
- `02_mcp_supabase_ops.json`
- `03_mcp_finance_summary.json`
- `04_mcp_infra_health.json`
- `05_mcp_workflow_monitor.json`
- `06_mcp_sync_trigger.json`
- `07_mcp_workflow_manager.json`
- `08_mcp_github_ops.json`
- `09_mcp_artifact_deployer.json`

**Location**: `/odoo/automations/n8n/workflows/claude-ai-mcp/`

### 2. Bearer Token Configured

You need a bearer token for authentication:

**Generate token**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Store in Supabase Vault** (recommended):
```sql
INSERT INTO vault.secrets (name, secret)
VALUES ('n8n_mcp_bearer_token', 'YOUR_TOKEN_HERE');
```

### 3. Claude.ai Custom Connector Added

1. Claude.ai → Settings → Custom Connectors
2. Click "Add Connector"
3. Paste contents of `connector-config.json`
4. Add your bearer token

---

## Tool Reference

### Read-Only Tools (Safe for All Users)

#### `odoo_query` — Query Odoo System of Record

**Purpose**: Fetch business data from Odoo (invoices, partners, products, etc.)

**Parameters**:
- `model` (required): Odoo model name (e.g., `account.move`, `res.partner`)
- `domain` (optional): Search filter (e.g., `[['state', '=', 'posted']]`)
- `fields` (optional): Fields to retrieve (e.g., `['name', 'invoice_date', 'amount_total']`)
- `limit` (optional): Max records to return (default: 100)

**Example**:
```
Query Odoo invoices posted this month with amounts > $1000
```

**Behind the scenes**:
```json
{
  "model": "account.move",
  "domain": "[['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['invoice_date', '>=', '2026-02-01'], ['amount_total', '>', 1000]]",
  "fields": ["name", "partner_id", "invoice_date", "amount_total"],
  "limit": 100
}
```

---

#### `supabase_ops` — Execute Supabase SQL/RPC

**Purpose**: Run SQL queries or call stored procedures on Supabase PostgreSQL

**Parameters**:
- `operation` (required): `sql` or `rpc`
- `query` (required if operation=sql): SQL SELECT statement
- `function_name` (required if operation=rpc): RPC function name
- `params` (optional): RPC function parameters (JSON object)

**Example**:
```
Query Supabase for recent task completions in the last 7 days
```

**Behind the scenes**:
```json
{
  "operation": "sql",
  "query": "SELECT * FROM tasks WHERE completed_at > NOW() - INTERVAL '7 days' ORDER BY completed_at DESC LIMIT 50"
}
```

---

#### `finance_summary` — Generate Finance Reports

**Purpose**: Create AR aging, AP aging, cash flow, and reconciliation reports

**Parameters**:
- `report_type` (required): `ar_aging`, `ap_aging`, `cash_flow`, `reconciliation`
- `start_date` (optional): Report start date (YYYY-MM-DD)
- `end_date` (optional): Report end date (YYYY-MM-DD)
- `currency` (optional): Currency code (default: `PHP`)

**Example**:
```
Generate AR aging report for February 2026
```

**Behind the scenes**:
```json
{
  "report_type": "ar_aging",
  "start_date": "2026-02-01",
  "end_date": "2026-02-29",
  "currency": "PHP"
}
```

---

#### `infra_health` — Check Infrastructure Status

**Purpose**: Monitor DigitalOcean droplet health, disk usage, CPU, and service uptime

**Parameters**:
- `check_type` (required): `droplet`, `service`, `disk`, `network`
- `droplet_id` (optional): Specific droplet ID (default: primary droplet)

**Example**:
```
Check health of production Odoo droplet
```

**Behind the scenes**:
```json
{
  "check_type": "droplet",
  "droplet_id": "odoo-production"
}
```

---

#### `workflow_monitor` — Track n8n Execution Status

**Purpose**: Monitor workflow executions, success rates, and recent activity

**Parameters**:
- `action` (required): `list`, `status`, `stats`
- `workflow_id` (optional): Specific workflow ID
- `limit` (optional): Max executions to return (default: 20)

**Example**:
```
Show recent n8n workflow executions with errors
```

**Behind the scenes**:
```json
{
  "action": "list",
  "limit": 20
}
```

---

#### `sync_trigger` — Trigger SSOT/SOR Sync

**Purpose**: Initiate data synchronization between Supabase (SSOT) and Odoo (SOR)

**Parameters**:
- `sync_type` (required): `full`, `incremental`, `specific_model`
- `model` (optional): Odoo model to sync (if sync_type=specific_model)
- `direction` (optional): `ssot_to_sor`, `sor_to_ssot`, `bidirectional`

**Example**:
```
Trigger incremental sync from Supabase to Odoo
```

**Behind the scenes**:
```json
{
  "sync_type": "incremental",
  "direction": "ssot_to_sor"
}
```

---

### Write-Path Tools (Admin Only)

#### `workflow_manager` — Deploy n8n Workflows

**Purpose**: Create, update, or delete n8n workflows via API

**Parameters**:
- `action` (required): `create`, `update`, `delete`, `activate`, `deactivate`
- `workflow_id` (optional): Workflow ID (required for update/delete/activate/deactivate)
- `workflow_json` (optional): Workflow definition (required for create/update)

**Example**:
```
Deploy a new n8n workflow for invoice notification
```

**Security Note**: Requires admin bearer token with elevated permissions.

---

#### `github_ops` — GitHub Repository Operations

**Purpose**: Create issues, pull requests, and commits programmatically

**Parameters**:
- `operation` (required): `create_issue`, `create_pr`, `commit`
- `repo` (required): Repository name (e.g., `Insightpulseai/odoo`)
- `title` (optional): Issue/PR title
- `body` (optional): Issue/PR body
- `files` (optional): Files to commit (for commit operation)

**Example**:
```
Create a GitHub issue for missing RLS policies in Supabase
```

**Behind the scenes**:
```json
{
  "operation": "create_issue",
  "repo": "Insightpulseai/odoo",
  "title": "Missing RLS policies for user_tasks table",
  "body": "Supabase table `user_tasks` lacks Row-Level Security policies..."
}
```

---

#### `artifact_deployer` — Deploy to DigitalOcean

**Purpose**: Deploy applications to DigitalOcean App Platform

**Parameters**:
- `app_id` (required): DigitalOcean app ID
- `artifact_url` (required): URL to deployment artifact (Docker image or git ref)
- `environment` (optional): `production`, `staging`, `development`

**Example**:
```
Deploy latest Odoo module to staging environment
```

**Security Note**: Requires DigitalOcean API token with deployment permissions.

---

## Usage Examples

See the `examples/` directory for detailed query examples:

- **Odoo Queries**: `examples/odoo-query-examples.md`
- **Supabase Operations**: `examples/supabase-ops-examples.md`
- **Workflow Deployment**: `examples/workflow-deployment-examples.md`

---

## Setup Guide

Complete step-by-step setup instructions: `setup-guide.md`

Quick start:
1. Import 9 workflows to n8n
2. Generate bearer token
3. Add custom connector to Claude.ai
4. Test with sample query

---

## Troubleshooting

### "Tool execution failed" Error

**Symptom**: Claude.ai shows generic error message

**Solutions**:
1. Check n8n execution logs: https://n8n.insightpulseai.com/executions
2. Verify bearer token is correct
3. Ensure workflow is activated

### "Unauthorized" Error

**Symptom**: 401 response from n8n

**Solutions**:
1. Regenerate bearer token
2. Update token in Claude.ai connector settings
3. Verify token matches Supabase Vault value

### Slow Response Times

**Symptom**: Queries take >10 seconds

**Solutions**:
1. Reduce query limit parameter
2. Add more specific domain filters
3. Check n8n droplet CPU/memory usage

---

## Security Best Practices

1. **Never share bearer tokens** in chat logs or public channels
2. **Use read-only tools** for exploratory queries
3. **Restrict write-path tools** to admin users only
4. **Monitor audit logs** regularly for unusual activity
5. **Rotate bearer tokens** monthly or after team member changes

---

## Limitations

- **Rate limits**: 60 requests/minute per bearer token
- **Query timeout**: 30 seconds per tool invocation
- **Max results**: 1000 records per query (use pagination for more)
- **File upload**: Not supported (use GitHub ops for code changes)

---

## Integration with SuperClaude Framework

This skill integrates with:

- **Persona**: Backend, Analyzer, DevOps personas
- **MCP Servers**: Sequential (for complex queries), Context7 (for Odoo patterns)
- **Commands**: `/analyze`, `/query`, `/deploy`

---

*For implementation details, see: `/odoo/docs/ai/CLAUDE_AI_N8N_CONNECTOR.md`*
