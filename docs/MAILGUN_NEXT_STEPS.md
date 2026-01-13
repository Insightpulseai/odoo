# Mailgun Email Setup - Next Steps

**Current Status:** DNS verified ✅ | SMTP password needed ⏳

---

## Immediate Action Required

### 1. Get SMTP Password from Mailgun

**URL:** https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net

**Steps:**
1. Navigate to Mailgun dashboard (link above)
2. Go to "Domain Settings" → "SMTP Credentials"
3. Find user: `postmaster@mg.insightpulseai.net`
4. Copy the SMTP password (or reset if needed)

---

### 2. Add Password to Odoo Production

**Method A: Via Odoo UI** (Recommended)

1. SSH to production server:
   ```bash
   ssh root@178.128.112.214
   ```

2. Access Odoo at: https://erp.insightpulseai.net
   - Login as admin
   - Navigate to: Settings → Technical → Email → Outgoing Mail Servers
   - Click on "Mailgun SMTP - InsightPulse AI"
   - Enter SMTP password
   - Click "Test Connection"
   - Save

**Method B: Via Python Script** (If UI access unavailable)

```bash
# SSH to production
ssh root@178.128.112.214

# Create password update script
cat > /tmp/add_smtp_password.py << 'EOF'
import odoo
from odoo import api, SUPERUSER_ID

db_name = 'odoo'
password = 'YOUR_MAILGUN_PASSWORD_HERE'  # Replace with actual password

registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Update mail server password
    mail_server = env['ir.mail_server'].search([
        ('smtp_host', '=', 'smtp.mailgun.org')
    ], limit=1)

    if mail_server:
        mail_server.smtp_pass = password
        cr.commit()
        print(f'✅ Updated password for {mail_server.name}')
    else:
        print('❌ Mail server not found')
EOF

# Run the script
docker exec odoo-prod python3 /tmp/add_smtp_password.py
```

---

### 3. Verify Email Sending

**After adding password, test immediately:**

```bash
# SSH to production
ssh root@178.128.112.214

# Create test script
cat > /tmp/send_test_email.py << 'EOF'
import odoo
from odoo import api, SUPERUSER_ID

db_name = 'odoo'
registry = odoo.registry(db_name)

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Get mail server
    mail_server = env['ir.mail_server'].search([
        ('smtp_host', '=', 'smtp.mailgun.org')
    ], limit=1)

    if not mail_server:
        print('❌ Mail server not found')
        exit(1)

    # Test SMTP connection
    try:
        print('📧 Testing SMTP connection...')
        mail_server.test_smtp_connection()
        print('✅ SMTP connection successful!')
    except Exception as e:
        print(f'❌ SMTP connection failed: {str(e)}')
        exit(1)

    # Send actual test email
    try:
        print('📧 Sending test email...')
        mail = env['mail.mail'].create({
            'subject': 'Mailgun Test Email',
            'body_html': '<p>This is a test email from Odoo production.</p>',
            'email_to': 'your-email@example.com',  # Replace with your email
            'email_from': 'noreply@mg.insightpulseai.net',
        })
        mail.send()
        print('✅ Test email sent successfully!')
        print(f'   Check your inbox: your-email@example.com')
    except Exception as e:
        print(f'❌ Email send failed: {str(e)}')
EOF

# Run test
docker exec odoo-prod python3 /tmp/send_test_email.py
```

---

### 4. Verify in Mailgun Dashboard

**After successful test:**

1. Go to: https://app.mailgun.com/mg/sending/domains/mg.insightpulseai.net/verify
2. Click "Verify DNS Settings"
3. Confirm all status indicators are green:
   - ✅ SPF record
   - ✅ DKIM record
   - ✅ MX records
   - ✅ CNAME record
   - ✅ DMARC record

---

## Expected Timeline

| Step | Duration | Status |
|------|----------|--------|
| DNS propagation | 10-60 min | ✅ Complete |
| Get SMTP password | 2 min | ⏳ Pending |
| Add to Odoo | 2 min | ⏳ Pending |
| Test connection | 30 sec | ⏳ Pending |
| Verify in Mailgun | 2 min | ⏳ Pending |
| **Total** | **~15 min** | **⏳ 7 min remaining** |

---

## Troubleshooting

### SMTP Connection Still Fails After Adding Password

**Check 1: Verify password is correct**
```bash
# Test SMTP auth directly
curl -v --ssl-reqd \
  --url 'smtp://smtp.mailgun.org:587' \
  --user 'postmaster@mg.insightpulseai.net:YOUR_PASSWORD' \
  --mail-from 'noreply@mg.insightpulseai.net' \
  --mail-rcpt 'test@example.com' \
  --upload-file /dev/null
```

**Check 2: Verify Odoo mail server config**
```bash
ssh root@178.128.112.214
docker exec odoo-prod psql -U odoo -d odoo -c "
  SELECT name, smtp_host, smtp_port, smtp_user, smtp_encryption, active
  FROM ir_mail_server
  WHERE smtp_host = 'smtp.mailgun.org';
"
```

**Check 3: Check Odoo logs**
```bash
docker logs odoo-prod --tail 100 | grep -i mail
```

### Mailgun Dashboard Shows Red Status

**Wait for DNS propagation:**
- DNS changes can take up to 48 hours (usually 10-60 minutes)
- Check propagation: https://dnschecker.org/

**Verify records manually:**
```bash
dig TXT mg.insightpulseai.net +short
dig TXT pic._domainkey.mg.insightpulseai.net +short
dig MX mg.insightpulseai.net +short
dig CNAME email.mg.insightpulseai.net +short
dig TXT _dmarc.mg.insightpulseai.net +short
```

---

## Post-Setup Verification

### Finance PPM Email Features

Once email is working, verify these automatic features:

1. **BIR Deadline Alerts** (7 days before deadline)
   - Check: Mattermost channel for notifications
   - Test: Create a BIR task due in 7 days

2. **Task Escalation** (3 days before deadline)
   - Check: Finance Director receives escalation email
   - Test: Create overdue task and verify escalation

3. **Monthly Compliance Summary** (End of month)
   - Check: Email report generated automatically
   - Test: Manually trigger end-of-month job

---

## Success Confirmation

**Email is working when ALL of these pass:**

- ✅ SMTP connection test succeeds in Odoo
- ✅ Test email received in inbox
- ✅ All Mailgun dashboard indicators green
- ✅ Finance PPM notifications sending automatically
- ✅ No errors in Odoo mail logs

---

*Last updated: 2026-01-13*
*Next action: Add SMTP password from Mailgun dashboard*
