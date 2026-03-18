# DigitalOcean SMTP Unblock Request

**Date**: December 30, 2025
**Droplet IP**: 159.223.75.148
**Droplet Name**: odoo-erp-prod
**Region**: SGP1 (Singapore)

---

## Support Ticket Request

**Subject**: Request to unblock outbound SMTP port 587 for droplet 159.223.75.148

**Message**:

```
Hello DigitalOcean Support,

I am requesting access to outbound SMTP port 587 for my droplet at 159.223.75.148 (odoo-erp-prod).

**Use Case**: Internal business notifications from Odoo CE 18 ERP system
- NOT for mass email marketing
- NOT for bulk commercial emails
- ONLY for internal notifications: task assignments, approvals, alerts

**Current Status**:
- Droplet can reach internet (verified: curl https://google.com works)
- SMTP ports 587, 465, 2525 are BLOCKED (verified: timeout on all ports)
- This prevents our internal Odoo ERP from sending notifications to employees

**Business Justification**:
We run a multi-company Finance Shared Services Center using Odoo CE 18. Email notifications are critical for:
1. BIR tax filing deadline alerts (regulatory compliance - Philippines)
2. Multi-employee task assignments
3. Manager approvals for expenses and invoices
4. Month-end closing process notifications

**Expected Volume**: <50 emails/day (internal team notifications only)

**SMTP Configuration**:
- Primary Provider: Zoho Workplace (smtppro.zoho.com) - Business email
- Backup Provider: Gmail (smtp.gmail.com) - Personal fallback
- Ports Required: 465 (SSL/TLS) and 587 (STARTTLS)
- Authentication: Password-based (no open relay)
- Purpose: Internal notifications only

**Security Measures**:
- Using Gmail App Password (not regular password)
- UFW firewall active on droplet
- Emails limited to authenticated internal users
- No public signup or mass mailing features

Please unblock outbound SMTP port 587 for this droplet.

Thank you,
Jake Tolentino
Finance SSC Manager
InsightPulse AI
```

---

## Alternative: Submit via DigitalOcean Portal

1. Go to: https://cloud.digitalocean.com/support/tickets
2. Click "Create Ticket"
3. Select **Droplet** category
4. Copy/paste the message above
5. Attach this document as reference

---

## Expected Timeline

- **Response**: 2-4 hours
- **Resolution**: 24-48 hours
- **Alternative**: Use SendGrid if DigitalOcean declines

---

## Verification After Unblocking

Test SMTP connectivity:

```bash
# SSH into droplet
ssh root@159.223.75.148

# Test Zoho SMTP (port 465)
timeout 5 bash -c '</dev/tcp/smtppro.zoho.com/465' && echo '✅ Zoho port 465 OPEN' || echo '❌ BLOCKED'

# Test Gmail SMTP (port 587)
timeout 5 bash -c '</dev/tcp/smtp.gmail.com/587' && echo '✅ Gmail port 587 OPEN' || echo '❌ BLOCKED'

# Test from Odoo container
docker exec odoo-core python3 -c 'import socket; socket.create_connection(("smtppro.zoho.com", 465), timeout=5); print("✅ Zoho SMTP reachable")'
```

If both tests show ✅, then go to Odoo UI:
- Settings → Technical → Outgoing Mail Servers
- Click "Zoho SMTP - InsightPulse"
- Enter your Zoho password in the Password field
- Save
- Click **Test Connection**
- Should show: "Connection Test Succeeded! Everything seems properly set up!"

---

## Backup Plan: SendGrid (If DigitalOcean Denies)

If DigitalOcean denies the request, use SendGrid SMTP Relay:

1. Sign up: https://signup.sendgrid.com (free 100 emails/day)
2. Create API Key: Settings → API Keys → Create API Key (Full Access)
3. Update Odoo SMTP:
   - Server: `smtp.sendgrid.net`
   - Port: `587`
   - Username: `apikey` (literal string)
   - Password: `[YOUR_SENDGRID_API_KEY]`
   - Encryption: TLS (STARTTLS)

SendGrid is NOT blocked by DigitalOcean and will work immediately.

---

## Current Configuration Status

✅ **Odoo SMTP Configured**:
- **Primary**: Zoho Workplace (business@insightpulseai.com)
  - Server: smtppro.zoho.com:465 (SSL/TLS)
  - Configuration ID: 3 (on odoo-core container)
  - Password: ⚠️ **Must be set in Odoo UI**

- **Backup**: Gmail (jgtolentino.rn@gmail.com) - Removed, replaced with Zoho

❌ **Network Status**: DigitalOcean blocks outbound SMTP ports 465, 587, 2525 (verified)

⏳ **Waiting For**: DigitalOcean support to unblock ports 465 and 587

---

**Last Updated**: 2025-12-30 00:55 UTC
