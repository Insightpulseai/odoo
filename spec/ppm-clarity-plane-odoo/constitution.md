# PPM Clarity Constitution

> Non-negotiable governance principles for Plane + Odoo Portfolio/Program/Project Management integration.

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-05

---

## Core Principles

### P1: Single Source of Truth (SSOT) Boundaries

**Planning Truth**: Plane.so templates and work items
**Operational Truth**: Odoo project.project and project.task records
**Reconciliation Truth**: Supabase ops schema (bidirectional mapping + event ledger)

**Enforcement**:
- Plane owns: title, description, priority, labels, cycle assignment, workflow state
- Odoo owns: assigned users, timesheets, costs, billable flags, attachments, chatter history
- No field may have dual ownership (prevents ping-pong edit conflicts)
- SSOT mapping tables use immutable UUIDs with UNIQUE constraints

### P2: Plane MCP Server First

**Integration Contract**: Use official Plane MCP server (55+ tools) over custom API clients.

**Tool Categories**:
- Projects (9 tools): List, create, update, delete projects; manage members
- Work Items (7 tools): Create, list, search, update, delete work items
- Cycles (12 tools): Manage cycles, add/remove items, transfer, archive
- Modules (11 tools): Manage modules, add/remove items, archive
- Initiatives (5 tools): Create and manage workspace-level initiatives
- Intake (5 tools): Manage intake work items for triage

**Authentication** (Self-Hosted Deployment):
- **Local Stdio Transport** (environment variables for self-hosted instances)
- PAT Token-based authentication via `PLANE_API_KEY`
- No OAuth required (OAuth only for Plane Cloud)

**Configuration**:
```bash
# Self-hosted Plane API credentials
PLANE_API_KEY=<workspace-api-key>
PLANE_WORKSPACE_SLUG=insightpulseai
PLANE_BASE_URL=https://plane-api.insightpulseai.com  # Required for self-hosted
```

**Rationale**: Official MCP server provides 55+ validated tools, OAuth support, and guaranteed compatibility with Plane API changes.

### P3: Field Ownership Enforcement

**Plane-Owned Fields** (Planning Layer):
- `title` (text)
- `description` (rich text)
- `priority` (enum: urgent, high, medium, low, none)
- `labels` (array of label IDs)
- `cycle` (cycle ID or null)
- `state` (workflow state ID)
- `estimate_point` (story points)

**Odoo-Owned Fields** (Execution Layer):
- `user_ids` (assigned users via project.task many2many)
- `timesheet_ids` (account.analytic.line records)
- `planned_hours` (float)
- `effective_hours` (computed from timesheets)
- `attachment_ids` (ir.attachment records)
- `message_ids` (mail.message chatter history)

**Cross-System Signals** (Read-Only Synchronization):
- Plane state change → Odoo stage change (one-way mapping)
- Odoo completion (stage=Done) → Plane state update (facts-only writeback)
- No bidirectional sync of same field (prevents edit conflicts)

**Violation Response**: Detected dual-ownership edits trigger `sync_state: 'needs_review'` in ops.work_item_links.

### P4: Webhook-Driven Synchronization

**Plane Webhooks** (HMAC-SHA256 signed, retry with exponential backoff):
- **Supported Events**: Project, Issue, Cycle, Module, Issue Comment
- **Actions**: create, update, delete
- **Delivery**: Webhook endpoint receives event → validates signature → triggers n8n workflow
- **Retry Logic**: 10-minute and 30-minute intervals on failure
- **Payload**: Full resource data (POST/PATCH) or ID only (DELETE)

**Signature Verification**:
```javascript
const crypto = require('crypto');
const signature = req.headers['x-plane-signature'];
const hash = crypto.createHmac('sha256', WEBHOOK_SECRET)
  .update(JSON.stringify(req.body))
  .digest('hex');
if (signature !== hash) throw new Error('Invalid signature');
```

**n8n Orchestration Workflows**:
1. **Plane → Odoo** (`ppm-clarity-plane-to-odoo.json`): Webhook receiver validates signature → checks commitment signal → syncs to Odoo
2. **Odoo → Plane** (`ppm-clarity-odoo-to-plane.json`): Cron every 10 minutes → polls Odoo completed tasks → writes back facts only
3. **Reconciliation** (`ppm-clarity-reconciliation.json`): Nightly at 2 AM → detects drift → applies field ownership rules

### P5: Idempotency Enforcement

**Idempotency Key Format**: `plane:sync:{workflow_id}:{plane_issue_id}:{odoo_task_id}:{timestamp}`

**Database Enforcement**:
```sql
CREATE TABLE ops.work_item_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  idempotency_key text UNIQUE,  -- UNIQUE constraint enforces deduplication
  link_id uuid REFERENCES ops.work_item_links(id),
  event_type text NOT NULL CHECK (event_type IN ('plane_to_odoo', 'odoo_to_plane', 'reconciliation', 'conflict')),
  event_data jsonb NOT NULL,
  success boolean NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

**Workflow Logic**:
1. Extract idempotency key from webhook/cron trigger
2. Query `ops.work_item_events WHERE idempotency_key = $key`
3. If exists: return cached result (HTTP 200 with previous response)
4. If not exists: execute sync → insert event with key → return new result

**Violation Response**: Duplicate idempotency key returns HTTP 409 Conflict with cached result.

### P6: Append-Only Event Ledger

**Audit Table**: `ops.work_item_events`

**Event Types**:
- `plane_to_odoo`: Plane change triggered Odoo sync
- `odoo_to_plane`: Odoo completion triggered Plane writeback
- `reconciliation`: Nightly drift repair applied
- `conflict`: Field ownership violation detected

**Event Data Schema** (JSONB):
```json
{
  "source_system": "plane|odoo|n8n",
  "operation": "create|update|delete",
  "plane_fields_changed": ["title", "priority"],
  "odoo_fields_changed": ["user_ids", "timesheet_ids"],
  "hash_before": "sha256_hash",
  "hash_after": "sha256_hash",
  "error_details": "...",  // if success=false
  "metadata": {
    "workflow_name": "ppm-clarity-plane-to-odoo",
    "webhook_id": "uuid",
    "execution_time_ms": 1250
  }
}
```

**Retention**: 90 days (aligned with n8n execution history retention)

**Query Examples**:
```sql
-- Conflict detection
SELECT * FROM ops.work_item_events
WHERE event_type = 'conflict'
AND created_at > now() - interval '7 days';

-- Sync health by link
SELECT link_id, COUNT(*) as event_count,
       SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count
FROM ops.work_item_events
GROUP BY link_id
HAVING SUM(CASE WHEN success THEN 1 ELSE 0 END) < COUNT(*) * 0.95;  -- <95% success
```

### P7: Hash-Based Change Detection

**Purpose**: Avoid unnecessary sync operations when no relevant changes occurred.

**Plane Hash Calculation** (Plane-owned fields only):
```python
import hashlib
import json

def calculate_plane_hash(issue: dict) -> str:
    canonical_fields = {
        'title': issue['name'],
        'description': issue['description_html'],
        'priority': issue['priority'],
        'labels': sorted(issue['label_ids']),  # deterministic order
        'cycle': issue.get('cycle_id'),
        'state': issue['state_id'],
        'estimate': issue.get('estimate_point')
    }
    canonical_json = json.dumps(canonical_fields, sort_keys=True)
    return hashlib.sha256(canonical_json.encode()).hexdigest()
```

**Odoo Hash Calculation** (Odoo-owned fields only):
```python
def calculate_odoo_hash(task: dict) -> str:
    canonical_fields = {
        'users': sorted([u['id'] for u in task['user_ids']]),
        'timesheets': sorted([t['id'] for t in task['timesheet_ids']]),
        'attachments': sorted([a['id'] for a in task['attachment_ids']]),
        'planned_hours': task['planned_hours'],
        'effective_hours': task['effective_hours']
    }
    canonical_json = json.dumps(canonical_fields, sort_keys=True)
    return hashlib.sha256(canonical_json.encode()).hexdigest()
```

**Sync Decision Logic**:
```python
current_plane_hash = calculate_plane_hash(plane_issue)
last_plane_hash = db.query("SELECT last_plane_hash FROM ops.work_item_links WHERE plane_issue_id = ?")

if current_plane_hash != last_plane_hash:
    sync_plane_to_odoo(plane_issue)
    db.update("UPDATE ops.work_item_links SET last_plane_hash = ? WHERE plane_issue_id = ?",
              current_plane_hash, plane_issue['id'])
else:
    logger.info(f"Skipping sync - no Plane changes detected for {plane_issue['id']}")
```

### P8: Conflict Resolution via Field Ownership

**Conflict Scenario**: Both Plane and Odoo hashes changed since last sync.

**Resolution Algorithm**:
1. Fetch current Plane record via MCP `get_work_item(issue_id)`
2. Fetch current Odoo record via RPC `task.read([task_id], fields=[...])`
3. Apply field ownership rules:
   - Plane-owned fields: Plane value wins → update Odoo
   - Odoo-owned fields: Odoo value wins → update Plane (facts-only writeback)
4. Update both systems with resolved values
5. Log reconciliation event with `event_type: 'reconciliation'`
6. Update both hashes in `ops.work_item_links`

**Example**:
- **Conflict**: User changed title in Plane (Plane-owned) AND added timesheet in Odoo (Odoo-owned)
- **Resolution**: Accept both changes → Odoo gets new title, Plane gets timesheet summary in comment
- **Rationale**: No actual conflict - different field ownership domains

**Escalation**: If same field edited in both systems (ownership violation), set `sync_state: 'needs_review'` and notify via Slack.

---

## Integration Architecture

### Plane MCP Server Integration

**MCP Server Setup** (Claude Code - Self-Hosted):
```json
{
  "plane": {
    "command": "uvx",
    "args": ["plane-mcp-server"],
    "env": {
      "PLANE_API_KEY": "$PLANE_API_KEY",
      "PLANE_WORKSPACE_SLUG": "$PLANE_WORKSPACE_SLUG",
      "PLANE_BASE_URL": "https://plane-api.insightpulseai.com"
    }
  }
}
```

**Requirements**:
- Python 3.10+ installed
- `uvx` installed (`pip install uvx`)
- Stdio transport for self-hosted instances (not HTTP OAuth)

**Usage in n8n Workflows**:
```javascript
// n8n HTTP Request node calling MCP gateway
const mcpResponse = await fetch('http://localhost:8765/mcp/plane/invoke', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'update_work_item',
    arguments: {
      project_id: projectId,
      issue_id: issueId,
      data: { state: completedStateId }
    }
  })
});
```

### Odoo RPC Client

**Authentication**:
```python
import xmlrpc.client

odoo_url = 'https://insightpulseai.com/odoo'
odoo_db = 'odoo'
odoo_username = 'admin'  # service account
odoo_password = os.getenv('ODOO_SERVICE_PASSWORD')

common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
uid = common.authenticate(odoo_db, odoo_username, odoo_password, {})

models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')
```

**CRUD Operations**:
```python
# Create task
task_id = models.execute_kw(odoo_db, uid, odoo_password,
    'project.task', 'create', [{
        'name': plane_issue['name'],
        'project_id': odoo_project_id,
        'description': plane_issue['description_html']
    }])

# Update task
models.execute_kw(odoo_db, uid, odoo_password,
    'project.task', 'write', [[task_id], {'stage_id': done_stage_id}])

# Read task with relations
task = models.execute_kw(odoo_db, uid, odoo_password,
    'project.task', 'read', [[task_id]], {
        'fields': ['name', 'user_ids', 'timesheet_ids', 'attachment_ids', 'effective_hours']
    })[0]
```

### n8n Workflow Templates

**1. Plane → Odoo (Webhook Trigger)**:
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Plane Webhook",
      "parameters": {
        "path": "ppm-clarity/plane",
        "responseMode": "onReceived",
        "options": {
          "rawBody": true
        }
      }
    },
    {
      "type": "n8n-nodes-base.function",
      "name": "Verify Signature",
      "parameters": {
        "functionCode": "const crypto = require('crypto');\nconst signature = $input.item.headers['x-plane-signature'];\nconst hash = crypto.createHmac('sha256', process.env.PLANE_WEBHOOK_SECRET).update($input.item.body).digest('hex');\nif (signature !== hash) throw new Error('Invalid signature');\nreturn $input.item;"
      }
    },
    {
      "type": "n8n-nodes-base.supabase",
      "name": "Sync to Odoo",
      "parameters": {
        "operation": "executeFunction",
        "function": "sync_plane_to_odoo",
        "arguments": {
          "plane_issue": "={{ JSON.stringify($json.data) }}",
          "event_type": "={{ $json.event }}",
          "action": "={{ $json.action }}"
        }
      }
    }
  ]
}
```

**2. Odoo → Plane (Cron Trigger)**:
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.cron",
      "name": "Every 10 Minutes",
      "parameters": {
        "cronExpression": "*/10 * * * *"
      }
    },
    {
      "type": "n8n-nodes-base.supabase",
      "name": "Query Completed Tasks",
      "parameters": {
        "operation": "executeFunction",
        "function": "get_completed_tasks_since_last_sync"
      }
    },
    {
      "type": "n8n-nodes-base.loop",
      "name": "For Each Task",
      "parameters": {}
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Update Plane via MCP",
      "parameters": {
        "url": "http://localhost:8765/mcp/plane/invoke",
        "method": "POST",
        "body": {
          "tool": "update_work_item",
          "arguments": {
            "project_id": "={{ $json.plane_project_id }}",
            "issue_id": "={{ $json.plane_issue_id }}",
            "data": {
              "state": "={{ $json.completed_state_id }}"
            }
          }
        }
      }
    }
  ]
}
```

**3. Reconciliation (Nightly Cron)**:
```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.cron",
      "name": "Nightly at 2 AM",
      "parameters": {
        "cronExpression": "0 2 * * *"
      }
    },
    {
      "type": "n8n-nodes-base.supabase",
      "name": "Get Conflicts",
      "parameters": {
        "operation": "executeFunction",
        "function": "get_sync_conflicts"
      }
    },
    {
      "type": "n8n-nodes-base.supabase",
      "name": "Reconcile Each Conflict",
      "parameters": {
        "operation": "executeFunction",
        "function": "reconcile_work_item",
        "arguments": {
          "link_id": "={{ $json.id }}"
        }
      }
    }
  ]
}
```

---

## Operational Constraints

### OC1: Plane Template Enforcement

**Template Structure**:
```yaml
portfolio_template:
  states:
    - name: "Ideation"
      type: "backlog"
    - name: "Planned"
      type: "started"
    - name: "In Progress"
      type: "started"
    - name: "Done"
      type: "completed"
  labels:
    - name: "Strategic"
      color: "#FF6B6B"
    - name: "Operational"
      color: "#4ECDC4"
  work_item_types:
    - name: "Initiative"
      icon: "target"
    - name: "Project"
      icon: "folder"
```

**Odoo Project Mapping**:
```python
# Plane state → Odoo stage mapping
STATE_MAPPING = {
    'Ideation': 'Draft',
    'Planned': 'Backlog',
    'In Progress': 'In Progress',
    'Done': 'Done'
}

# Create Odoo project with aligned stages
odoo_project_id = models.execute_kw(db, uid, password,
    'project.project', 'create', [{
        'name': plane_project['name'],
        'type_ids': [(0, 0, {'name': stage}) for stage in STATE_MAPPING.values()]
    }])
```

### OC2: Webhook Endpoint Security

**Requirements**:
- HTTPS only (no HTTP)
- Publicly accessible (not localhost)
- HMAC-SHA256 signature verification
- Rate limiting (10 requests/second max)
- Timeout: 30 seconds response time

**nginx Configuration**:
```nginx
location /webhooks/plane {
    limit_req zone=webhook_limit burst=5 nodelay;
    proxy_pass http://n8n:5678/webhook/ppm-clarity/plane;
    proxy_read_timeout 30s;
    proxy_connect_timeout 10s;
}
```

### OC3: Supabase RPC Security

**Row-Level Security (RLS)**:
```sql
-- ops.work_item_links: service_role only
ALTER TABLE ops.work_item_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON ops.work_item_links
  FOR ALL USING (auth.role() = 'service_role');

-- ops.work_item_events: append-only for service_role
CREATE POLICY "service_role_append" ON ops.work_item_events
  FOR INSERT WITH CHECK (auth.role() = 'service_role');
```

**RPC Function Permissions**:
```sql
GRANT EXECUTE ON FUNCTION sync_plane_to_odoo TO service_role;
GRANT EXECUTE ON FUNCTION sync_odoo_to_plane TO service_role;
GRANT EXECUTE ON FUNCTION get_sync_conflicts TO service_role;
GRANT EXECUTE ON FUNCTION reconcile_work_item TO service_role;
```

---

## Emergency Procedures

### EP1: Sync Failure Escalation

**Incident Response**:
1. Check `ops.work_item_events` for error patterns
2. Query failed events: `SELECT * FROM ops.work_item_events WHERE success = false AND created_at > now() - interval '1 hour'`
3. Identify affected work item links
4. Set `sync_state: 'blocked'` for affected links
5. Notify via Slack with error details
6. Manual intervention required to unblock

**Rollback Strategy**:
- Revert Odoo task to previous state (use chatter history)
- Revert Plane issue via MCP `update_work_item` with previous values
- Delete failed event from `ops.work_item_events` (idempotency key reset)
- Retry sync with corrected data

### EP2: Webhook Signature Validation Failure

**Detection**:
```javascript
if (signature !== expected_hash) {
  logger.error('Webhook signature mismatch', {
    webhook_id: req.body.webhook_id,
    expected: expected_hash,
    received: signature
  });
  return res.status(403).json({ error: 'Invalid signature' });
}
```

**Response**:
1. Reject webhook with HTTP 403
2. Log to `ops.platform_events` with `event_type: 'webhook_security_violation'`
3. Check Plane webhook secret rotation
4. Rotate secret if compromised
5. Update n8n environment variables with new secret

---

## References

- **Plane MCP Server Docs**: https://developers.plane.so/dev-tools/mcp-server-claude-code
- **Plane Webhooks**: https://developers.plane.so/dev-tools/intro-webhooks
- **Plane Agents**: https://developers.plane.so/dev-tools/agents/overview
- **Odoo External API**: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **SSOT Boundaries**: `docs/architecture/SSOT_BOUNDARIES.md`
- **Supabase RLS Policies**: `supabase/migrations/*_rls_policies.sql`

---

**This constitution is immutable for active implementations. Changes require architecture review + approval.**
