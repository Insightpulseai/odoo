# IPAI Integration Bus - n8n Workflows

This directory contains the n8n workflows for the IPAI Supabase Integration Bus.

## Architecture

```
Odoo → Supabase Edge Function → integration.outbox table
                                        ↓
                                  n8n event-router (polls every 30s)
                                        ↓
                      ┌─────────────────┼─────────────────┐
                      ↓                 ↓                 ↓
              expense-handler   asset-handler   finance-handler
                      ↓                 ↓                 ↓
                           Mattermost / Email
```

## Workflows

### 1. event-router.json
**Purpose**: Main polling workflow that claims events from Supabase and routes to domain handlers

**Flow**:
1. Schedule trigger (every 30 seconds)
2. Call `claim_outbox` RPC (claims up to 25 pending events with SKIP LOCKED)
3. Route by event type:
   - `expense.*` → expense-handler
   - `asset.*` → asset-handler
   - `finance_task.*` → finance-handler
4. Call domain handler webhook
5. Acknowledge success (`ack_outbox`) or failure (`fail_outbox`)

**Environment Variables**:
- `SUPABASE_URL` - Supabase project URL
- `N8N_WEBHOOK_BASE_URL` - Base URL for n8n webhooks (e.g., `https://n8n.example.com`)

**Required Credentials**:
- Supabase API credential (service_role key)

### 2. expense-handler.json
**Purpose**: Process expense lifecycle events and send Mattermost notifications

**Events Handled**:
- `expense.submitted` 📝 - Expense submitted for approval
- `expense.approved` ✅ - Expense approved by manager
- `expense.rejected` ❌ - Expense rejected with reason
- `expense.paid` 💰 - Expense payment completed

**Environment Variables**:
- `MATTERMOST_WEBHOOK_URL` - Incoming webhook URL for Mattermost channel
- `ODOO_BASE_URL` - Odoo instance URL for deep links

### 3. asset-handler.json
**Purpose**: Process asset booking lifecycle events

**Events Handled**:
- `asset.reserved` 📅 - Asset reserved for future use
- `asset.checked_out` 📤 - Asset physically checked out
- `asset.checked_in` 📥 - Asset returned
- `asset.overdue` ⚠️ - Asset not returned by deadline

**Environment Variables**:
- `MATTERMOST_WEBHOOK_URL` - Incoming webhook URL
- `ODOO_BASE_URL` - Odoo instance URL

### 4. finance-handler.json
**Purpose**: Process Finance PPM task lifecycle events (BIR compliance)

**Events Handled**:
- `finance_task.created` 📋 - BIR task auto-created from schedule
- `finance_task.in_progress` 🔄 - Task work started
- `finance_task.submitted` ✅ - Task submitted for review
- `finance_task.approved` ✅ - Task approved by finance manager
- `finance_task.filed` 📄 - BIR form filed with government
- `finance_task.overdue` 🚨 - Task past deadline (URGENT)

**Environment Variables**:
- `MATTERMOST_WEBHOOK_URL` - Incoming webhook URL
- `ODOO_BASE_URL` - Odoo instance URL

## Import Instructions

### 1. Configure Environment Variables

In n8n Settings → Environments, add:

```bash
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
N8N_WEBHOOK_BASE_URL=https://n8n.insightpulseai.net
MATTERMOST_WEBHOOK_URL=https://mattermost.example.com/hooks/xxx-your-webhook-id-xxx
ODOO_BASE_URL=https://odoo.insightpulseai.net
```

### 2. Configure Supabase Credentials

In n8n Settings → Credentials, create a new "Supabase API" credential:
- **Name**: `IPAI Supabase`
- **Host**: `spdtwktxdalcfigzeqrz.supabase.co`
- **Service Role Secret**: (paste your `SUPABASE_SERVICE_ROLE_KEY`)

### 3. Import Workflows

For each workflow file:

1. Go to n8n → Workflows → Import from File
2. Select the JSON file
3. Click "Import"
4. Open the imported workflow
5. Update credential selections if needed
6. Click "Save"

**Import Order** (domain handlers must exist before event-router):
1. ✅ expense-handler.json
2. ✅ asset-handler.json
3. ✅ finance-handler.json
4. ✅ event-router.json (imports last, references the handlers)

### 4. Activate Workflows

After import, activate each workflow:
1. Open the workflow
2. Toggle "Active" switch to ON
3. Verify the Schedule trigger shows "Active" status

### 5. Verify Webhooks

Test that domain handler webhooks are accessible:

```bash
# Test expense-handler
curl -X POST https://n8n.insightpulseai.net/webhook/expense-handler \
  -H "Content-Type: application/json" \
  -d '{"event_type":"expense.submitted","payload":{"employee_name":"Test","amount":100}}'

# Expected: {"ok":true}
```

## Monitoring

### Check Event Router Execution

1. Go to n8n → Executions
2. Filter by workflow: "IPAI Event Router (Integration Bus)"
3. Check for:
   - Regular executions every 30 seconds
   - Successful status (green checkmark)
   - Events claimed and routed

### Check Outbox Status (Supabase)

```sql
-- View pending events
SELECT id, source, event_type, aggregate_type, status, attempts, created_at
FROM integration.outbox
WHERE status = 'pending'
ORDER BY created_at ASC
LIMIT 25;

-- View processing events (should be empty or very few)
SELECT id, event_type, locked_at, locked_by, attempts
FROM integration.outbox
WHERE status = 'processing';

-- View failed events (need attention)
SELECT id, event_type, attempts, last_error, created_at
FROM integration.outbox
WHERE status = 'failed'
ORDER BY created_at DESC;
```

### Check Event Log (Audit Trail)

```sql
-- View recent events by type
SELECT event_type, COUNT(*) as count, MAX(created_at) as last_seen
FROM integration.event_log
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY event_type
ORDER BY count DESC;
```

## Troubleshooting

### Events Not Being Claimed

**Symptom**: Outbox has pending events but event-router shows 0 items

**Causes**:
1. Supabase credential not configured or expired
2. RPC function `claim_outbox` not accessible (check public wrappers)
3. Network connectivity issue

**Fix**:
```sql
-- Verify public wrapper exists
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name = 'claim_outbox';

-- Test RPC directly
SELECT * FROM claim_outbox(5, 'test-worker');
```

### Events Stuck in 'processing'

**Symptom**: Events locked but never acknowledged

**Causes**:
1. Domain handler webhook unreachable
2. Domain handler crashed mid-execution
3. Network timeout

**Fix**:
```sql
-- Unlock stuck events (after 10 minutes)
UPDATE integration.outbox
SET status = 'pending',
    locked_at = NULL,
    locked_by = NULL,
    attempts = attempts + 1
WHERE status = 'processing'
  AND locked_at < NOW() - INTERVAL '10 minutes';
```

### Mattermost Notifications Not Appearing

**Causes**:
1. `MATTERMOST_WEBHOOK_URL` incorrect or expired
2. Webhook not enabled in Mattermost channel settings
3. Message format invalid

**Fix**:
```bash
# Test webhook directly
curl -X POST https://mattermost.example.com/hooks/xxx \
  -H "Content-Type: application/json" \
  -d '{"text":"Test from n8n integration bus"}'

# Expected: {"text":"Test from n8n integration bus","ok":true}
```

### High Event Failure Rate

**Symptom**: Many events in `status='failed'` with `attempts >= 3`

**Investigation**:
```sql
-- Group failures by error message
SELECT last_error, COUNT(*) as count
FROM integration.outbox
WHERE status = 'failed'
GROUP BY last_error
ORDER BY count DESC;
```

**Common Errors**:
- `"404 Not Found"` → Domain handler webhook not imported/activated
- `"401 Unauthorized"` → Supabase credential issue
- `"Timeout"` → Network or performance issue

## Performance Tuning

### Adjust Polling Interval

Event router polls every 30 seconds by default. Adjust based on load:

**Low volume** (< 100 events/hour): 60 seconds
```json
"interval": [{"field": "seconds", "secondsInterval": 60}]
```

**Medium volume** (100-500 events/hour): 30 seconds (current)

**High volume** (> 500 events/hour): 10 seconds
```json
"interval": [{"field": "seconds", "secondsInterval": 10}]
```

### Adjust Batch Size

Event router claims 25 events per batch. Increase for high volume:

```json
"bodyParameters": {
  "parameters": [
    {"name": "p_limit", "value": "50"}  // Was 25
  ]
}
```

**Note**: Higher batch size increases memory usage and execution time.

## Security

### HMAC Signature Verification (Already Implemented)

Events from Odoo are HMAC-signed and verified by the Supabase Edge Function before insertion. n8n does NOT need to re-verify signatures.

### RLS Policies

The integration schema has RLS policies:
- Service role: Full CRUD access
- Authenticated users: Read-only access (for MCP agents)
- Anonymous users: No access

### Webhook Security

Domain handler webhooks are **internal only** (called from event-router, not exposed publicly). No additional authentication required.

## References

- **Architecture Doc**: `docs/INTEGRATION_BUS.md`
- **Supabase Migration**: `supabase/migrations/20260122000100_integration_bus.sql`
- **Edge Function**: `supabase/functions/odoo-webhook/index.ts`
- **Odoo Event Hooks**: `addons/ipai/ipai_enterprise_bridge/models/*_integration.py`
