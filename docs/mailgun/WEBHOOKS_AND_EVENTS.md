# Mailgun Webhooks and Events

**Purpose**: Configure Mailgun webhooks to receive real-time email event notifications

**Use Cases**:
- Track email delivery status (delivered, bounced, failed)
- Monitor spam complaints and unsubscribes
- Log email events for compliance and debugging
- Trigger automated workflows based on email events

---

## Official Mailgun Webhook Documentation

**Source**: https://documentation.mailgun.com/docs/mailgun/user-manual/webhooks/

Mailgun sends HTTP POST requests to configured webhook URLs when email events occur.

---

## Event Types (Official)

### Delivery Events

| Event | Description | When Triggered |
|-------|-------------|----------------|
| `delivered` | Email successfully delivered to recipient's server | SMTP 250 OK response from recipient |
| `failed` | Permanent delivery failure | Hard bounce (invalid address, domain doesn't exist) |
| `temporary-failed` | Temporary delivery failure | Soft bounce (mailbox full, server down) |

### Engagement Events

| Event | Description | When Triggered |
|-------|-------------|----------------|
| `opened` | Recipient opened email | Tracking pixel loaded (requires tracking enabled) |
| `clicked` | Recipient clicked link in email | Link click (requires tracking enabled) |
| `unsubscribed` | Recipient clicked unsubscribe link | Unsubscribe link clicked |
| `complained` | Recipient marked email as spam | Spam complaint (FBL feedback loop) |

### Additional Events

| Event | Description | When Triggered |
|-------|-------------|----------------|
| `accepted` | Mailgun accepted email for delivery | Immediately after API call |
| `rejected` | Mailgun rejected email | Suppression list, invalid format, spam content |
| `stored` | Email stored via Routes | Route uses `store()` action |

---

## Webhook Configuration (Mailgun Dashboard)

### Step 1: Navigate to Webhooks

1. Go to: https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net/webhooks
2. Click **"Add Webhook"**

### Step 2: Configure Webhook

**Example: Track Delivery Status**

| Field | Value |
|-------|-------|
| **Event Type** | `delivered` |
| **URL** | `https://ipa.insightpulseai.net/webhooks/mailgun/delivered` |

**Repeat for additional event types** (failed, opened, clicked, etc.)

### Step 3: Test Webhook

1. Click **"Test Webhook"** button
2. Mailgun sends sample POST request to your URL
3. **Expected**: Webhook responds with HTTP 200 OK
4. Check n8n/Odoo logs for received test data

---

## Webhook Payload (JSON)

### Delivered Event

```json
{
  "signature": {
    "token": "06c96bafc3408e745d95b0098a8d5b7e4ac37b7c3e624b17fb1f",
    "timestamp": "1705228800",
    "signature": "5f4b7e3c8f2a9d1b6e5c7f8a3d2e1b9c4a6d8e2f7b1c3a5d"
  },
  "event-data": {
    "event": "delivered",
    "timestamp": 1705228800.123,
    "id": "Ase7i2zsRYeDXztHGENqRA",
    "message": {
      "headers": {
        "message-id": "20260114120000.1.ABCD1234@mg.insightpulseai.net",
        "from": "noreply@mg.insightpulseai.net",
        "to": "recipient@example.com",
        "subject": "Expense Approval Required - EXP-2026-001"
      }
    },
    "recipient": "recipient@example.com",
    "delivery-status": {
      "message": "OK",
      "code": 250,
      "description": "Message accepted"
    },
    "tags": ["expense-approval", "production"]
  }
}
```

### Failed Event (Permanent)

```json
{
  "event-data": {
    "event": "failed",
    "severity": "permanent",
    "reason": "bounce",
    "delivery-status": {
      "message": "550 5.1.1 The email account does not exist",
      "code": 550
    },
    "recipient": "invalid@example.com"
  }
}
```

### Opened Event (Requires Tracking)

```json
{
  "event-data": {
    "event": "opened",
    "timestamp": 1705228850.456,
    "recipient": "recipient@example.com",
    "ip": "203.0.113.42",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "client-info": {
      "client-name": "Gmail",
      "client-type": "webmail",
      "device-type": "desktop"
    }
  }
}
```

---

## Webhook Security (Signature Verification)

**Purpose**: Verify webhook requests are from Mailgun (prevent spoofing)

**Official Documentation**: https://documentation.mailgun.com/docs/mailgun/user-manual/webhooks/#securing-webhooks

### Signature Fields

| Field | Description |
|-------|-------------|
| `token` | Random 50-character string |
| `timestamp` | Unix timestamp when event occurred |
| `signature` | HMAC-SHA256 signature of `timestamp + token` |

### Verification Algorithm (Python)

```python
import hmac
import hashlib
import os

def verify_mailgun_webhook(signature_data):
    """
    Verify Mailgun webhook signature
    Args:
        signature_data: Dict with keys: token, timestamp, signature
    Returns:
        bool: True if signature is valid
    """
    token = signature_data['token']
    timestamp = signature_data['timestamp']
    signature = signature_data['signature']

    # Retrieve signing key from environment
    signing_key = os.environ['MAILGUN_WEBHOOK_SIGNING_KEY']

    # Compute HMAC-SHA256
    hmac_digest = hmac.new(
        key=signing_key.encode(),
        msg=f'{timestamp}{token}'.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Constant-time comparison
    return hmac.compare_digest(signature, hmac_digest)
```

### n8n Webhook Implementation

**n8n Workflow**: Webhook → Function (Verify Signature) → Process Event

**Function Node Code**:
```javascript
const crypto = require('crypto');

// Extract signature fields
const token = $json.signature.token;
const timestamp = $json.signature.timestamp;
const signature = $json.signature.signature;

// Get signing key from environment
const signingKey = $env('MAILGUN_WEBHOOK_SIGNING_KEY');

// Compute HMAC-SHA256
const hmacDigest = crypto
  .createHmac('sha256', signingKey)
  .update(`${timestamp}${token}`)
  .digest('hex');

// Verify signature
if (signature !== hmacDigest) {
  throw new Error('Invalid Mailgun webhook signature');
}

// Return event data for processing
return $json['event-data'];
```

**Signing Key Location**: Mailgun Dashboard → Settings → Webhooks → "HTTP Webhook Signing Key"

---

## Example Use Cases (TBWA\SMP)

### Use Case 1: Email Delivery Monitoring

**Goal**: Track expense approval email delivery status

**n8n Workflow**:
1. **Webhook**: Receive `delivered` or `failed` events
2. **Function**: Verify signature
3. **HTTP Request**: Query Odoo expense record by message-id
4. **Edit**: Update expense status field (email_sent_at, email_status)
5. **Mattermost**: Notify if delivery failed

**Webhook URL**: `https://ipa.insightpulseai.net/webhooks/mailgun/delivery-status`

### Use Case 2: Bounce Handling

**Goal**: Mark user email addresses as invalid after hard bounces

**n8n Workflow**:
1. **Webhook**: Receive `failed` event with `severity: permanent`
2. **Function**: Verify signature + extract recipient email
3. **HTTP Request**: Update Odoo user record (mark email as bounced)
4. **Mattermost**: Alert admin to update user's email

**Webhook URL**: `https://ipa.insightpulseai.net/webhooks/mailgun/bounces`

### Use Case 3: Spam Complaint Handling

**Goal**: Automatically unsubscribe users who mark emails as spam

**n8n Workflow**:
1. **Webhook**: Receive `complained` event
2. **Function**: Verify signature
3. **HTTP Request**: Add recipient to Mailgun suppression list
4. **Odoo XML-RPC**: Update user preferences (opt-out from emails)
5. **Log**: Record complaint in compliance log

**Webhook URL**: `https://ipa.insightpulseai.net/webhooks/mailgun/complaints`

### Use Case 4: Email Engagement Analytics

**Goal**: Track which users open expense approval emails

**Prerequisites**: Enable tracking in Mailgun (Settings → Domain → Tracking)

**n8n Workflow**:
1. **Webhook**: Receive `opened` event
2. **Function**: Verify signature + extract user-agent/IP
3. **Supabase**: Insert analytics record
4. **Dashboard**: Visualize engagement metrics in Superset

**Webhook URL**: `https://ipa.insightpulseai.net/webhooks/mailgun/engagement`

---

## Webhook Configuration via API

### Create Webhook

```bash
curl -X POST --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/domains/mg.insightpulseai.net/webhooks \
  -F "id=delivered" \
  -F "url=https://ipa.insightpulseai.net/webhooks/mailgun/delivered"
```

### List Webhooks

```bash
curl --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/domains/mg.insightpulseai.net/webhooks
```

### Update Webhook

```bash
curl -X PUT --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/domains/mg.insightpulseai.net/webhooks/delivered \
  -F "url=https://ipa.insightpulseai.net/webhooks/mailgun/delivery-status"
```

### Delete Webhook

```bash
curl -X DELETE --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/domains/mg.insightpulseai.net/webhooks/delivered
```

---

## Testing Webhooks

### Test 1: Send Test Event (Mailgun Dashboard)

1. Go to: Webhooks → [Select Webhook] → "Test Webhook"
2. Mailgun sends sample POST to your URL
3. **Expected**: HTTP 200 OK response
4. Check n8n logs for received test data

### Test 2: Trigger Real Event

```bash
# Send test email via Mailgun API
curl -X POST --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/mg.insightpulseai.net/messages \
  -F "from=test@mg.insightpulseai.net" \
  -F "to=recipient@example.com" \
  -F "subject=Webhook Test" \
  -F "text=This email will trigger delivery webhook." \
  -F "o:tag=webhook-test"
```

**Expected Webhook Flow**:
1. `accepted` event (immediate)
2. `delivered` event (1-30 seconds later)
3. `opened` event (if recipient opens email + tracking enabled)

### Test 3: Verify Signature

```bash
# n8n logs should show signature verification passed
# If signature invalid, workflow will throw error
```

---

## Webhook Retry Logic (Mailgun Official)

**Behavior**: If webhook URL returns non-200 status code, Mailgun retries

**Retry Schedule**:
- 1 minute
- 5 minutes
- 15 minutes
- 30 minutes
- 1 hour
- 3 hours
- 6 hours
- 12 hours
- 24 hours

**Max Retries**: 9 attempts over ~48 hours

**Recommendation**: Ensure webhook endpoints are highly available (>99.9% uptime)

---

## Troubleshooting

### Webhook Not Receiving Events

**Symptom**: Events occur but webhook URL never receives POST requests

**Diagnosis**:
1. Check webhook URL is publicly accessible (not localhost/private IP)
2. Verify webhook is configured for correct domain
3. Check Mailgun logs for webhook delivery attempts
4. Test URL manually with cURL

**Fix**: Ensure webhook endpoint is running and accessible from internet

### Signature Verification Failing

**Symptom**: Webhook receives requests but signature doesn't match

**Diagnosis**:
1. Verify signing key is correct (copy from Mailgun dashboard)
2. Check timestamp + token concatenation order (`timestamp + token` not `token + timestamp`)
3. Ensure HMAC algorithm is SHA256 (not MD5/SHA1)
4. Verify no leading/trailing whitespace in signing key

**Fix**: Re-copy signing key from Mailgun dashboard, update environment variable

### Missing Event Data

**Symptom**: Webhook receives POST but event-data field is empty

**Diagnosis**:
1. Check Mailgun logs for event type
2. Verify webhook is configured for that event type
3. Check content-type header (should be `application/json`)

**Fix**: Ensure webhook URL accepts POST requests with JSON body

---

## Production Checklist

Before enabling webhooks in production:

1. ✅ Webhook URLs deployed and tested
2. ✅ Signature verification implemented and tested
3. ✅ Error handling and retry logic in place
4. ✅ Webhook signing key stored securely in environment
5. ✅ n8n workflows handle all required event types
6. ✅ Monitoring alerts configured for webhook failures
7. ✅ Test events trigger expected downstream actions
8. ✅ Logging configured for debugging and compliance

---

**Last Updated**: 2026-01-14
**Status**: Documentation ready (webhooks not yet configured)
**Primary Use Cases**: Email delivery tracking, bounce handling, engagement analytics
**Security**: HMAC-SHA256 signature verification required for all webhooks
