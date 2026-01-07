# Sinch SMS/Verification Provider Setup Runbook

**Purpose:** Configure Sinch as the SMS and verification provider for IPAI applications.

**Prerequisites:**
- Sinch account with API access
- Production phone numbers (if needed)
- Odoo instance configured

---

## 1. Overview

Sinch provides:
- SMS messaging (transactional, OTP)
- Voice verification
- Number verification
- WhatsApp Business messaging (optional)

**Reference:** [Sinch Developer Documentation](https://developers.sinch.com/)

---

## 2. Account Setup

### Step 1: Create Sinch Account

1. Go to [Sinch Dashboard](https://dashboard.sinch.com/)
2. Sign up for an account
3. Verify your email and phone number

### Step 2: Create an Application

1. Navigate to **Apps** in the dashboard
2. Click **Create App**
3. Enter app name (e.g., `ipai-production`)
4. Select capabilities:
   - SMS
   - Verification (if needed)
5. Note the **App Key** and **App Secret**

### Step 3: Configure Phone Numbers

1. Go to **Numbers** → **Your Numbers**
2. Rent or port phone numbers for your region
3. Assign numbers to your application

---

## 3. API Credentials

### Environment Variables

Set these in the Odoo container:

```bash
SINCH_APP_KEY=your-app-key
SINCH_APP_SECRET=your-app-secret
SINCH_PROJECT_ID=your-project-id
SINCH_REGION=us  # or eu, au
SINCH_FROM_NUMBER=+1234567890  # Your Sinch number
```

### Credential Storage

Store credentials securely:
- Use environment variables (recommended)
- Or Odoo system parameters with encryption
- Never hardcode in source

---

## 4. API Reference

### Send SMS

```bash
# Using curl
curl -X POST "https://sms.api.sinch.com/xms/v1/${PROJECT_ID}/batches" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+1234567890",
    "to": ["+0987654321"],
    "body": "Your verification code is: 123456"
  }'
```

### Verification

```bash
# Start verification
curl -X POST "https://verification.api.sinch.com/verification/v1/verifications" \
  -u "${APP_KEY}:${APP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "identity": {
      "type": "number",
      "endpoint": "+1234567890"
    },
    "method": "sms"
  }'

# Report verification result
curl -X PUT "https://verification.api.sinch.com/verification/v1/verifications/number/+1234567890" \
  -u "${APP_KEY}:${APP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "sms",
    "sms": {
      "code": "123456"
    }
  }'
```

---

## 5. Odoo Integration

### Module: `ipai_messaging_gateway`

Abstract messaging provider with Sinch implementation.

**Configuration (System Parameters):**

| Key | Value |
|-----|-------|
| `ipai_messaging.sms_provider` | `sinch` |
| `ipai_messaging.sinch_app_key` | (from env) |
| `ipai_messaging.sinch_app_secret` | (encrypted) |
| `ipai_messaging.sinch_project_id` | (from env) |
| `ipai_messaging.sinch_from_number` | `+1234567890` |

### Python Integration

```python
import requests
import os

class SinchSmsProvider:
    """Sinch SMS provider implementation."""

    def __init__(self):
        self.project_id = os.getenv("SINCH_PROJECT_ID")
        self.app_key = os.getenv("SINCH_APP_KEY")
        self.app_secret = os.getenv("SINCH_APP_SECRET")
        self.from_number = os.getenv("SINCH_FROM_NUMBER")
        self.base_url = "https://sms.api.sinch.com/xms/v1"

    def send_sms(self, to_number, message):
        """Send SMS via Sinch."""
        url = f"{self.base_url}/{self.project_id}/batches"

        response = requests.post(
            url,
            auth=(self.app_key, self.app_secret),
            json={
                "from": self.from_number,
                "to": [to_number],
                "body": message,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
```

---

## 6. Webhooks

### Configure Callback URL

1. In Sinch Dashboard, go to **Apps** → Your App → **Callbacks**
2. Set callback URL: `https://your-domain.com/ipai/sinch/webhook`
3. Select events:
   - Message delivery reports
   - Inbound messages (if needed)
   - Verification events

### Webhook Handler

```python
from odoo import http
from odoo.http import request

class SinchWebhookController(http.Controller):

    @http.route("/ipai/sinch/webhook", type="json", auth="none", methods=["POST"], csrf=False)
    def sinch_webhook(self, **kwargs):
        """Handle Sinch webhook callbacks."""
        payload = request.jsonrequest

        event_type = payload.get("type")

        if event_type == "delivery_report":
            # Handle delivery report
            pass
        elif event_type == "inbound":
            # Handle inbound message
            pass
        elif event_type == "verification":
            # Handle verification event
            pass

        return {"status": "ok"}
```

---

## 7. Testing

### Sandbox Mode

Use Sinch sandbox for testing:
- No real messages sent
- Free for development
- Configure in app settings

### Test Commands

```bash
# Check credentials
curl -X GET "https://sms.api.sinch.com/xms/v1/${PROJECT_ID}/inbounds" \
  -u "${APP_KEY}:${APP_SECRET}"

# Send test SMS (production)
curl -X POST "https://sms.api.sinch.com/xms/v1/${PROJECT_ID}/batches" \
  -u "${APP_KEY}:${APP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "${FROM_NUMBER}",
    "to": ["${TEST_NUMBER}"],
    "body": "Test message from IPAI"
  }'
```

### Verify in Odoo

```python
# From Odoo shell
provider = env['ipai.messaging.gateway'].get_provider('sinch')
result = provider.send_sms('+1234567890', 'Test from Odoo')
print(result)
```

---

## 8. Monitoring

### Key Metrics

| Metric | Description | Alert |
|--------|-------------|-------|
| SMS delivery rate | % delivered | < 95% |
| SMS latency | Time to deliver | > 30s |
| API errors | Error count | > 10/hour |
| Cost | Monthly spend | Budget threshold |

### Dashboard

Access Sinch Dashboard for:
- Message logs
- Delivery statistics
- Cost tracking
- Error analysis

---

## 9. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid credentials | Verify app key/secret |
| 403 Forbidden | Missing permissions | Check app capabilities |
| Number not valid | Invalid format | Use E.164 format (+1234567890) |
| Message not delivered | Carrier issues | Check delivery reports |

### Debug Commands

```bash
# Check message status
curl -X GET "https://sms.api.sinch.com/xms/v1/${PROJECT_ID}/batches/${BATCH_ID}" \
  -u "${APP_KEY}:${APP_SECRET}"

# List recent messages
curl -X GET "https://sms.api.sinch.com/xms/v1/${PROJECT_ID}/batches?page_size=10" \
  -u "${APP_KEY}:${APP_SECRET}"
```

---

## 10. Checklist

### Setup

- [ ] Sinch account created
- [ ] Application created with SMS capability
- [ ] Phone number(s) provisioned
- [ ] Credentials stored securely
- [ ] Webhook URL configured

### Integration

- [ ] Environment variables set
- [ ] Odoo messaging gateway configured
- [ ] Test SMS sent successfully
- [ ] Delivery reports received

### Production

- [ ] Sandbox disabled
- [ ] Production phone numbers active
- [ ] Monitoring configured
- [ ] Cost alerts set

---

*Last updated: 2026-01-08*
