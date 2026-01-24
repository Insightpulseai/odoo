# Supabase Integration Bus - Deployment Guide

## Overview

The IPAI Integration Bus enables real-time event-driven communication between Odoo CE and external systems via Supabase.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Integration Bus Architecture                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Odoo CE 18.0                                                              │
│   ├── hr.expense (4 events)                                                 │
│   ├── maintenance.equipment (4 events)                                      │
│   └── project.task [finance] (6 events)                                     │
│           │                                                                  │
│           │ HMAC-SHA256 signed webhook                                       │
│           ▼                                                                  │
│   ┌───────────────────────────────────────┐                                 │
│   │ Supabase Edge Function (odoo-webhook) │                                 │
│   │ - Signature verification               │                                 │
│   │ - Replay protection (5 min window)     │                                 │
│   └───────────────────────────────────────┘                                 │
│           │                                                                  │
│           │ RPC calls                                                        │
│           ▼                                                                  │
│   ┌───────────────────────────────────────┐                                 │
│   │ integration.outbox                     │ ← Durable queue                │
│   │ - status: pending/processing/done/dead │                                │
│   │ - retry with exponential backoff       │                                │
│   └───────────────────────────────────────┘                                 │
│           │                                                                  │
│   ┌───────────────────────────────────────┐                                 │
│   │ integration.event_log                  │ ← Immutable audit trail        │
│   └───────────────────────────────────────┘                                 │
│           │                                                                  │
│           │ Poll every 30s (claim_outbox with SKIP LOCKED)                  │
│           ▼                                                                  │
│   ┌───────────────────────────────────────┐                                 │
│   │ n8n Event Router                       │                                │
│   │ - Claims batch of 25 events            │                                │
│   │ - Routes by event_type prefix          │                                │
│   └───────────────────────────────────────┘                                 │
│           │                                                                  │
│           ├── expense.* → Expense Handler                                   │
│           ├── asset.* → Asset Handler                                       │
│           └── finance_task.* → Finance Handler                              │
│                   │                                                          │
│                   ▼                                                          │
│   ┌───────────────────────────────────────┐                                 │
│   │ Mattermost Notifications               │                                │
│   │ - #finance-notifications               │                                │
│   │ - #operations-notifications            │                                │
│   └───────────────────────────────────────┘                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Event Types

### Expense Domain (`expense.*`)

| Event | Trigger | Notification Channel |
|-------|---------|---------------------|
| `expense.submitted` | Employee submits expense | #finance-notifications |
| `expense.approved` | Manager approves expense | #finance-notifications |
| `expense.rejected` | Manager rejects expense | #finance-notifications |
| `expense.paid` | Expense posted/paid | #finance-notifications |

### Asset Domain (`asset.*`)

| Event | Trigger | Notification Channel |
|-------|---------|---------------------|
| `asset.reserved` | Equipment reserved | #operations-notifications |
| `asset.checked_out` | Equipment checked out | #operations-notifications |
| `asset.checked_in` | Equipment returned | #operations-notifications |
| `asset.overdue` | Return deadline passed | #operations-notifications |

### Finance Task Domain (`finance_task.*`)

| Event | Trigger | Notification Channel |
|-------|---------|---------------------|
| `finance_task.created` | Finance task created | #finance-notifications |
| `finance_task.in_progress` | Task work started | #finance-notifications |
| `finance_task.submitted` | Task submitted for review | #finance-notifications |
| `finance_task.approved` | Task approved | #finance-notifications |
| `finance_task.filed` | Task filed/completed | #finance-notifications |
| `finance_task.overdue` | Deadline passed | #finance-notifications |

## Deployment Steps

### Step 1: Supabase Infrastructure

The migration file is already in place:

```bash
# Apply migration (if not already applied)
supabase db push
# OR via psql:
psql "$SUPABASE_DB_URL" -f supabase/migrations/20260122000100_integration_bus.sql
```

### Step 2: Deploy Edge Function

```bash
# Deploy the odoo-webhook Edge Function
supabase functions deploy odoo-webhook

# Set the webhook secret
supabase secrets set WEBHOOK_SECRET="your-shared-secret"
```

### Step 3: Configure Odoo

```bash
# Set webhook parameters
./scripts/integration/configure-odoo-params.sh --docker

# Update the module
docker exec odoo-core odoo -d odoo_core -u ipai_enterprise_bridge --stop-after-init
```

### Step 4: Import n8n Workflows

1. Access n8n web interface
2. Go to **Workflows → Import from File**
3. Import workflows in order:
   - `n8n/workflows/integration/expense-handler.json`
   - `n8n/workflows/integration/asset-handler.json`
   - `n8n/workflows/integration/finance-handler.json`
   - `n8n/workflows/integration/event-router.json`
4. Configure credentials on HTTP Request nodes
5. Set environment variables:
   - `SUPABASE_URL`
   - `N8N_WEBHOOK_BASE_URL`
   - `MATTERMOST_WEBHOOK_URL`
   - `ODOO_BASE_URL`
6. Activate all workflows

### Step 5: Test End-to-End

```bash
# Run integration test
./scripts/integration/test-expense-flow.sh
```

## Files

### Supabase Migration
- `supabase/migrations/20260122000100_integration_bus.sql`

### Odoo Models
- `addons/ipai/ipai_enterprise_bridge/models/hr_expense_integration.py`
- `addons/ipai/ipai_enterprise_bridge/models/maintenance_equipment_integration.py`
- `addons/ipai/ipai_enterprise_bridge/models/project_task_integration.py`

### n8n Workflows
- `n8n/workflows/integration/event-router.json`
- `n8n/workflows/integration/expense-handler.json`
- `n8n/workflows/integration/asset-handler.json`
- `n8n/workflows/integration/finance-handler.json`

### Scripts
- `scripts/integration/configure-odoo-params.sh`
- `scripts/integration/configure-odoo-params.sql`
- `scripts/integration/test-expense-flow.sh`

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Supabase Integration
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
IPAI_WEBHOOK_SECRET=your-shared-secret-here

# n8n
N8N_WEBHOOK_BASE_URL=https://n8n.example.com

# Mattermost
MATTERMOST_WEBHOOK_URL=https://mm.example.com/hooks/xxx

# Odoo
ODOO_BASE_URL=https://odoo.example.com
```

### Odoo System Parameters

| Key | Value |
|-----|-------|
| `ipai.webhook.url` | Edge Function URL |
| `ipai.webhook.secret` | HMAC signing secret |

## Monitoring

### Check Queue Health

```sql
-- Queue depth by status
SELECT status, COUNT(*) as count
FROM integration.outbox
GROUP BY status;

-- Recent events
SELECT event_type, status, created_at, updated_at
FROM integration.outbox
ORDER BY created_at DESC
LIMIT 20;
```

### Check Dead Letter Queue

```sql
SELECT id, event_type, last_error, attempts, created_at
FROM integration.outbox
WHERE status = 'dead'
ORDER BY updated_at DESC;
```

### Event Log Audit

```sql
SELECT event_type, source, COUNT(*) as count
FROM integration.event_log
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type, source
ORDER BY count DESC;
```

## Troubleshooting

### Events Not Being Processed

1. **Check Event Router is running**: Verify workflow is active in n8n
2. **Check credentials**: Ensure Supabase API credential is valid
3. **Check RLS**: Service role key required for claim_outbox

### Signature Verification Failed

1. **Check timestamp**: Ensure server clocks are synchronized
2. **Check secret**: Same secret in Odoo and Edge Function
3. **Check payload encoding**: UTF-8 JSON encoding

### Notifications Not Arriving

1. **Check Mattermost webhook**: Test with curl
2. **Check channel name**: Matches n8n workflow
3. **Check n8n execution logs**: Look for HTTP errors

## Security

- **HMAC-SHA256 signatures**: All events cryptographically signed
- **Replay protection**: 5-minute timestamp window
- **Idempotency keys**: Prevent duplicate processing
- **RLS policies**: Row-level security on all tables
- **Service role only**: Write operations require service role

## Performance

| Metric | Value |
|--------|-------|
| Poll interval | 30 seconds |
| Batch size | 25 events |
| Lock timeout | 10 minutes |
| Max retries | 9 (then dead letter) |
| Retry backoff | 30s × attempt |

---

*Last updated: 2026-01-22*
