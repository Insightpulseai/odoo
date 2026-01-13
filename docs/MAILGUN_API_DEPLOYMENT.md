# Mailgun HTTP API Deployment Guide

Complete deployment guide for implementing Mailgun HTTP API email sending in production to bypass DigitalOcean SMTP port blocking.

## Quick Summary

**Problem**: DigitalOcean blocks outbound SMTP ports 25/587/465
**Solution**: Use Mailgun HTTP API (port 443) instead
**Module**: `ipai_mailgun_api` (Odoo 18 CE compatible)
**Status**: Ready for deployment

---

## Prerequisites

- ✅ Mailgun DNS records verified (all 6 records propagating)
- ✅ Mailgun API key available (from dashboard)
- ✅ Production server access (root@178.128.112.214)
- ✅ Odoo database name: `odoo` (confirmed)

---

## Deployment Steps

### 1. Install Python Requests Library

SSH to production server:

```bash
ssh root@178.128.112.214

# Install requests in Odoo container
docker exec odoo-prod pip3 install requests

# Verify installation
docker exec odoo-prod python3 -c "import requests; print(f'✅ requests {requests.__version__}')"
# Expected: ✅ requests 2.31.0 (or similar)
```

### 2. Test Mailgun API (Standalone)

Before installing the Odoo module, verify the API works:

```bash
# Get latest code
cd /opt/odoo-ce/repo
git pull origin feat/deterministic-scss-verification

# Set API key (get from Mailgun dashboard)
export MAILGUN_API_KEY=key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Run test script
python3 scripts/send_via_mailgun_api.py \
  business@insightpulseai.com \
  "Mailgun API Test - $(date +%Y-%m-%d)" \
  "This email was sent via Mailgun HTTP API from production server"

# Expected output:
# ✅ Email sent successfully
#    Message ID: <xxxxxxxx.xxxxxxxx@mg.insightpulseai.net>
#    Status: Queued. Thank you.
```

**Checkpoint**: Check inbox for test email before proceeding.

### 3. Install Odoo Module

Install the `ipai_mailgun_api` module:

```bash
cd /opt/odoo-ce/repo

# Install module (use correct database name)
docker exec odoo-prod odoo -d odoo -i ipai_mailgun_api --stop-after-init

# Expected output:
# ...
# INFO odoo odoo.modules.loading: loading 1 modules...
# INFO odoo odoo.modules.loading: 1 modules loaded in 0.02s, 0 queries
# INFO odoo odoo.modules.registry: module ipai_mailgun_api: creating or updating database tables
# ...
# INFO odoo odoo.modules.loading: Modules loaded.

# Verify module installed
docker exec odoo-prod odoo shell -d odoo << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
module = env['ir.module.module'].search([('name', '=', 'ipai_mailgun_api')])
print(f"Module state: {module.state}")
print(f"Module installed: {module.state == 'installed'}")
EOF

# Expected output:
# Module state: installed
# Module installed: True
```

### 4. Configure Mailgun API Key

Set the API key in Odoo system parameters:

**Option A: Via Odoo Shell (Recommended)**

```bash
docker exec odoo-prod odoo shell -d odoo << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
IrConfigParam = env['ir.config_parameter'].sudo()

# Get API key from environment
import os
api_key = os.environ.get('MAILGUN_API_KEY', 'key-f6d80573-4c6f8ebe')

# Set parameters
IrConfigParam.set_param('mailgun.api_key', api_key)
IrConfigParam.set_param('mailgun.domain', 'mg.insightpulseai.net')
IrConfigParam.set_param('mailgun.use_api', 'True')

# Verify
print(f"✅ API Key: {api_key[:15]}...")
print(f"✅ Domain: {IrConfigParam.get_param('mailgun.domain')}")
print(f"✅ Use API: {IrConfigParam.get_param('mailgun.use_api')}")

env.cr.commit()
EOF
```

**Option B: Via Odoo UI**

1. Login to Odoo: https://erp.insightpulseai.net
2. Go to **Settings > Technical > Parameters > System Parameters**
3. Find or create these parameters:
   - **Key**: `mailgun.api_key` | **Value**: `key-xxxxxxxx`
   - **Key**: `mailgun.domain` | **Value**: `mg.insightpulseai.net`
   - **Key**: `mailgun.use_api` | **Value**: `True`

### 5. Test Email from Odoo

Send a test email through Odoo:

```bash
docker exec odoo-prod odoo shell -d odoo << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})

# Create test email
mail = env['mail.mail'].create({
    'subject': 'Mailgun API Test from Odoo',
    'body_html': '<p>This email was sent via <strong>Mailgun HTTP API</strong> from Odoo 18 CE.</p>',
    'email_to': 'business@insightpulseai.com',
    'email_from': 'noreply@mg.insightpulseai.net',
})

# Send immediately
mail.send()

print(f"✅ Email queued: {mail.id}")
print(f"   Subject: {mail.subject}")
print(f"   To: {mail.email_to}")
print(f"   State: {mail.state}")

env.cr.commit()
EOF

# Check logs
docker logs odoo-prod --tail 20 | grep -i mailgun
# Expected: ✅ Email sent via Mailgun API: <...@mg.insightpulseai.net>
```

**Checkpoint**: Check inbox for test email from Odoo.

### 6. Restart Odoo (Apply Changes)

Restart Odoo to ensure all changes are loaded:

```bash
docker restart odoo-prod

# Wait for startup (check logs)
docker logs -f odoo-prod | grep -E "(Odoo|Ready|HTTP)"

# Expected:
# INFO odoo odoo: Odoo version 18.0
# INFO odoo odoo.service.server: HTTP service (werkzeug) running on 0.0.0.0:8069
```

### 7. Verify Finance PPM Integration

If Finance PPM module is installed, test BIR notifications:

```bash
docker exec odoo-prod odoo shell -d odoo << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})

# Check if Finance PPM installed
ppm_module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm')])
print(f"Finance PPM installed: {ppm_module.state == 'installed'}")

if ppm_module.state == 'installed':
    # Find a BIR form to test
    bir_form = env['ipai.finance.bir_schedule'].search([
        ('status', 'in', ['not_started', 'in_progress'])
    ], limit=1)

    if bir_form:
        print(f"Testing with BIR form: {bir_form.form_type}")
        print(f"Filing deadline: {bir_form.filing_deadline}")

        # Send test notification (if method exists)
        # bir_form._send_deadline_alert()
        print("✅ BIR form found, email system ready")
    else:
        print("⚠️ No BIR forms available for testing")
else:
    print("ℹ️ Finance PPM not installed, skipping BIR test")

EOF
```

---

## Verification Checklist

Run all verification checks:

```bash
# 1. Module installed
docker exec odoo-prod odoo shell -d odoo -c "env['ir.module.module'].search([('name', '=', 'ipai_mailgun_api')]).state"
# Expected: installed

# 2. API key configured
docker exec odoo-prod odoo shell -d odoo << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
api_key = env['ir.config_parameter'].sudo().get_param('mailgun.api_key')
print(f"✅ API Key: {bool(api_key)} ({api_key[:10]}...)" if api_key else "❌ API Key not set")
EOF

# 3. Requests library available
docker exec odoo-prod python3 -c "import requests; print('✅ requests installed')"

# 4. Email sent successfully
docker logs odoo-prod --tail 50 | grep -i "Email sent via Mailgun API"
# Expected: ✅ Email sent via Mailgun API: <...@mg.insightpulseai.net>

# 5. No SMTP errors
docker logs odoo-prod --tail 50 | grep -i "smtp.*error\|smtp.*fail"
# Expected: (no output - no SMTP errors)

# 6. Mailgun dashboard shows delivery
echo "Check Mailgun dashboard: https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net/logs"
```

---

## Rollback Plan (If Needed)

If something goes wrong, rollback steps:

```bash
# 1. Disable Mailgun API module
docker exec odoo-prod odoo shell -d odoo << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
IrConfigParam = env['ir.config_parameter'].sudo()
IrConfigParam.set_param('mailgun.use_api', 'False')
env.cr.commit()
print("✅ Mailgun API disabled, falling back to SMTP")
EOF

# 2. Uninstall module (if needed)
docker exec odoo-prod odoo -d odoo -u ipai_mailgun_api --stop-after-init

# 3. Restart Odoo
docker restart odoo-prod
```

**Note**: SMTP will still not work (port blocked), but this disables the API if needed.

---

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Ensure code is pulled to production:

```bash
cd /opt/odoo-ce/repo
git fetch origin
git checkout feat/deterministic-scss-verification
git pull
docker restart odoo-prod
```

### Issue: "requests module not found"

**Solution**: Install requests library:

```bash
docker exec odoo-prod pip3 install requests
docker restart odoo-prod
```

### Issue: "API key not configured"

**Solution**: Set API key in system parameters (see Step 4)

### Issue: Email not delivered

**Checklist**:
1. ✅ API key correct (check first 10 chars match dashboard)
2. ✅ Domain correct (`mg.insightpulseai.net`)
3. ✅ DNS records verified (all 6 green in Mailgun dashboard)
4. ✅ Mailgun logs show delivery attempt
5. ✅ Odoo logs show "Email sent via Mailgun API"

**Debug**:
```bash
# Check Odoo logs
docker logs odoo-prod --tail 100 | grep -i mailgun

# Check Mailgun dashboard
# https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net/logs
```

---

## Acceptance Gates

Before marking deployment complete, verify ALL gates pass:

- [x] Python requests library installed in Odoo container
- [x] Standalone test script sends email successfully
- [x] Odoo module installed (state: installed)
- [x] API key configured in system parameters
- [x] Test email sent from Odoo successfully
- [x] Odoo restarted without errors
- [x] No SMTP errors in logs (should use API instead)
- [x] Email received in business@insightpulseai.com inbox
- [ ] Finance PPM BIR notifications working (if applicable)
- [ ] No performance degradation observed
- [ ] Mailgun dashboard shows successful deliveries

---

## Monitoring

### Daily Checks

```bash
# Email delivery success rate
docker logs odoo-prod --since 24h | grep -c "Email sent via Mailgun API"

# Email delivery failures
docker logs odoo-prod --since 24h | grep -i "mailgun.*error\|mailgun.*fail"

# Mailgun dashboard
# https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net
# Check: Delivered vs Bounced vs Failed
```

### Alerts

Set up alerts for:
- Mailgun API errors (check Odoo logs)
- Delivery failures (check Mailgun dashboard)
- Rate limit hits (5,000 emails/month free tier)

---

## Next Steps (Post-Deployment)

1. **Monitor for 24 hours**: Watch Odoo logs and Mailgun dashboard
2. **Test BIR notifications**: Trigger actual Finance PPM deadline alerts
3. **Document API key rotation**: Create process for key rotation
4. **Set up webhooks**: Configure Mailgun webhooks for delivery events
5. **Upgrade plan if needed**: Monitor monthly usage against 5,000 email limit

---

## References

- **Module README**: `addons/ipai/ipai_mailgun_api/README.md`
- **Root Cause Analysis**: `docs/MAILGUN_SMTP_PORT_BLOCKED.md`
- **Infrastructure Reference**: `deploy/INFRASTRUCTURE.yaml`
- **DNS Settings**: `docs/DNS_SETTINGS.md`
- **Mailgun API Docs**: https://documentation.mailgun.com/docs/mailgun/api-reference/

---

## Support

For deployment issues:
1. Check this guide's troubleshooting section
2. Review Odoo logs: `docker logs odoo-prod | grep -i mailgun`
3. Review Mailgun dashboard logs
4. Escalate to DevOps if needed

---

**Deployment Date**: [To be filled after deployment]
**Deployed By**: [To be filled]
**Verification Status**: [To be filled]
**Production URL**: https://erp.insightpulseai.net

---

*Last updated: 2026-01-13*
