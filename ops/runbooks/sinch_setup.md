# Sinch SMS/OTP Setup Runbook

## Overview

This runbook covers the setup of Sinch as an SMS/OTP provider for Odoo.

---

## Prerequisites

- Sinch account with SMS API access
- Environment variables configured (NOT in repo):
  - `SINCH_SERVICE_PLAN_ID`
  - `SINCH_API_TOKEN`

---

## 1. Sinch Account Setup

### 1.1 Create Account

1. Sign up at [Sinch Dashboard](https://dashboard.sinch.com)
2. Complete phone verification
3. Select SMS API product

### 1.2 Get Credentials

1. Navigate to **APIs** > **REST Configuration**
2. Note your:
   - Service Plan ID
   - API Token
   - Region (us/eu)

---

## 2. Configure SMS Sending

### 2.1 Test API Access

```bash
curl -X POST \
  "https://us.sms.api.sinch.com/xms/v1/${SINCH_SERVICE_PLAN_ID}/batches" \
  -H "Authorization: Bearer ${SINCH_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "YOUR_SINCH_NUMBER",
    "to": ["+1234567890"],
    "body": "Test message from Sinch"
  }'
```

### 2.2 Response Codes

| Code | Meaning |
|------|---------|
| 201 | Message queued successfully |
| 400 | Invalid request (check payload) |
| 401 | Authentication failed |
| 403 | Insufficient permissions |

---

## 3. Odoo Integration

### 3.1 System Parameters

Set in Odoo via Settings > Technical > Parameters > System Parameters:

| Key | Value |
|-----|-------|
| `sinch.service_plan_id` | `${SINCH_SERVICE_PLAN_ID}` |
| `sinch.api_token` | `${SINCH_API_TOKEN}` |
| `sinch.region` | `us` or `eu` |
| `sinch.from_number` | Your Sinch phone number |

### 3.2 SMS Gateway Module

If using `ipai_sms_gateway`:

1. Install the module: `odoo -d odoo -i ipai_sms_gateway --stop-after-init`
2. Configure via Settings > SMS > Providers
3. Select Sinch as provider
4. Enter credentials

---

## 4. OTP Configuration

### 4.1 Enable Two-Factor Authentication

For Odoo 2FA with SMS:

1. Install `auth_totp_sms` if available
2. Configure SMS provider in settings
3. Users enable 2FA in their preferences

### 4.2 Custom OTP Flow

For custom OTP (e.g., password reset):

```python
# Example: Send OTP via Sinch
def send_otp(self, phone_number, otp_code):
    import requests

    url = f"https://us.sms.api.sinch.com/xms/v1/{SERVICE_PLAN_ID}/batches"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": FROM_NUMBER,
        "to": [phone_number],
        "body": f"Your verification code is: {otp_code}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 201
```

---

## 5. Verification Checklist

- [ ] Sinch account created and verified
- [ ] Service Plan ID obtained
- [ ] API Token obtained
- [ ] Test SMS sent successfully
- [ ] Odoo system parameters configured
- [ ] SMS gateway module installed (if applicable)
- [ ] OTP flow tested end-to-end

---

## 6. Rate Limits & Quotas

### 6.1 Default Limits

| Metric | Limit |
|--------|-------|
| Messages per second | 30 |
| Daily messages (trial) | 100 |
| Monthly messages (production) | Per plan |

### 6.2 Monitoring

Check usage in Sinch Dashboard:
- **Analytics** > **SMS** > **Overview**

---

## 7. Troubleshooting

### Messages Not Delivered

1. Check Sinch Dashboard > Logs
2. Verify phone number format (E.164: +1234567890)
3. Check carrier filtering (some carriers block shortcodes)

### Authentication Errors

1. Regenerate API token in Sinch Dashboard
2. Verify Service Plan ID is correct
3. Check region matches your account

### Rate Limiting

1. Implement exponential backoff
2. Request limit increase from Sinch support
3. Queue messages for async sending

---

## 8. Security Notes

- NEVER commit `SINCH_API_TOKEN` to repo
- Use environment variables or secrets manager
- Rotate API tokens periodically
- Implement rate limiting in your application
- Log all SMS sends for audit

---

*Last updated: 2026-01-08*
