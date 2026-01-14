# Mailgun Inbound Email Routes

**Purpose**: Configure Mailgun Routes for processing inbound emails (optional feature)

**Status**: Not currently configured (Odoo sending-only)

**When to use**: If TBWA\SMP needs to receive emails at `@mg.insightpulseai.net` and process them automatically

---

## Official Mailgun Routes Documentation

**Source**: https://documentation.mailgun.com/docs/mailgun/user-manual/get-started/#routes

Mailgun Routes allow you to:
- Forward inbound emails to webhooks
- Store emails for retrieval via API
- Forward to external email addresses
- Stop/drop unwanted emails

---

## Route Expressions (Official Syntax)

### Match Types

| Expression | Description | Example |
|------------|-------------|---------|
| `match_recipient(".*")` | Match all recipients | Catch-all route |
| `match_recipient("support@.*")` | Match specific mailbox | `support@mg.insightpulseai.net` |
| `match_recipient(".*@mg.insightpulseai.net")` | Match domain | All `@mg.insightpulseai.net` emails |
| `match_header("subject", ".*urgent.*")` | Match subject line | Emails with "urgent" in subject |
| `match_header("from", ".*@example.com")` | Match sender domain | Emails from `@example.com` |

### Logical Operators

```python
# AND operator
match_recipient("support@.*") and match_header("subject", ".*bug.*")

# OR operator
match_recipient("support@.*") or match_recipient("help@.*")

# NOT operator
not match_recipient("spam@.*")
```

---

## Route Actions (Official)

### 1. Forward to Webhook (Most Common for Odoo Integration)

**Syntax**:
```python
forward("https://your-server.com/webhooks/mailgun")
```

**Use Case**: Parse emails in n8n/Odoo for ticket creation, expense receipt processing

**Webhook Payload** (JSON):
```json
{
  "From": "sender@example.com",
  "To": "support@mg.insightpulseai.net",
  "Subject": "Expense Receipt - Invoice #12345",
  "body-plain": "Email body text...",
  "body-html": "<html>Email HTML...</html>",
  "attachment-count": 1,
  "attachments": [...]
}
```

### 2. Store and Forward

**Syntax**:
```python
store(notify="https://your-server.com/notify")
```

**Use Case**: Store email for later retrieval + send notification to webhook

**Storage Duration**: 3 days (free plan), 30 days (paid plans)

### 3. Forward to Email

**Syntax**:
```python
forward("recipient@example.com")
```

**Use Case**: Route emails to specific team members

### 4. Stop (Drop Email)

**Syntax**:
```python
stop()
```

**Use Case**: Block spam or unwanted senders

---

## Example Routes for TBWA\SMP (Future Use)

### Route 1: Expense Receipt Processing

**Expression**:
```python
match_recipient("expenses@mg.insightpulseai.net") and match_header("subject", ".*receipt.*")
```

**Action**:
```python
forward("https://ipa.insightpulseai.net/webhooks/mailgun/expense-receipt")
```

**Purpose**: Forward expense receipts to n8n for OCR processing

**n8n Workflow**:
1. Receive email via webhook
2. Extract attachments (PDF/images)
3. Send to OCR service (PaddleOCR-VL)
4. Create Odoo expense with OCR data
5. Notify submitter via Mattermost

### Route 2: Support Ticket Creation

**Expression**:
```python
match_recipient("support@mg.insightpulseai.net")
```

**Action**:
```python
forward("https://ipa.insightpulseai.net/webhooks/mailgun/support-ticket")
```

**Purpose**: Convert support emails to Odoo helpdesk tickets

### Route 3: Finance Team Forwarding

**Expression**:
```python
match_recipient("finance@mg.insightpulseai.net")
```

**Action**:
```python
forward("jake.tolentino@insightpulseai.com")
```

**Purpose**: Route finance emails to Jake's primary inbox

### Route 4: Catch-All (Low Priority)

**Expression**:
```python
match_recipient(".*@mg.insightpulseai.net")
```

**Priority**: `0` (lowest)

**Action**:
```python
store(notify="https://ipa.insightpulseai.net/webhooks/mailgun/catchall")
```

**Purpose**: Store unmatched emails for manual review

---

## Creating Routes via Mailgun Dashboard

### Step 1: Navigate to Routes

1. Go to: https://app.mailgun.com/mg/routes
2. Click **"Create Route"**

### Step 2: Configure Route

| Field | Value |
|-------|-------|
| **Expression Type** | `Match Recipient` |
| **Recipient** | `expenses@mg.insightpulseai.net` |
| **Actions** | `Forward` |
| **Destination** | `https://ipa.insightpulseai.net/webhooks/mailgun/expense-receipt` |
| **Priority** | `10` (higher = processed first) |
| **Description** | `Expense Receipt Processing` |

### Step 3: Save and Test

1. Click **"Create Route"**
2. Send test email to `expenses@mg.insightpulseai.net`
3. Check webhook logs in n8n
4. Verify email data received

---

## Creating Routes via Mailgun API

### Create Route (cURL)

```bash
curl -X POST --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/routes \
  -F "priority=10" \
  -F "description=Expense Receipt Processing" \
  -F "expression=match_recipient('expenses@mg.insightpulseai.net')" \
  -F "action=forward('https://ipa.insightpulseai.net/webhooks/mailgun/expense-receipt')"
```

### List Routes

```bash
curl --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/routes
```

### Delete Route

```bash
curl -X DELETE --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/routes/{ROUTE_ID}
```

---

## Route Priority

**Processing Order**: Higher priority number = processed first

| Priority | Use Case |
|----------|----------|
| `100` | Critical routes (urgent tickets, high-priority mailboxes) |
| `50` | Standard routes (normal ticket processing) |
| `10` | Low-priority routes (forwarding, notifications) |
| `0` | Catch-all routes (unmatched emails) |

**Rule**: At most one route action executes per email (first match wins)

---

## Webhook Security

### Verify Mailgun Signatures

**Purpose**: Ensure webhook requests are from Mailgun (not spoofed)

**Official Documentation**: https://documentation.mailgun.com/docs/mailgun/user-manual/webhooks/#securing-webhooks

**Verification Algorithm** (Python):
```python
import hmac
import hashlib

def verify_mailgun_signature(token, timestamp, signature):
    """
    Verify Mailgun webhook signature
    Args:
        token: From 'token' field in webhook payload
        timestamp: From 'timestamp' field
        signature: From 'signature' field
    """
    signing_key = os.environ['MAILGUN_WEBHOOK_SIGNING_KEY']
    hmac_digest = hmac.new(
        key=signing_key.encode(),
        msg=f'{timestamp}{token}'.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, hmac_digest)
```

**n8n Implementation**:
```javascript
// n8n Webhook node → Function node
const token = $json.token;
const timestamp = $json.timestamp;
const signature = $json.signature;

const crypto = require('crypto');
const signingKey = $env('MAILGUN_WEBHOOK_SIGNING_KEY');

const hmacDigest = crypto
  .createHmac('sha256', signingKey)
  .update(`${timestamp}${token}`)
  .digest('hex');

if (signature !== hmacDigest) {
  throw new Error('Invalid Mailgun signature');
}

return $json; // Continue processing
```

---

## Testing Routes

### Test 1: Send Email Manually

```bash
# Send test email via Mailgun API
curl -X POST --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/mg.insightpulseai.net/messages \
  -F "from=test@mg.insightpulseai.net" \
  -F "to=expenses@mg.insightpulseai.net" \
  -F "subject=Test Expense Receipt" \
  -F "text=This is a test email to verify route processing."
```

### Test 2: Check Mailgun Logs

1. Go to: https://app.mailgun.com/mg/logs
2. Filter by recipient: `expenses@mg.insightpulseai.net`
3. **Expected**: Event shows "accepted" + "route matched"
4. Click event → View "Routes" tab → Verify correct route applied

### Test 3: Verify Webhook Delivery

1. Check n8n execution logs
2. **Expected**: Webhook received with email data
3. Verify attachment processing (if applicable)
4. Confirm downstream action triggered (Odoo expense creation, etc.)

---

## Troubleshooting

### Route Not Matching

**Symptom**: Email delivered but route action doesn't execute

**Diagnosis**:
1. Check route expression syntax (case-sensitive, regex must match exactly)
2. Verify priority order (higher priority routes may intercept)
3. Check Mailgun logs for "route matched" event

**Fix**: Update expression or adjust priority

### Webhook Not Receiving Data

**Symptom**: Route matches but webhook URL returns 404/500

**Diagnosis**:
1. Verify webhook URL is publicly accessible (not localhost)
2. Check n8n/Odoo logs for errors
3. Test webhook URL manually with cURL

**Fix**: Ensure webhook endpoint is running and accessible

### Attachments Not Processed

**Symptom**: Webhook receives email but attachments missing

**Diagnosis**:
1. Check `attachment-count` field in webhook payload
2. Verify attachments are within size limit (25MB per Mailgun)
3. Check content-type headers

**Fix**: Use `store()` action to retrieve large attachments via API

---

## Production Checklist (When Enabling Inbound)

Before enabling inbound email routes:

1. ✅ MX records configured and verified
2. ✅ Webhook endpoints deployed and tested
3. ✅ Webhook signature verification implemented
4. ✅ Route expressions tested with sample emails
5. ✅ n8n workflows handle email parsing correctly
6. ✅ Odoo integration creates records as expected
7. ✅ Error handling and retry logic in place
8. ✅ Monitoring alerts configured for webhook failures

---

**Last Updated**: 2026-01-14
**Status**: Documentation only (routes not yet configured)
**When Needed**: If TBWA\SMP requires inbound email processing
**Primary Use Case**: Expense receipt OCR automation via n8n
