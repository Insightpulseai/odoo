# n8n Integration

## Overview

n8n is our workflow automation platform, enabling no-code/low-code automation between Odoo and external services.

**Production URL:** https://n8n.insightpulseai.net

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       n8n Integration                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Odoo CE                          ipai-ops-stack                │
│   ┌────────────────────┐           ┌──────────────────────┐     │
│   │ ipai_integrations  │           │   n8n Server         │     │
│   │ - Connector config │◄─────────►│   (Docker)           │     │
│   │ - Webhooks         │   REST    │                      │     │
│   └────────────────────┘           │   PostgreSQL/SQLite  │     │
│   ┌────────────────────┐           │                      │     │
│   │ ipai_n8n_connector │           │   Redis (queue)      │     │
│   │ - API client       │           └──────────────────────┘     │
│   │ - Workflow sync    │                                        │
│   │ - Execution logs   │           ┌──────────────────────┐     │
│   │ - Webhook handlers │           │   n8n/workflows/     │     │
│   └────────────────────┘           │   (JSON exports)     │     │
│                                    └──────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Odoo Modules

### ipai_n8n_connector

n8n-specific functionality:
- API client (`N8nClient`)
- Workflow synchronization
- Execution tracking
- Webhook callbacks from n8n
- Odoo action triggers from n8n

## Configuration

### 1. System Parameters

Set these in Odoo (Settings > Technical > Parameters > System Parameters):

| Key | Description |
|-----|-------------|
| `ipai_integrations.n8n_url` | Base URL (default: https://n8n.insightpulseai.net) |
| `ipai_n8n.api_key_{connector_id}` | n8n API key |

### 2. Create Connector

1. Go to **Integrations > Configuration > Connectors**
2. Create new connector:
   - Name: n8n (InsightPulse AI)
   - Type: n8n
   - Base URL: https://n8n.insightpulseai.net
   - Auth Type: Token (API Key)
3. Set the API key in System Parameters
4. Click **Test Connection**
5. If successful, click **Activate**

### 3. Sync Workflows

1. Go to **Integrations > n8n > Workflows**
2. The connector auto-creates a sync action
3. Click **Sync Workflows** to import from n8n
4. Workflows with webhook triggers can be triggered from Odoo

## Workflow Patterns

### Pattern 1: Odoo → n8n (Trigger Workflow)

Odoo triggers an n8n workflow via webhook:

```python
# In Odoo code
connector = self.env["ipai.integration.connector"].search([
    ("connector_type", "=", "n8n"),
    ("state", "=", "active"),
], limit=1)

if connector:
    connector.n8n_trigger_webhook(
        "/webhook/odoo-task-created",
        {"task_id": self.id, "name": self.name}
    )
```

### Pattern 2: n8n → Odoo (Callback)

n8n calls back to Odoo with results:

**n8n HTTP Request Node:**
- URL: `https://your-odoo.com/integrations/n8n/callback`
- Method: POST
- Body:
```json
{
  "workflow_id": "{{ $workflow.id }}",
  "execution_id": "{{ $execution.id }}",
  "status": "success",
  "data": { "result": "..." }
}
```

### Pattern 3: n8n → Odoo (CRUD Operations)

n8n can create/update Odoo records:

**Create Record:**
- URL: `https://your-odoo.com/integrations/n8n/trigger/create_record`
- Body:
```json
{
  "model": "project.task",
  "values": {
    "name": "New Task from n8n",
    "project_id": 1
  }
}
```

**Update Record:**
- URL: `https://your-odoo.com/integrations/n8n/trigger/update_record`
- Body:
```json
{
  "model": "project.task",
  "record_id": 123,
  "values": {"stage_id": 2}
}
```

## API Usage

### Sync Workflows

```python
connector = self.env["ipai.integration.connector"].search([
    ("connector_type", "=", "n8n"),
    ("state", "=", "active"),
], limit=1)

if connector:
    connector.n8n_sync_workflows()
```

### Trigger Workflow

```python
workflow = self.env["ipai.n8n.workflow"].browse(workflow_id)
workflow.action_trigger()
```

### Check Executions

```python
workflow = self.env["ipai.n8n.workflow"].browse(workflow_id)
for execution in workflow.execution_ids[:10]:
    print(f"{execution.create_date}: {execution.status}")
```

## Workflow Storage

Workflows are stored as JSON exports in the ops repo:

```
ipai-ops-stack/
  n8n/
    workflows/
      odoo-task-sync.json
      finance-approval.json
      ...
    bootstrap/
      import_workflows.sh
```

### Export Workflow

1. In n8n UI: Workflow > Export
2. Save JSON to `ipai-ops-stack/n8n/workflows/`
3. Commit and push

### Import Workflows

```bash
# In ipai-ops-stack
./n8n/bootstrap/import_workflows.sh
```

## Data Model

### ipai.n8n.workflow

| Field | Type | Description |
|-------|------|-------------|
| `n8n_workflow_id` | Char | n8n workflow ID |
| `name` | Char | Workflow name |
| `trigger_type` | Selection | webhook/schedule/manual/event |
| `webhook_path` | Char | Webhook trigger path |
| `active_in_n8n` | Boolean | Active in n8n |

### ipai.n8n.execution

| Field | Type | Description |
|-------|------|-------------|
| `n8n_execution_id` | Char | n8n execution ID |
| `workflow_id` | Many2one | Linked workflow |
| `status` | Selection | waiting/running/success/error |
| `input_data` | Text | Input JSON |
| `output_data` | Text | Output JSON |

## Security

### Webhook Authentication

For n8n → Odoo webhooks, implement signature validation:

1. Set a shared secret in both systems
2. n8n sends `X-N8N-Signature` header
3. Odoo validates HMAC signature

### Allowed Methods

The `run_method` action only allows methods with these prefixes:
- `action_` (action methods)
- `button_` (button methods)
- `_handle_` (handler methods)

## Troubleshooting

### Connection Failed

1. Verify n8n is running: `curl https://n8n.insightpulseai.net/healthz`
2. Check API key is valid
3. Review audit logs

### Workflow Not Triggering

1. Verify workflow is active in n8n
2. Check webhook URL is correct
3. Review n8n execution history

### Callback Not Received

1. Check Odoo is accessible from n8n
2. Verify callback URL is correct
3. Check for firewall/proxy issues

## Common Workflows

### 1. Task Status Sync

Sync task status between Odoo and external systems.

### 2. Approval Notifications

Send Slack/email notifications on approval requests.

### 3. Document Processing

Extract data from uploaded documents and update Odoo records.

### 4. Scheduled Reports

Generate and email reports on schedule.

## External Resources

- **Runtime Deployment:** `ipai-ops-stack` repository
- **n8n Docs:** https://docs.n8n.io/
- **Workflow Templates:** `ipai-ops-stack/n8n/workflows/`
- **Channel:** #automations on chat.insightpulseai.net
