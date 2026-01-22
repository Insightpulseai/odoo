# IPAI Integration Bus - Complete Implementation Guide

**Architecture**: Odoo → Supabase (integration bus) → n8n (orchestration) → Mattermost/Email/Dashboards

**Status**: Implementation Ready
**Version**: 1.0.0
**Last Updated**: 2026-01-22

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     IPAI Integration Bus                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Odoo CE 18.0 (Source of Truth)                                 │
│       ↓ HTTP POST (HMAC-signed)                                 │
│  Supabase Edge Function (odoo-webhook)                          │
│       ↓ Write to integration.outbox                             │
│  PostgreSQL 15 (Durable Queue + Audit Log)                      │
│       ↓ RPC Polling                                             │
│  n8n Event Router (claim_outbox → route → ack/fail)             │
│       ↓ Domain Workflows                                        │
│  ├─ Expense Handler → Mattermost approvals                      │
│  ├─ Asset Handler → Calendar + Email confirmations              │
│  └─ Finance Handler → PPM dashboard + BIR filing                │
│                                                                  │
│  MCP Tools (Read-Only via Supabase RLS)                         │
│  └─ Claude Desktop / VS Code → query event_log                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

1. **Odoo Never Talks to Supabase DB Directly** - All events via HMAC-signed webhooks
2. **Idempotent by Design** - Duplicate events are deduplicated via `idempotency_key`
3. **Durable by Default** - Events survive crashes (outbox pattern)
4. **Read-Only MCP** - Agents query `event_log`, never mutate `outbox`
5. **Event-Driven n8n** - All workflows triggered by events, not schedules

---

## Quick Start

### 1. Deploy Supabase Infrastructure

```bash
# Prerequisites
brew install supabase/tap/supabase  # macOS
# OR: npm install -g supabase

# Link to project
cd /Users/tbwa/Documents/GitHub/odoo-ce
supabase link --project-ref spdtwktxdalcfigzeqrz

# Deploy (migrations + Edge Function + secrets)
./scripts/integration/deploy-supabase.sh
```

**What This Does**:
- Creates `integration` schema with `outbox`, `event_log`, `id_map` tables
- Deploys `odoo-webhook` Edge Function with HMAC verification
- Sets `ODOO_WEBHOOK_SECRET` (saves to `.env` if not set)
- Verifies all tables and functions exist

### 2. Configure Odoo

**System Parameters** (Settings → Technical → Parameters):

| Key | Value |
|-----|-------|
| `ipai.webhook.url` | `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo-webhook` |
| `ipai.webhook.secret` | `<ODOO_WEBHOOK_SECRET from deploy script>` |

**Install Required Modules**:
```bash
# Via Docker
docker compose exec odoo-core odoo -d odoo_core -i ipai_enterprise_bridge --stop-after-init

# Or via Odoo UI: Apps → Search "ipai_enterprise_bridge" → Install
```

### 3. Test Event Emission

```bash
# Set environment variables
export SUPABASE_FUNCTION_URL="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo-webhook"
export ODOO_WEBHOOK_SECRET="<secret from deploy>"

# Test expense event
./scripts/integration/test-webhook.py expense.submitted

# Test asset event
./scripts/integration/test-webhook.py asset.reserved

# Test finance PPM event
./scripts/integration/test-webhook.py finance_task.created
```

**Expected Output**:
```
✅ expense.submitted
✅ asset.reserved
✅ finance_task.created
```

**Verify in Supabase**:
```bash
supabase db query "SELECT event_type, aggregate_id, status FROM integration.outbox ORDER BY created_at DESC LIMIT 10;"
```

### 4. Import n8n Workflows

**Files**:
- `n8n/workflows/integration/event-router.json` - Main router (claim → route → ack/fail)
- `n8n/workflows/integration/expense-handler.json` - Expense approvals + notifications
- `n8n/workflows/integration/asset-handler.json` - Asset booking confirmations
- `n8n/workflows/integration/finance-handler.json` - Finance PPM dashboard updates

**Import Steps**:
1. Open n8n: https://n8n.insightpulseai.net
2. Workflows → Import from File → Select JSON
3. Configure credentials:
   - Supabase API (service role key)
   - Mattermost Webhook URL
   - Google Calendar API (for asset bookings)
4. Activate workflows

### 5. Verify End-to-End

**Test Expense Workflow**:
1. Login to Odoo: http://localhost:8069
2. Expenses → Create → Submit for approval
3. Check Supabase outbox: `SELECT * FROM integration.outbox WHERE event_type='expense.submitted';`
4. Verify Mattermost notification sent to approver
5. Approve expense in Odoo
6. Check `expense.approved` event created

**Monitor**:
```bash
# Watch outbox in real-time
watch -n 2 "supabase db query \"SELECT event_type, status, attempts FROM integration.outbox WHERE status != 'done' ORDER BY created_at DESC LIMIT 20;\""

# Check dead letter queue
supabase db query "SELECT * FROM integration.outbox WHERE status='dead';"
```

---

## Event Taxonomy

See [`EVENT_TAXONOMY.md`](./EVENT_TAXONOMY.md) for complete event definitions.

**Summary**:

| Domain | Events | Aggregate Type |
|--------|--------|----------------|
| **Expense** | submitted, approved, rejected, paid | expense |
| **Equipment** | reserved, checked_out, checked_in, overdue | asset_booking |
| **Finance PPM** | created, in_progress, submitted, approved, filed, overdue | finance_task |

---

## Odoo Event Emission

### Pattern (All Events)

```python
from odoo.addons.ipai_enterprise_bridge.utils.ipai_webhook import send_ipai_event

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def action_submit_expenses(self):
        res = super().action_submit_expenses()

        # Get system parameters
        webhook_url = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.url')
        webhook_secret = self.env['ir.config_parameter'].sudo().get_param('ipai.webhook.secret')

        if not webhook_url or not webhook_secret:
            _logger.warning("IPAI webhook not configured, skipping event emission")
            return res

        # Emit event
        for expense in self:
            event = {
                "event_type": "expense.submitted",
                "aggregate_type": "expense",
                "aggregate_id": str(expense.id),
                "payload": {
                    "expense_id": expense.id,
                    "employee_id": expense.employee_id.id,
                    "employee_name": expense.employee_id.name,
                    "employee_code": expense.employee_id.employee_code or "",
                    "amount": float(expense.total_amount),
                    "currency": expense.currency_id.name,
                    "description": expense.name,
                    "date": expense.date.isoformat() if expense.date else None,
                    "category": expense.product_id.name if expense.product_id else "Other",
                    "submitted_at": fields.Datetime.now().isoformat(),
                    "status": "submit"
                }
            }

            try:
                send_ipai_event(webhook_url, webhook_secret, event)
            except Exception as e:
                _logger.error(f"Failed to emit expense.submitted event: {e}")

        return res
```

### Hook Points

**Expense** (`hr.expense`):
- `action_submit_expenses()` → `expense.submitted`
- `approve_expense_sheets()` → `expense.approved`
- `refuse_expense(reason)` → `expense.rejected`
- `action_sheet_move_create()` → `expense.paid`

**Equipment** (`maintenance.equipment` + custom module):
- `action_reserve()` → `asset.reserved`
- `action_checkout()` → `asset.checked_out`
- `action_checkin()` → `asset.checked_in`
- Cron job for overdue detection → `asset.overdue`

**Finance PPM** (`project.task`):
- `write({'stage_id': ...})` → `finance_task.*` (based on stage)
- Cron job for deadline monitoring → `finance_task.overdue`

---

## n8n Workflow Patterns

### Event Router (Main)

```
Trigger: Schedule (Every 30s)
  ↓
HTTP Request: POST /rest/v1/rpc/claim_outbox
  Body: {"p_limit": 25, "p_worker": "n8n-event-router"}
  ↓
Switch: event_type
  ├─ expense.* → Call Expense Handler
  ├─ asset.* → Call Asset Handler
  └─ finance_task.* → Call Finance Handler
  ↓
HTTP Request: POST /rest/v1/rpc/ack_outbox
  Body: {"p_id": "{{ $json.id }}"}
```

### Expense Handler

```
Webhook Trigger: /webhook/expense-handler
  ↓
Switch: event_type
  ├─ expense.submitted:
  │    ↓
  │  HTTP Request: Fetch approver from Odoo
  │    ↓
  │  Mattermost: Send approval notification with buttons
  │    ↓
  │  Return 200 OK
  │
  ├─ expense.approved:
  │    ↓
  │  Supabase: Insert into payment_queue
  │    ↓
  │  Mattermost: Notify Finance team
  │    ↓
  │  Return 200 OK
  │
  └─ expense.rejected:
       ↓
     Mattermost: Notify employee with rejection reason
       ↓
     Return 200 OK
```

### Asset Handler

```
Webhook Trigger: /webhook/asset-handler
  ↓
Switch: event_type
  ├─ asset.reserved:
  │    ↓
  │  Email: Send confirmation to employee
  │    ↓
  │  Google Calendar: Create event
  │    ↓
  │  Supabase: Update asset_availability dashboard
  │    ↓
  │  Return 200 OK
  │
  ├─ asset.checked_out:
  │    ↓
  │  Supabase: Update asset status
  │    ↓
  │  Return 200 OK
  │
  └─ asset.overdue:
       ↓
     Switch: escalation_level
       ├─ Level 1: Email employee
       ├─ Level 2: Email employee + CC manager
       └─ Level 3: Email employee + CC manager + CC IT Admin
       ↓
     Return 200 OK
```

### Finance Handler

```
Webhook Trigger: /webhook/finance-handler
  ↓
Switch: event_type
  ├─ finance_task.submitted:
  │    ↓
  │  HTTP Request: Fetch reviewer from task metadata
  │    ↓
  │  Mattermost: Send review notification with link
  │    ↓
  │  Supabase: Update PPM dashboard
  │    ↓
  │  Return 200 OK
  │
  ├─ finance_task.approved:
  │    ↓
  │  Supabase: Update BIR compliance dashboard
  │    ↓
  │  Return 200 OK
  │
  └─ finance_task.overdue:
       ↓
     HTTP Request: Fetch escalation rules
       ↓
     Mattermost: Send alerts to responsible users
       ↓
     If: overdue_days > 3
       ↓
     Mattermost: Escalate to Finance Director
       ↓
     Return 200 OK
```

---

## MCP Tool Surface

### Supabase RLS Policies (Read-Only for Agents)

**Policy**: Authenticated users can read `event_log`, service role can do everything

```sql
-- Already created in migration
CREATE POLICY "authenticated_read_event_log" ON integration.event_log
  FOR SELECT TO authenticated USING (true);
```

### MCP Server Tools

**Location**: `mcp/servers/odoo-erp-server/tools/integration.ts`

```typescript
{
  name: "query_expense_events",
  description: "Query expense submission events from integration bus",
  inputSchema: {
    type: "object",
    properties: {
      employee_code: { type: "string" },
      status: { type: "string", enum: ["submit", "approve", "cancel", "done"] },
      date_from: { type: "string", format: "date" },
      date_to: { type: "string", format: "date" },
      limit: { type: "number", default: 50 }
    }
  },
  handler: async (args) => {
    const { employee_code, status, date_from, date_to, limit } = args;
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    let query = supabase
      .from("integration.event_log")
      .select("*")
      .eq("aggregate_type", "expense")
      .like("event_type", "expense.%")
      .order("created_at", { ascending: false })
      .limit(limit);

    if (employee_code) {
      query = query.eq("payload->employee_code", employee_code);
    }

    if (status) {
      query = query.eq("payload->status", status);
    }

    if (date_from) {
      query = query.gte("created_at", date_from);
    }

    if (date_to) {
      query = query.lte("created_at", date_to);
    }

    const { data, error } = await query;
    if (error) throw new Error(error.message);

    return { events: data };
  }
}
```

**Usage in Claude Desktop**:
```
User: Show me all expense submissions from employee RIM in the last 7 days

Claude: [Uses query_expense_events tool]
{
  "employee_code": "RIM",
  "date_from": "2026-01-15",
  "limit": 100
}

Response: Found 12 expense submissions for RIM totaling PHP 45,000.00.
Most recent: "Client dinner - Makati" for PHP 1,000.00 on 2026-01-22.
Status: 8 approved, 3 submitted, 1 rejected.
```

---

## Monitoring & Troubleshooting

### Health Checks

```bash
# Check outbox queue depth
supabase db query "SELECT status, COUNT(*) FROM integration.outbox GROUP BY status;"

# Check event log volume (last 24h)
supabase db query "SELECT event_type, COUNT(*) FROM integration.event_log WHERE created_at > NOW() - INTERVAL '24 hours' GROUP BY event_type ORDER BY COUNT DESC;"

# Find stuck jobs
supabase db query "SELECT id, event_type, status, attempts, last_error FROM integration.outbox WHERE status='processing' AND locked_at < NOW() - INTERVAL '10 minutes';"

# Dead letter queue
supabase db query "SELECT id, event_type, aggregate_id, attempts, last_error FROM integration.outbox WHERE status='dead' ORDER BY updated_at DESC;"
```

### Common Issues

**Problem**: Events stuck in `pending` state
**Cause**: n8n event router not running or credential issues
**Fix**:
1. Check n8n workflow is active
2. Verify Supabase credentials in n8n
3. Check n8n logs for errors

**Problem**: Events stuck in `processing` state
**Cause**: Worker crashed without acking/failing
**Fix**:
1. Wait 10 minutes (auto-unlock)
2. Manual unlock: `UPDATE integration.outbox SET status='pending', locked_at=NULL WHERE status='processing';`

**Problem**: Events in `dead` state
**Cause**: Failed after 10 retry attempts
**Fix**:
1. Check `last_error` field
2. Fix root cause (e.g., Mattermost webhook URL)
3. Reset to pending: `UPDATE integration.outbox SET status='pending', attempts=0 WHERE id='...';`

**Problem**: Duplicate events
**Cause**: Odoo retrying without same `idempotency_key`
**Fix**: Ensure Odoo uses stable idempotency key (e.g., `f"{aggregate_type}:{aggregate_id}:{event_type}"`)

---

## Security

### HMAC Signature Verification

**Edge Function** verifies:
1. `x-ipai-timestamp` within 5-minute window (replay protection)
2. `x-ipai-signature` matches `HMAC-SHA256(secret, "${ts}.${raw_body}")`
3. `x-idempotency-key` prevents duplicate processing

**Odoo Emitter** (`ipai_webhook.py`):
- Generates HMAC signature with shared secret
- Uses millisecond timestamp for replay window
- Generates UUID for idempotency (or uses stable key)

### RLS Policies

- **Service Role**: Full access to `outbox`, `event_log`, `id_map`
- **Authenticated Users**: Read-only access to `event_log`
- **Anon**: No access (MCP tools must use authenticated sessions)

### Secrets Management

**Supabase**:
- `ODOO_WEBHOOK_SECRET` stored in Supabase secrets (never in code)
- Service role key in n8n credentials (encrypted)

**Odoo**:
- `ipai.webhook.secret` stored as Odoo system parameter (access via `sudo()`)
- Never logged or exposed in UI

---

## Deployment Checklist

- [ ] Supabase project linked: `supabase link --project-ref spdtwktxdalcfigzeqrz`
- [ ] Migrations deployed: `supabase db push`
- [ ] Edge Function deployed: `supabase functions deploy odoo-webhook`
- [ ] Secrets set: `supabase secrets set ODOO_WEBHOOK_SECRET='...'`
- [ ] Odoo system parameters configured (webhook URL + secret)
- [ ] Odoo module installed: `ipai_enterprise_bridge`
- [ ] Event emission hooks added to Odoo models
- [ ] n8n workflows imported and activated
- [ ] End-to-end test passed: expense submission → Mattermost notification
- [ ] Monitoring dashboard configured (Superset/Tableau)
- [ ] Dead letter queue alerts configured (Mattermost webhook)

---

## Next Steps

1. **Add More Events**: Extend taxonomy for invoices, POs, timesheets
2. **MCP Tool Expansion**: Add write-back tools for approvals (with capability grants)
3. **CMS Integration**: Git-backed Markdown → Supabase ingestion for SOPs
4. **Advanced n8n**: Conditional routing, multi-stage approvals, SLA tracking
5. **Analytics**: Event volume dashboard in Superset/Tableau

---

**Status**: Ready for Production
**Contact**: Jake Tolentino (Finance SSC Manager)
**Last Updated**: 2026-01-22
