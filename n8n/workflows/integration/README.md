# IPAI Integration Bus - n8n Workflows

Event-driven workflows for processing Odoo events from the Supabase integration bus.

## Architecture

```
Odoo CE 18.0 (Events)
    ↓ HMAC-signed webhook
Supabase Edge Function
    ↓ RPC
integration.outbox (durable queue)
    ↓ Poll every 30s
n8n Event Router (claim_outbox)
    ↓ Route by event_type prefix
Domain Handlers
    ↓ Format & send
Mattermost / Email
```

## Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Event Router | `event-router.json` | Schedule (30s) | Claims events from outbox, routes to handlers |
| Expense Handler | `expense-handler.json` | Webhook | Processes expense lifecycle events |
| Asset Handler | `asset-handler.json` | Webhook | Processes asset/equipment events |
| Finance Handler | `finance-handler.json` | Webhook | Processes finance task events |

## Event Types

### Expense Events (`expense.*`)
- `expense.submitted` - Employee submitted expense for approval
- `expense.approved` - Manager approved expense
- `expense.rejected` - Manager rejected expense
- `expense.paid` - Expense posted/paid

### Asset Events (`asset.*`)
- `asset.reserved` - Equipment reserved for employee
- `asset.checked_out` - Equipment checked out
- `asset.checked_in` - Equipment returned
- `asset.overdue` - Equipment overdue for return

### Finance Task Events (`finance_task.*`)
- `finance_task.created` - New finance/compliance task created
- `finance_task.in_progress` - Task work started
- `finance_task.submitted` - Task submitted for review
- `finance_task.approved` - Task approved
- `finance_task.filed` - Task filed/completed
- `finance_task.overdue` - Task past deadline

## Environment Variables

Configure these in n8n Settings → Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://spdtwktxdalcfigzeqrz.supabase.co` |
| `N8N_WEBHOOK_BASE_URL` | Base URL for n8n webhooks | `https://n8n.example.com` |
| `MATTERMOST_WEBHOOK_URL` | Mattermost incoming webhook | `https://mm.example.com/hooks/xxx` |
| `ODOO_BASE_URL` | Odoo instance URL for deep links | `https://odoo.example.com` |

## Credentials

Create a Supabase API credential in n8n:
1. Go to Credentials → Add Credential → Supabase API
2. Name: `Supabase Integration Bus`
3. API URL: `https://spdtwktxdalcfigzeqrz.supabase.co`
4. Service Role Key: (from Supabase dashboard → Settings → API)

## Import Instructions

1. Open n8n web interface
2. Go to Workflows → Import from File
3. Import in this order:
   - `expense-handler.json`
   - `asset-handler.json`
   - `finance-handler.json`
   - `event-router.json` (last, as it calls the handlers)
4. Configure credentials on each HTTP Request node that uses Supabase
5. Activate all workflows

## Testing

### Test Event Router
```bash
# Manually insert a test event
curl -X POST "$SUPABASE_URL/rest/v1/integration.outbox" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "event_type": "expense.submitted",
    "aggregate_type": "expense",
    "aggregate_id": "hr.expense,999",
    "payload": {"expense_id": 999, "name": "Test Expense", "employee_name": "Test User", "total_amount": 100.00, "currency": "PHP"},
    "idempotency_key": "test-expense-'$(date +%s)'"
  }'
```

### Test Individual Handler
```bash
# Direct webhook test
curl -X POST "https://n8n.example.com/webhook/expense-handler" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "expense.submitted",
    "payload": {
      "expense_id": 999,
      "name": "Test Expense",
      "employee_name": "Test User",
      "total_amount": 100.00,
      "currency": "PHP"
    }
  }'
```

## Monitoring

### Check Queue Depth
```sql
SELECT status, COUNT(*)
FROM integration.outbox
GROUP BY status;
```

### Check Recent Events
```sql
SELECT event_type, created_at, status
FROM integration.outbox
ORDER BY created_at DESC
LIMIT 20;
```

### Check Dead Letter Queue
```sql
SELECT * FROM integration.outbox
WHERE status = 'dead'
ORDER BY updated_at DESC;
```

## Troubleshooting

### Events Not Being Claimed
1. Check Event Router workflow is active
2. Verify Supabase credentials are valid
3. Check for RLS policy issues (use service role key)

### Notifications Not Sending
1. Verify `MATTERMOST_WEBHOOK_URL` is correct
2. Check Mattermost channel exists and webhook is enabled
3. Review n8n execution logs for HTTP errors

### Duplicate Notifications
1. Check `idempotency_key` in outbox
2. Verify `ack_outbox` is being called after processing
3. Check for workflow timeout/retry issues

## Performance Tuning

### Increase Throughput
- Decrease poll interval (default: 30s)
- Increase `p_limit` in `claim_outbox` call (default: 25)
- Run multiple Event Router instances with different worker IDs

### Reduce Latency
- Use webhook-based trigger instead of polling (requires additional Edge Function)
- Co-locate n8n with Supabase region

## Security

- All events are HMAC-SHA256 signed by Odoo
- Edge Function verifies signature before storing
- n8n uses service role key (server-side only)
- RLS policies prevent unauthorized access
