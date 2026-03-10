# PPM Clarity: Plane + Odoo Integration — Operational Guide

> Clean Portfolio/Program/Project Management using Plane.so templates + Odoo execution tracking.
> **Spec**: `spec/ppm-clarity-plane-odoo/`
> **SSOT**: `ssot/integrations/plane.yaml` + `supabase/migrations/*_ppm_clarity*.sql`
> Last updated: 2026-03-05

---

## Overview

PPM Clarity provides enterprise-grade portfolio/program/project management through a **3-layer SSOT architecture**:

- **Plane (Planning Truth)**: Template-driven strategic planning with cycles, initiatives, and work items
- **Odoo (Operational Truth)**: Execution tracking with timesheets, resource allocation, and invoicing
- **Supabase SSOT (Reconciliation Truth)**: Bidirectional mapping + append-only event ledger

### Key Features

| Feature | Plane | Odoo | SSOT |
|---------|-------|------|------|
| **Planning** | ✅ Templates, states, labels | ❌ | ✅ Field ownership |
| **Execution** | ❌ | ✅ Timesheets, costs, resources | ✅ Event ledger |
| **Analytics** | ✅ Dashboards, widgets | ✅ Profitability reports | ✅ Aggregation views |
| **Sync** | ✅ Commitment signal | ✅ Completion facts | ✅ Reconciliation |

---

## Integration Architecture

```
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│   Plane.so       │            │   Supabase       │            │   Odoo 19        │
│  (Planning)      │            │    (SSOT)        │            │  (Execution)     │
├──────────────────┤            ├──────────────────┤            ├──────────────────┤
│ • Projects       │ Webhook    │ • work_item_     │  n8n Cron  │ • project.task   │
│ • Work items     │───────────>│   links          │───────────>│ • hr_timesheet   │
│ • States/Labels  │ Commitment │ • work_item_     │ Completion │ • project_budget │
│ • Cycles         │            │   events         │            │ • sale_timesheet │
└──────────────────┘            └──────────────────┘            └──────────────────┘
         │                              │                              │
         │                              │                              │
         │                       n8n Workflows                         │
         │                    (Orchestration)                          │
         │                              │                              │
         ├──────────────────────────────┴──────────────────────────────┤
         │  1. plane-to-odoo.json (Webhook handler)                    │
         │  2. odoo-to-plane.json (Completion sync)                    │
         │  3. reconciliation.json (Nightly drift repair)              │
         └─────────────────────────────────────────────────────────────┘
```

---

## Field Ownership Contract

**Critical Rule**: Each field is owned by ONE system only. No ping-pong edits.

### Plane-Owned Fields (Synced Plane → Odoo)

| Field | Plane | Odoo | Why |
|-------|-------|------|-----|
| Title | ✅ | 📖 Read-only | Plane defines task scope |
| Description | ✅ | 📖 Read-only | Plane holds requirements |
| Priority | ✅ | 📖 Read-only | Plane sets strategic priority |
| State | ✅ | 📖 Read-only | Plane workflow drives stages |
| Labels | ✅ | 📖 Stored in link table | Plane categorization |
| Cycle | ✅ | 📖 Stored in link table | Plane sprint planning |
| Estimate (story points) | ✅ | 📖 → `planned_hours` | Plane estimation × 8 |

### Odoo-Owned Fields (Never Synced to Plane)

| Field | Plane | Odoo | Why |
|-------|-------|------|-----|
| Assigned Users | ❌ | ✅ | Odoo resource allocation |
| Timesheets | ❌ | ✅ | Odoo time tracking |
| Actual Hours | ❌ | ✅ | Odoo execution data |
| Costs | ❌ | ✅ | Odoo financial tracking |
| Billable Flags | ❌ | ✅ | Odoo invoicing logic |
| Attachments | ❌ | ✅ | Odoo file management |
| Chatter/Comments | ❌ | ✅ | Odoo collaboration |

### Facts-Only Writeback (Odoo → Plane)

**What Gets Written Back**:
- Completion status: Task stage="Done" → Plane state="Done"
- Summary metrics in comment: "Actual hours: X, Cost: $Y, Completed: YYYY-MM-DD"

**What Never Gets Written Back**:
- Assigned users (Odoo-specific)
- Detailed timesheet entries (privacy)
- File attachments (Odoo-specific)
- Chatter comments (Odoo collaboration)

---

## Sync Workflows

### 1. Commitment Signal (Plane → Odoo)

**Trigger**: Plane work item state changes to "Planned" OR label "Committed" added

**n8n Workflow**: `automations/n8n/workflows/ppm-clarity-plane-to-odoo.json`

**Steps**:
1. **Webhook Receipt**: Plane webhook fires with `event: "issue"`, `action: "update"`
2. **Signature Validation**: Verify HMAC-SHA256 signature using `PLANE_WEBHOOK_SECRET`
3. **Commitment Check**: `state === "Planned"` OR `"Committed" in labels`
4. **Mapping Lookup**: Query `ops.work_item_links` for existing mapping
5. **Hash Comparison**: Calculate Plane hash, compare with `last_plane_hash`
6. **Odoo Sync**:
   - If no mapping: Create Odoo task + insert link record
   - If mapping exists: Update Odoo task with Plane-owned fields only
7. **Event Logging**: Append event to `ops.work_item_events` with `event_type: 'plane_to_odoo'`
8. **Idempotency**: Use `idempotency_key` to prevent duplicate processing

**Frequency**: Real-time (webhook-driven)

**Success Criteria**: `ops.work_item_events.success = true` AND Odoo task exists with correct fields

---

### 2. Completion Signal (Odoo → Plane)

**Trigger**: Odoo task stage changes to "Done"

**n8n Workflow**: `automations/n8n/workflows/ppm-clarity-odoo-to-plane.json`

**Steps**:
1. **Cron Trigger**: Every 10 minutes, query Odoo tasks with `stage_id = done_stage` AND `write_date > last_sync`
2. **Mapping Lookup**: For each completed task, query `ops.work_item_links` for Plane mapping
3. **Hash Comparison**: Calculate Odoo hash, compare with `last_odoo_hash`
4. **Plane Update**:
   - Update Plane issue state: `state: completed_state_id`
   - Append comment with facts: "Task completed in Odoo. Actual hours: X, Cost: $Y"
5. **Event Logging**: Append event to `ops.work_item_events` with `event_type: 'odoo_to_plane'`
6. **Mapping Update**: Update `last_odoo_hash` in link record

**Frequency**: Every 10 minutes (batch sync)

**Success Criteria**: Plane issue state="Done" AND comment with execution metrics exists

---

### 3. Conflict Reconciliation (Nightly)

**Trigger**: Cron at 2 AM Asia/Manila daily

**n8n Workflow**: `automations/n8n/workflows/ppm-clarity-reconciliation.json`

**Steps**:
1. **Conflict Detection**: Query `ops.work_item_links` WHERE `last_plane_hash` AND `last_odoo_hash` both changed since `last_synced_at`
2. **Fetch Current State**: For each conflict, fetch current Plane issue + Odoo task
3. **Field Ownership Resolution**:
   - Plane-owned fields (title, description, priority): Update Odoo with Plane values
   - Odoo-owned fields (timesheets, costs): Update Plane comment with Odoo facts
4. **Hash Recalculation**: Recalculate both hashes, update link record
5. **Event Logging**: Append event with `event_type: 'reconciliation'`
6. **Conflict Marking**: If irreconcilable, set `sync_state: 'needs_review'`

**Frequency**: Daily at 2 AM

**Success Criteria**: `ops.work_item_links.sync_state = 'ok'` for all reconciled items

---

## Slack Notifications

### Notification Channels

| Channel | Purpose | Frequency |
|---------|---------|-----------|
| `#ppm-clarity-logs` | Success logs for all sync events | Real-time |
| `#ppm-clarity-alerts` | Failure alerts requiring attention | Real-time |
| `#ppm-clarity-conflicts` | Conflict detection requiring manual review | Real-time |
| `#ppm-clarity-daily` | Daily summary report | 8 AM daily |

---

### Success Notifications (`#ppm-clarity-logs`)

**Format**:
```
✅ Plane → Odoo: Issue "Implement authentication" → Task #123 (Created)
   - Plane Project: proj-456
   - Odoo Task: https://erp.insightpulseai.com/web#id=123&model=project.task
   - Event ID: abc-123-def
```

**Trigger**: `ops.work_item_events.success = true`

---

### Failure Notifications (`#ppm-clarity-alerts`)

**Format**:
```
❌ Plane → Odoo FAILED: Issue "Implement authentication"
   - Error: Odoo RPC timeout (30s exceeded)
   - Event ID: abc-123-def
   - Retry: Scheduled for next sync cycle
   - Manual Action: Check Odoo availability
```

**Trigger**: `ops.work_item_events.success = false`

---

### Conflict Notifications (`#ppm-clarity-conflicts`)

**Format**:
```
⚠️ Conflict Detected: Issue "Implement authentication" / Task #123
   - Plane Hash Changed: abc123 → def456 (title updated)
   - Odoo Hash Changed: xyz789 → uvw012 (timesheets added)
   - Resolution: Field ownership applied (Plane title wins, Odoo timesheets preserved)
   - Link: https://erp.insightpulseai.com/web#id=123&model=project.task
```

**Trigger**: `ops.work_item_events.event_type = 'conflict'`

---

### Daily Summary Report (`#ppm-clarity-daily`)

**Format**:
```
📊 PPM Clarity Daily Summary (2026-03-05)

✅ Successful Syncs: 47
❌ Failed Syncs: 2
⚠️  Conflicts Resolved: 1
🔄 Pending Reconciliation: 0

Top Projects:
1. Scout Dashboard (15 syncs)
2. Finance SSC Platform (12 syncs)
3. PPM Clarity (8 syncs)

Manual Review Required:
- Issue proj-123/issue-456: Task creation failed (Odoo offline)
```

**Trigger**: Cron at 8 AM daily

---

## Slack Slash Commands

### `/ppm-retry <event_id>`

**Purpose**: Manually retry a failed sync event

**Usage**:
```
/ppm-retry abc-123-def
```

**Response**:
```
🔄 Retrying event abc-123-def...
✅ Retry successful: Issue "Implement authentication" → Task #123
```

**Authorization**: `@insightpulseai/devops` and `@insightpulseai/ppm-admins`

---

### `/ppm-resolve <link_id> <resolution>`

**Purpose**: Manually resolve a conflict with explicit resolution strategy

**Usage**:
```
/ppm-resolve abc-123-def plane-wins
```

**Resolutions**:
- `plane-wins`: Apply Plane-owned fields to Odoo
- `odoo-wins`: Apply Odoo-owned fields to Plane (facts-only)
- `field-ownership`: Apply standard field ownership rules (default)

**Response**:
```
✅ Conflict resolved: Link abc-123-def (field-ownership applied)
   - Plane title → Odoo task name
   - Odoo timesheets → Plane comment (facts-only)
```

**Authorization**: `@insightpulseai/ppm-admins` only

---

### `/ppm-status [project_id]`

**Purpose**: Get current sync status for a project or all projects

**Usage**:
```
/ppm-status proj-456
```

**Response**:
```
📊 PPM Clarity Status: Scout Dashboard (proj-456)

✅ Active Mappings: 23
🔄 Last Sync: 2 minutes ago
⚠️  Pending Conflicts: 0
❌ Failed Syncs (24h): 1

Recent Events:
- [2m ago] Issue "Fix login bug" → Task #789 (Updated)
- [5m ago] Task #788 completed → Issue "Add search" (Done)
```

**Authorization**: `@insightpulseai/all-staff` (read-only)

---

## Troubleshooting Guide

### Issue: Plane Webhook Not Received

**Symptoms**: Plane work item state changed but no Odoo task created

**Diagnosis**:
1. Check n8n workflow status: `https://n8n.insightpulseai.com/workflow/<workflow-id>`
2. Verify webhook configured in Plane: Settings → Webhooks → `https://n8n.insightpulseai.com/webhook/ppm-clarity/plane`
3. Check Plane webhook secret matches `PLANE_WEBHOOK_SECRET` in Supabase Vault

**Resolution**:
```bash
# Test webhook endpoint
curl -X POST https://n8n.insightpulseai.com/webhook/ppm-clarity/plane \
  -H "Content-Type: application/json" \
  -H "X-Plane-Signature: <signature>" \
  -d '{"event": "issue", "action": "update", "data": {...}}'

# Expected: HTTP 200, event logged in ops.work_item_events
```

---

### Issue: Odoo Task Creation Failed

**Symptoms**: Event logged with `success = false` and error message "Odoo RPC timeout"

**Diagnosis**:
1. Check Odoo availability: `curl https://erp.insightpulseai.com/health`
2. Verify Odoo service account credentials: `ODOO_SERVICE_USER` / `ODOO_SERVICE_PASSWORD`
3. Check Odoo logs: `ssh root@178.128.112.214 "docker logs odoo-production -n 100"`

**Resolution**:
```bash
# Retry failed event manually
# Via Slack: /ppm-retry <event_id>

# Or via Supabase RPC:
SELECT ops.append_work_item_event(
  p_link_id := '<link-id>',
  p_event_type := 'plane_to_odoo',
  p_source_system := 'n8n',
  p_event_data := '{"retry": true}'::jsonb,
  p_idempotency_key := 'retry-<original-key>',
  p_success := true
);
```

---

### Issue: Conflict Not Resolving

**Symptoms**: `ops.work_item_links.sync_state = 'needs_review'` persists after reconciliation

**Diagnosis**:
1. Query conflict details: `SELECT * FROM ops.get_sync_conflicts(10);`
2. Review recent events: Check `recent_events` JSONB array for error messages
3. Verify field ownership rules in sync engine code

**Resolution**:
```sql
-- Manually resolve conflict via Slack
/ppm-resolve <link_id> field-ownership

-- Or via SQL (service_role only):
UPDATE ops.work_item_links
SET sync_state = 'ok', last_synced_at = now()
WHERE id = '<link-id>';
```

---

### Issue: Hash Mismatch (Drift Detection False Positive)

**Symptoms**: Reconciliation workflow flags conflict but no actual changes detected

**Diagnosis**:
1. Compare hashes: `SELECT last_plane_hash, last_odoo_hash FROM ops.work_item_links WHERE id = '<link-id>';`
2. Recalculate hashes manually: Fetch Plane issue + Odoo task, run hash function
3. Check for hash algorithm changes (determinism requirement)

**Resolution**:
```python
# Recalculate and update hashes
from scripts.ppm.sync_engine import SyncEngine

engine = SyncEngine(plane_client, odoo_client, supabase_client)
link = supabase_client.table('work_item_links').select('*').eq('id', link_id).single().execute()

plane_issue = plane_client.get_issue(link['plane_project_id'], link['plane_issue_id'])
odoo_task = odoo_client.get_task_details(link['odoo_task_id'])

new_plane_hash = plane_client.calculate_hash(plane_issue)
new_odoo_hash = odoo_client.calculate_hash(odoo_task)

supabase_client.table('work_item_links').update({
    'last_plane_hash': new_plane_hash,
    'last_odoo_hash': new_odoo_hash,
    'sync_state': 'ok',
    'last_synced_at': 'now()'
}).eq('id', link_id).execute()
```

---

### Issue: n8n Workflow Stuck

**Symptoms**: Workflow status shows "running" for >10 minutes without completion

**Diagnosis**:
1. Check n8n execution logs: n8n UI → Executions → Filter by workflow
2. Verify Supabase RPC function response times: `supabase functions logs <function-name>`
3. Check for database locks: `SELECT * FROM pg_locks WHERE granted = false;`

**Resolution**:
```bash
# Cancel stuck execution via n8n UI
# Or restart n8n container
ssh root@178.128.112.214 "docker restart n8n"

# Verify workflow resumes
curl https://n8n.insightpulseai.com/health
```

---

## Evidence Format

All sync operations generate evidence bundles following repo standards:

**Path**: `web/docs/evidence/<YYYYMMDD-HHMM+0800>/ppm-clarity-sync/logs/`

**Timezone**: Asia/Manila (UTC+08:00)

**Summary** (`summary.json`):
```json
{
  "timestamp": "20260305-1430+0800",
  "workflow": "plane-to-odoo",
  "events_processed": 5,
  "events_succeeded": 4,
  "events_failed": 1,
  "conflicts_detected": 0,
  "status": "PARTIAL",
  "logs": {
    "webhook_receipt": "web/docs/evidence/20260305-1430+0800/ppm-clarity-sync/logs/webhook-receipt.log",
    "odoo_sync": "web/docs/evidence/20260305-1430+0800/ppm-clarity-sync/logs/odoo-sync.log",
    "event_ledger": "web/docs/evidence/20260305-1430+0800/ppm-clarity-sync/logs/event-ledger.log",
    "errors": "web/docs/evidence/20260305-1430+0800/ppm-clarity-sync/logs/errors.log"
  }
}
```

---

## Verification Checklist

### Pre-Deployment Verification

- [ ] Supabase migration applied: `ops.work_item_links` + `ops.work_item_events` exist
- [ ] Plane webhook configured with correct URL and secret
- [ ] Odoo service account created: `plane_sync@insightpulseai.com` with project.task permissions
- [ ] n8n workflows deployed: `plane-to-odoo`, `odoo-to-plane`, `reconciliation`
- [ ] Slack channels created: `#ppm-clarity-logs`, `#ppm-clarity-alerts`, `#ppm-clarity-conflicts`, `#ppm-clarity-daily`
- [ ] Secrets stored in Supabase Vault: `plane_api_key`, `plane_webhook_secret`, `odoo_service_password`

---

### Post-Deployment Verification

- [ ] Plane work item → state="Planned" → Odoo task created (verify in `ops.work_item_links`)
- [ ] Odoo task → stage="Done" → Plane state updated (verify in Plane UI)
- [ ] Duplicate event → idempotent (no duplicate tasks, same `idempotency_key`)
- [ ] Drift reconciliation → detects mismatched title/state → resolves per field ownership
- [ ] All events logged in `ops.work_item_events` (100% audit coverage)
- [ ] Slack notifications received in correct channels

---

## Success Metrics

### M1: Sync Reliability

- **Target**: ≥99.5% sync success rate
- **Measurement**: `SUM(success) / COUNT(*) FROM ops.work_item_events`
- **Threshold**: Alert if <95% in 24-hour window

---

### M2: Sync Latency

- **Target**: <5 minutes from Plane change to Odoo update
- **Measurement**: `(odoo_update_time - plane_webhook_time)` from event metadata
- **Threshold**: Alert if median >10 minutes

---

### M3: Conflict Rate

- **Target**: <1% of syncs trigger conflict reconciliation
- **Measurement**: `COUNT(event_type='conflict') / COUNT(*) FROM ops.work_item_events`
- **Threshold**: Alert if >5% in 7-day window

---

### M4: Analytics Freshness

- **Target**: Superset dashboards show data <1 hour old
- **Measurement**: `now() - MAX(updated_at) FROM ops.work_item_links`
- **Threshold**: Alert if >2 hours stale

---

### M5: User Adoption

- **Target**: ≥80% of projects use Plane → Odoo sync
- **Measurement**: `COUNT(DISTINCT plane_project_id) / total_projects FROM ops.work_item_links`
- **Threshold**: Review if <50% after 30 days

---

## References

- **Spec Bundle**: `spec/ppm-clarity-plane-odoo/` (constitution, PRD, plan, tasks)
- **Database Schema**: `supabase/migrations/20260305_create_ppm_clarity_schema.sql`
- **Integration Clients**: `scripts/ppm/plane_client.py`, `scripts/ppm/odoo_client.py`, `scripts/ppm/sync_engine.py`
- **n8n Workflows**: `automations/n8n/workflows/ppm-clarity-*.json`
- **SSOT Boundaries**: `docs/architecture/SSOT_BOUNDARIES.md`
- **Plane API Docs**: https://developers.plane.so/api-reference
- **Plane MCP Server**: https://developers.plane.so/dev-tools/mcp-server-claude-code
