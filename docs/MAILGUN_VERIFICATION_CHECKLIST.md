# Mailgun Setup Verification Checklist

## ✅ Completed Steps

### 1. DNS Records Added to DigitalOcean
- [x] SPF (TXT) - Authorization for Mailgun to send
- [x] DKIM (TXT) - Email signature verification
- [x] MX Records (2) - Incoming mail routing
- [x] CNAME - Click/open tracking
- [x] DMARC (TXT) - Authentication policy

**DNS Zone:** `mg.insightpulseai.net` on DigitalOcean
**Nameservers:**
- ns1.digitalocean.com
- ns2.digitalocean.com
- ns3.digitalocean.com

### 2. Odoo SMTP Configuration
- [x] Mail server created on production (178.128.112.214)
- [x] SMTP Host: smtp.mailgun.org
- [x] SMTP Port: 587
- [x] Username: postmaster@mg.insightpulseai.net
- [x] Encryption: STARTTLS
- [x] System parameters configured
- [x] Company email set

## ⏳ Pending Steps

### 3. ~~Delegate Subdomain to DigitalOcean~~ (SKIP - Using Parent Domain DNS)
**Status:** Using Google Domains DNS directly instead of delegation

**Current Setup:**
- All DNS records added directly to parent domain `insightpulseai.net`
- Records resolving correctly (verified via dig)
- No NS delegation needed since managing all records in one place

### 4. Add SMTP Password in Odoo
**Action Required:** Get password from Mailgun and add to Odoo

1. Go to Mailgun dashboard: https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net
2. Find SMTP credentials section
3. Copy the SMTP password
4. Go to Odoo: Settings → Technical → Outgoing Mail Servers
5. Edit "Mailgun SMTP - InsightPulse AI"
6. Paste password and save

### 5. ~~Verify DNS Propagation~~ ✅ COMPLETE
**Status:** All DNS records verified and propagating correctly

```bash
# ✅ SPF Record
dig TXT mg.insightpulseai.net +short
# Result: "v=spf1 include:mailgun.org ~all"

# ✅ DKIM Record
dig TXT pic._domainkey.mg.insightpulseai.net +short
# Result: "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB"

# ✅ MX Records
dig MX mg.insightpulseai.net +short
# Result: 10 mxb.mailgun.org.
#         10 mxa.mailgun.org.

# ✅ CNAME Tracking
dig CNAME email.mg.insightpulseai.net +short
# Result: mailgun.org.

# ✅ DMARC Record
dig TXT _dmarc.mg.insightpulseai.net +short
# Result: "Data: v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;"
```

**Verified:** 2026-01-13 18:00 UTC

### 6. Verify in Mailgun Dashboard
1. Go to: https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net/verify
2. All status indicators should be green
3. Domain should show as "Verified"

### 7. Send Test Email from Odoo
1. Go to Odoo: Settings → Technical → Outgoing Mail Servers
2. Click on "Mailgun SMTP - InsightPulse AI"
3. Click "Test Connection"
4. Send a test email to verify delivery

## 🎯 Success Criteria

- [x] ~~NS records delegating mg.insightpulseai.net to DigitalOcean~~ (Using parent domain DNS)
- [x] All DNS records verified (resolving correctly via dig)
- [ ] All DNS records verified (green in Mailgun dashboard)
- [ ] SMTP password added to Odoo
- [ ] Test email sent successfully
- [ ] Finance PPM BIR notifications working

## 📋 Finance PPM Email Features

Once email is working, these features will be active:

1. **BIR Deadline Alerts** - 7 days before deadline
2. **Task Escalation** - 3 days before deadline if not completed
3. **Monthly Compliance Summary** - End of month report
4. **Prep/Review/Approval Notifications** - Workflow reminders

All emails sent as: noreply@mg.insightpulseai.net

---
*Last updated: 2026-01-13*
*Status: DNS configured, awaiting NS delegation*
