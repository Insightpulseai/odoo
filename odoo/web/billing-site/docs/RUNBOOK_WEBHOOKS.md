# Webhook Runbook

## Overview

This runbook covers Paddle webhook handling, verification, testing, and replay procedures.

## Webhook Events

### Supported Events

| Event | Description | Action |
|-------|-------------|--------|
| `customer.created` | New customer created | Upsert billing.customers |
| `customer.updated` | Customer info updated | Update billing.customers |
| `subscription.created` | New subscription | Create billing.subscriptions, provision Odoo |
| `subscription.activated` | Subscription activated | Update status |
| `subscription.updated` | Subscription changed | Update billing.subscriptions |
| `subscription.canceled` | Subscription canceled | Mark as canceled |
| `transaction.completed` | Transaction completed | Create billing.invoices |
| `transaction.paid` | Payment received | Update invoice status |

## Signature Verification

Paddle uses HMAC-SHA256 to sign webhooks:

```
signature = HMAC-SHA256(timestamp + ":" + payload, webhook_secret)
header = "ts={timestamp};h1={signature}"
```

### Verification Code

```typescript
import crypto from 'crypto'

function verifyPaddleWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const [tsPart, h1Part] = signature.split(';')
  const timestamp = tsPart.replace('ts=', '')
  const expectedSig = h1Part.replace('h1=', '')

  const signedPayload = `${timestamp}:${payload}`
  const hmac = crypto.createHmac('sha256', secret)
  hmac.update(signedPayload)
  const calculatedSig = hmac.digest('hex')

  return crypto.timingSafeEqual(
    Buffer.from(calculatedSig, 'hex'),
    Buffer.from(expectedSig, 'hex')
  )
}
```

## Testing Webhooks

### Local Testing with Paddle CLI

```bash
# Install Paddle CLI
npm install -g @paddle/paddle-cli

# Simulate webhook
paddle webhook test \
  --url http://localhost:3001/api/webhooks/paddle \
  --event subscription.created \
  --secret $PADDLE_WEBHOOK_SECRET
```

### Unit Test

```bash
# Run webhook tests
pnpm test --filter paddle

# Example test
pnpm vitest run src/lib/__tests__/paddle.test.ts
```

### Manual cURL Test

```bash
# Generate test payload
TIMESTAMP=$(date +%s)
PAYLOAD='{"event_type":"subscription.created","event_id":"evt_test","data":{"id":"sub_123","customer_id":"ctm_123","status":"active"}}'

# Generate signature
SIGNATURE=$(echo -n "$TIMESTAMP:$PAYLOAD" | openssl dgst -sha256 -hmac "$PADDLE_WEBHOOK_SECRET" | cut -d' ' -f2)

# Send request
curl -X POST http://localhost:3001/api/webhooks/paddle \
  -H "Content-Type: application/json" \
  -H "paddle-signature: ts=$TIMESTAMP;h1=$SIGNATURE" \
  -d "$PAYLOAD"
```

## Webhook Replay

### Query Failed Webhooks

```sql
-- Find unprocessed webhooks
SELECT id, event_id, event_type, error, created_at
FROM billing.webhook_events
WHERE NOT processed
ORDER BY created_at DESC
LIMIT 20;
```

### Replay Single Webhook

```sql
-- Get payload to replay
SELECT payload FROM billing.webhook_events
WHERE event_id = 'evt_12345';
```

```bash
# Replay via API (internal endpoint)
curl -X POST http://localhost:3001/api/webhooks/paddle/replay \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -d '{"event_id": "evt_12345"}'
```

### Bulk Replay

```bash
#!/bin/bash
# Replay all failed webhooks from last 24 hours

psql "$DATABASE_URL" -t -c "
  SELECT event_id FROM billing.webhook_events
  WHERE NOT processed
    AND created_at > NOW() - INTERVAL '24 hours'
" | while read event_id; do
  echo "Replaying $event_id..."
  curl -X POST http://localhost:3001/api/webhooks/paddle/replay \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -d "{\"event_id\": \"$event_id\"}"
  sleep 1
done
```

## Monitoring

### Key Metrics

```sql
-- Webhook success rate (last 7 days)
SELECT
  DATE(created_at) as date,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE processed) as success,
  COUNT(*) FILTER (WHERE NOT processed AND error IS NOT NULL) as failed,
  ROUND(100.0 * COUNT(*) FILTER (WHERE processed) / COUNT(*), 2) as success_rate
FROM billing.webhook_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Events by type
SELECT event_type, COUNT(*) as count
FROM billing.webhook_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY event_type
ORDER BY count DESC;
```

### Alerts

Set up alerts for:
- Webhook success rate < 95%
- Unprocessed webhooks > 10 in queue
- Processing latency > 5 seconds

## Troubleshooting

### Invalid Signature (401)

1. Verify `PADDLE_WEBHOOK_SECRET` matches Paddle dashboard
2. Check timestamp is within tolerance (5 min)
3. Ensure raw body is used (not parsed JSON)

### Processing Failures (500)

1. Check Vercel function logs
2. Look at `billing.webhook_events.error` column
3. Verify Supabase connection
4. Check RLS policies allow service role

### Missing Events

1. Check Paddle webhook dashboard for delivery status
2. Verify webhook URL is correct in Paddle
3. Check all required events are enabled

### Duplicate Events

Paddle may retry failed webhooks. Handling is idempotent:
- Use `event_id` as unique constraint
- Upsert operations prevent duplicates

## Security Best Practices

1. **Always verify signatures** - Never skip verification in production
2. **Use HTTPS** - Webhook endpoints must use TLS
3. **Log all events** - Keep audit trail for debugging
4. **Rate limit** - Protect against webhook flooding
5. **Timeout handling** - Return 200 quickly, process async if needed
