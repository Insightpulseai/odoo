# TBWA\SMP Mailgun Canonical Configuration

**Domain**: `mg.insightpulseai.com`
**Primary Use**: Odoo CE 18.0 transactional email (expense approvals, alerts, notifications)
**Region**: US (api.mailgun.net)
**DNS Provider**: DigitalOcean (erp.insightpulseai.com domain)

---

## Official Requirements (Mailgun Documentation)

**Source**: https://documentation.mailgun.com/docs/mailgun/quickstart-sending/verifying-your-domain/

### DNS Records (Verification + Sending)

Mailgun requires 4 DNS records for full domain verification and email sending:

1. **SPF Record** (TXT) - Sender Policy Framework authorization
2. **DKIM Records** (2× TXT) - DomainKeys Identified Mail signatures
3. **MX Records** (2× MX) - Inbound email routing (optional for sending-only)

---

## Canonical DNS Records (TBWA\SMP)

**Applied to**: `erp.insightpulseai.com` zone in DigitalOcean DNS

### 1. SPF Record (Required for Sending)

| Type | Host | Value | TTL |
|------|------|-------|-----|
| TXT | `mg.insightpulseai.com` | `v=spf1 include:mailgun.org ~all` | 3600 |

**Purpose**: Authorizes Mailgun's servers to send email on behalf of `mg.insightpulseai.com`

**Verification Command**:
```bash
dig TXT mg.insightpulseai.com +short | grep "v=spf1"
# Expected: "v=spf1 include:mailgun.org ~all"
```

### 2. DKIM Records (Required for Sending)

#### DKIM Signature #1
| Type | Host | Value | TTL |
|------|------|-------|-----|
| TXT | `mailo._domainkey.mg.insightpulseai.com` | `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDYi+WQoP6DEtjZIwC02BRwLKco3WnjQzXBmCr7pT4nMBLEk/WcLjTCE3PRBvNqtSyXzXdZKl65p4VvsmXFGJvGb4qBEQdXLBRZxLJMqfMWjpHqXK7bRxjsKvZCa1thgPyFoaDq+FfX6EcLlAjxLNNjpUE3KcIjmh6mH7HfEeGhIQIDAQAB` | 3600 |

**Verification Command**:
```bash
dig TXT mailo._domainkey.mg.insightpulseai.com +short
# Expected: "k=rsa; p=MIGfMA0G..."
```

#### DKIM Signature #2
| Type | Host | Value | TTL |
|------|------|-------|-----|
| TXT | `mx._domainkey.mg.insightpulseai.com` | `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDXPPiPYQ5/96/UphEq3GhXR7RoB3vxm3KjDqHHCHTjV2FojKqZuCKkLMJzOPkz/4yV8k1xUB8VQp8R5z2L6TGhkEWVGCJzXJKXOTZqMYLh3vLVzIGPzhLjCMUMQKYvM7lINKOp8BZkRdqP0S1hTHzI6PG6MQMv5xJd+Qd8pD9xwQIDAQAB` | 3600 |

**Verification Command**:
```bash
dig TXT mx._domainkey.mg.insightpulseai.com +short
# Expected: "k=rsa; p=MIGfMA0G..."
```

### 3. MX Records (Optional - Only for Inbound Email)

**Decision**: Not configuring MX records for `mg.insightpulseai.com`

**Rationale**:
- Odoo CE 18.0 ONLY sends transactional emails (expense approvals, alerts)
- Odoo does NOT need to receive emails at `mg.insightpulseai.com`
- Inbound email routing (if needed) should use primary domain `erp.insightpulseai.com`
- Mailgun MX records are only required if using Mailgun Routes for inbound processing

**If inbound email is required later**:
| Type | Host | Value | Priority | TTL |
|------|------|-------|----------|-----|
| MX | `mg.insightpulseai.com` | `mxa.mailgun.org` | 10 | 3600 |
| MX | `mg.insightpulseai.com` | `mxb.mailgun.org` | 10 | 3600 |

---

## DNS Propagation Verification

### Check All Records
```bash
# SPF
dig TXT mg.insightpulseai.com +short | grep "v=spf1"

# DKIM #1
dig TXT mailo._domainkey.mg.insightpulseai.com +short

# DKIM #2
dig TXT mx._domainkey.mg.insightpulseai.com +short

# MX (if configured)
dig MX mg.insightpulseai.com +short
```

### Automated Verification (Mailgun API)
```bash
export MAILGUN_API_KEY="your-private-api-key"
export MAILGUN_DOMAIN="mg.insightpulseai.com"
export MAILGUN_REGION="us"

./scripts/mailgun/verify_domain.sh
```

**Expected Output**:
```
Domain Status:
  Domain: mg.insightpulseai.com
  State: active
  Created: 2026-01-14

Receiving DNS Records (MX):
  ❌ MX mg.insightpulseai.com
     Value: mxa.mailgun.org (priority: 10)

Sending DNS Records (SPF/DKIM):
  ✅ TXT mg.insightpulseai.com
     Value: v=spf1 include:mailgun.org ~all
  ✅ TXT mailo._domainkey.mg.insightpulseai.com
     Value: k=rsa; p=MIGfMA0G...
  ✅ TXT mx._domainkey.mg.insightpulseai.com
     Value: k=rsa; p=MIGfMA0G...
```

---

## Mailgun API Configuration

### API Endpoints (US Region)
- **Base URL**: `https://api.mailgun.net/v3`
- **Sending**: `POST /v3/mg.insightpulseai.com/messages`
- **Domain Verification**: `GET /v3/domains/mg.insightpulseai.com`

### Authentication
- **Method**: HTTP Basic Auth
- **Username**: `api`
- **Password**: `{MAILGUN_API_KEY}` (private API key from Mailgun dashboard)

### Rate Limits (Official)
- **Free Plan**: 5,000 emails/month
- **Foundation Plan**: Starting at 100 emails/month (pay-as-you-go)
- **Rate Limit**: 1,000 emails/hour (default)

---

## Security & Best Practices

### API Key Management
- **Storage**: `~/.zshrc` or environment variables only
- **Never Commit**: API keys must never be in version control
- **Rotation**: Rotate keys quarterly
- **Validation**: Test authentication before deployment

```bash
# Validate API key
curl -s --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/domains/mg.insightpulseai.com | jq '.domain.state'
# Expected: "active"
```

### SPF Record Security
- **Syntax**: `v=spf1 include:mailgun.org ~all`
- **~all (softfail)**: Recommended for initial deployment
- **-all (hardfail)**: Use after verification period (strict rejection)

### DKIM Key Rotation
- Mailgun manages DKIM key rotation automatically
- No manual intervention required
- Keys are 1024-bit RSA minimum (Mailgun standard)

---

## Troubleshooting

### DNS Records Not Verified
**Symptom**: Mailgun dashboard shows "Unverified" status

**Fixes**:
1. **Propagation delay**: Wait 15-60 minutes after DNS changes
2. **Check exact values**: Copy-paste from Mailgun dashboard to avoid typos
3. **Verify TTL**: Use 3600 seconds (1 hour) minimum
4. **Check host syntax**: `mg.insightpulseai.com` vs `mg` (depends on DNS provider)

```bash
# Force Mailgun re-verification
curl -X PUT --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/domains/mg.insightpulseai.com/verify
```

### Emails Marked as Spam
**Root Causes**:
1. SPF/DKIM not verified
2. Missing DMARC policy
3. No reverse DNS (PTR) record for sending IP
4. Low sender reputation (new domain)

**Solutions**:
1. Ensure all DNS records verified (✅ green in Mailgun dashboard)
2. Add DMARC record (optional but recommended):
   ```
   _dmarc.mg.insightpulseai.com TXT "v=DMARC1; p=none; rua=mailto:dmarc@insightpulseai.com"
   ```
3. Wait for sender reputation to build (send gradually)
4. Enable tracking (opens/clicks) for engagement metrics

### API Authentication Failures
**Symptom**: `401 Unauthorized` or `Forbidden`

**Fixes**:
1. Verify API key is correct (check Mailgun dashboard)
2. Ensure `api:` prefix in Basic Auth username
3. Check region endpoint (US vs EU)
4. Verify domain is verified in Mailgun dashboard

---

## Acceptance Gates

**Before marking Mailgun configuration as "done"**:

1. ✅ All 3 DNS records verified in Mailgun dashboard (SPF + 2× DKIM)
2. ✅ `./scripts/mailgun/verify_domain.sh` shows ✅ for all sending records
3. ✅ Domain state = `active` (not `unverified`)
4. ✅ Odoo SMTP test email delivers successfully (see ODOO_SMTP_SETUP.md)
5. ✅ Test email passes SPF/DKIM checks (use mail-tester.com or similar)
6. ✅ No spam classification on test emails to Gmail/Outlook

---

**Last Updated**: 2026-01-14
**Applies To**: Production Odoo CE 18.0 (`erp.insightpulseai.com`)
**Mailgun Domain**: `mg.insightpulseai.com` (US region)
**DNS Zone**: `erp.insightpulseai.com` (DigitalOcean)
