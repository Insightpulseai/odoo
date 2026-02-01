# DigitalOcean Email Setup for Odoo CE 18

**Version**: 1.0
**Date**: 2026-01-05
**Stack**: Odoo 18 CE on DigitalOcean Droplet

---

## The Problem: DigitalOcean SMTP Port Blocking

DigitalOcean **permanently blocks** standard outbound SMTP ports for new accounts to prevent spam:
- **Port 25** - Blocked (legacy SMTP relay)
- **Port 465** - Blocked (SMTPS/SSL)
- **Port 587** - Blocked (SMTP Submission/STARTTLS)

Traditional configurations using these ports will result in:
- "Connection Test Failed" errors in Odoo
- Socket connection timeouts
- Emails stuck in "Outgoing" queue

**Analogy**: Setting up email on DigitalOcean is like trying to mail a letter from a high-security facility. The standard exit gates (ports 25, 465, 587) are locked tight. You need a specialized courier service (port 2525 or API) that has its own authorized side-door.

---

## Solution Options

### Option A: Port 2525 SMTP (Recommended - Fastest Implementation)

Port **2525** is an alternative SMTP submission port that is **NOT blocked** by DigitalOcean. Major providers support it:

| Provider | SMTP Server | Port | Free Tier |
|----------|-------------|------|-----------|
| **Mailgun** | smtp.mailgun.org | 2525 | 5,000 emails/month (3 months) |
| **SendGrid** | smtp.sendgrid.net | 2525 | 100 emails/day |
| **Brevo** | smtp-relay.brevo.com | 2525 | 300 emails/day |

**Pros**:
- Works immediately on DigitalOcean
- No support ticket required
- Standard SMTP protocol (easy debugging)
- All major providers support it

**Cons**:
- Requires third-party provider account
- Free tiers have volume limits

### Option B: API-Based Sending (Most Reliable)

Use RESTful HTTP APIs instead of SMTP. This uses **port 443 (HTTPS)** which is never blocked.

| Provider | API Endpoint | Free Tier |
|----------|--------------|-----------|
| **Mailgun** | api.mailgun.net/v3 | 5,000 emails/month |
| **SendGrid** | api.sendgrid.com/v3 | 100 emails/day |
| **Amazon SES** | email.{region}.amazonaws.com | $0.10 per 1,000 |

**Pros**:
- Never blocked (uses HTTPS port 443)
- Up to 3x faster than SMTP
- Better deliverability metrics
- Webhook support for tracking

**Cons**:
- Requires custom Odoo module or OCA integration
- More complex initial setup

### Option C: Request SMTP Port Unblock (Legacy)

Submit a support ticket to DigitalOcean requesting port unblock.

**Process**:
1. Submit ticket: https://cloud.digitalocean.com/support/tickets
2. Subject: "Request to unblock outbound SMTP ports"
3. Explain business use case
4. Wait 24-48 hours

**Pros**:
- Can use any SMTP provider
- Gmail/Zoho work directly

**Cons**:
- May be denied (especially for new accounts)
- 24-48 hour wait time
- DigitalOcean prefers API-based solutions

---

## Quick Start: SendGrid with Port 2525

SendGrid is a DigitalOcean partner and the easiest to set up.

### Step 1: Create SendGrid Account

1. Sign up at: https://signup.sendgrid.com/
2. Verify your email address
3. Complete account setup

### Step 2: Create API Key

1. Go to: Settings > API Keys
2. Click "Create API Key"
3. Name: "Odoo ERP"
4. Select "Full Access" (or Restricted with Mail Send)
5. **Copy the API key** (shown only once!)

### Step 3: Verify Sender Domain

1. Go to: Settings > Sender Authentication
2. Click "Authenticate Your Domain"
3. Select your DNS provider
4. Add the required DNS records (SPF, DKIM)
5. Verify domain

### Step 4: Configure Odoo

**Option A - Automated Script**:
```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Navigate to project
cd /root/odoo-ce

# Run configuration script
docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_sendgrid_smtp.py
```

**Option B - Odoo UI**:
1. Go to Settings > Technical > Outgoing Mail Servers
2. Click "Create"
3. Configure:
   - **Name**: SendGrid SMTP
   - **SMTP Server**: smtp.sendgrid.net
   - **SMTP Port**: 2525
   - **Connection Security**: TLS (STARTTLS)
   - **Username**: apikey (literal string)
   - **Password**: [Your SendGrid API Key]
4. Click "Save"
5. Click "Test Connection"

### Step 5: Test Email Sending

```bash
# Test from Odoo shell
docker exec -i odoo-core odoo shell -d odoo_core <<EOF
mail = env['mail.mail'].create({
    'email_to': 'test@example.com',
    'subject': 'Test from Odoo on DigitalOcean',
    'body_html': '<p>Port 2525 works!</p>'
})
mail.send()
print(f"Email sent - State: {mail.state}")
EOF
```

---

## Quick Start: Mailgun with Port 2525

### Step 1: Create Mailgun Account

1. Sign up at: https://www.mailgun.com/
2. Verify your email
3. Add payment method (required for custom domain)

### Step 2: Add Sending Domain

1. Go to: Sending > Domains
2. Click "Add New Domain"
3. Enter: mail.yourdomain.com (or mg.yourdomain.com)
4. Select region (US or EU)

### Step 3: Configure DNS

Add these records to your DNS provider:

**SPF Record**:
```
Type: TXT
Host: mail (or your subdomain)
Value: v=spf1 include:mailgun.org ~all
```

**DKIM Records** (from Mailgun dashboard):
```
Type: TXT
Host: k1._domainkey.mail (or as shown)
Value: [Provided by Mailgun]
```

**CNAME for Tracking** (optional):
```
Type: CNAME
Host: email.mail
Value: mailgun.org
```

### Step 4: Get SMTP Credentials

1. Go to: Sending > Domain Settings
2. Click on your domain
3. Navigate to "SMTP credentials"
4. Note the SMTP login (usually postmaster@mail.yourdomain.com)
5. Reset password or create new credential

### Step 5: Configure Odoo

```bash
# Run configuration script
docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_mailgun_smtp.py
```

Or configure manually in Odoo UI:
- **SMTP Server**: smtp.mailgun.org
- **SMTP Port**: 2525
- **Connection Security**: TLS (STARTTLS)
- **Username**: postmaster@mail.yourdomain.com
- **Password**: [Your Mailgun SMTP password]

---

## DNS Configuration for Email Deliverability

**Critical**: Without proper DNS records, your emails will be flagged as spam.

### SPF (Sender Policy Framework)

Add a TXT record to authorize your email provider:

```
# For SendGrid
v=spf1 include:sendgrid.net ~all

# For Mailgun
v=spf1 include:mailgun.org ~all

# For multiple providers
v=spf1 include:sendgrid.net include:mailgun.org ~all
```

### DKIM (DomainKeys Identified Mail)

Add the DKIM TXT record provided by your email provider. Each provider gives you a unique key.

**Example** (Mailgun):
```
Host: k1._domainkey.yourdomain.com
Type: TXT
Value: k=rsa; p=MIGfMA0GCSq...
```

### DMARC (Domain-based Message Authentication)

Add a DMARC policy to tell receivers how to handle failed authentication:

```
Host: _dmarc.yourdomain.com
Type: TXT
Value: v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
```

**Policy options**:
- `p=none` - Monitor only (recommended to start)
- `p=quarantine` - Send to spam
- `p=reject` - Block completely

### Verify DNS Configuration

Use these tools to verify your DNS setup:
- **MX Toolbox**: https://mxtoolbox.com/
- **Mail-Tester**: https://www.mail-tester.com/
- **DKIM Validator**: https://dkimvalidator.com/

---

## Odoo System Parameters

Configure these system parameters for proper email handling:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `mail.catchall.domain` | yourdomain.com | Domain for catchall emails |
| `mail.default.from` | notifications | Default FROM name |
| `mail.catchall.alias` | catchall | Catchall alias |
| `mail.bounce.alias` | bounce | Bounce handling alias |
| `mail.force.smtp.from` | sender@yourdomain.com | Force all mail from this address |

### Configure via Script

```bash
docker exec -i odoo-core odoo shell -d odoo_core <<EOF
ICP = env['ir.config_parameter'].sudo()
ICP.set_param('mail.catchall.domain', 'insightpulseai.com')
ICP.set_param('mail.default.from', 'notifications')
ICP.set_param('mail.force.smtp.from', 'notifications@insightpulseai.com')
env.cr.commit()
print("System parameters configured!")
EOF
```

### Force FROM Address

To prevent "Sender Mismatch" errors:

```bash
docker exec -i odoo-core odoo shell -d odoo_core <<EOF
ICP = env['ir.config_parameter'].sudo()
ICP.set_param('mail.force.smtp.from', 'notifications@insightpulseai.com')
env.cr.commit()
print("mail.force.smtp.from configured!")
EOF
```

---

## Testing & Verification

### Test 1: SMTP Port Connectivity

```bash
# Test from inside Odoo container
docker exec odoo-core python3 <<EOF
import socket
ports = [25, 465, 587, 2525]
for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('smtp.sendgrid.net', port))
        status = 'OPEN' if result == 0 else 'BLOCKED'
        sock.close()
        print(f"Port {port}: {status}")
    except Exception as e:
        print(f"Port {port}: ERROR - {e}")
EOF
```

**Expected Output**:
```
Port 25: BLOCKED
Port 465: BLOCKED
Port 587: BLOCKED
Port 2525: OPEN
```

### Test 2: SMTP Connection Test

```bash
# Run the diagnostic script
./scripts/diagnose_smtp.sh
```

### Test 3: Odoo Connection Test

1. Go to: Settings > Technical > Outgoing Mail Servers
2. Click on your configured server
3. Click "Test Connection"
4. Expected: "Connection Test Successful!"

### Test 4: Send Test Email

```bash
docker exec -i odoo-core odoo shell -d odoo_core <<EOF
mail = env['mail.mail'].create({
    'email_to': 'your.email@gmail.com',
    'subject': 'Odoo Test Email - DigitalOcean Port 2525',
    'body_html': '<p>If you receive this, email is working!</p>'
})
mail.send()
print(f"Email ID: {mail.id}")
print(f"State: {mail.state}")
print(f"Failure: {mail.failure_reason or 'None'}")
EOF
```

---

## Troubleshooting

### Issue: "Connection Test Failed" with timeout

**Cause**: Port is blocked by DigitalOcean
**Solution**: Use port 2525 instead of 465/587

### Issue: "Authentication Required" error

**Cause**: Wrong credentials or auth method
**Solution**:
- For SendGrid: Username must be literal "apikey"
- For Mailgun: Use the SMTP password, not your account password

### Issue: Emails marked as spam

**Cause**: Missing or incorrect DNS records
**Solution**:
1. Verify SPF record is correct
2. Verify DKIM record is correct
3. Add DMARC record
4. Check sender reputation at https://www.mail-tester.com/

### Issue: "Sender address rejected"

**Cause**: FROM address doesn't match authenticated sender
**Solution**: Set `mail.force.smtp.from` system parameter

### Issue: Emails stuck in "Outgoing" state

**Cause**: Mail cron not running
**Solution**:
```bash
# Enable mail queue cron
docker exec -i odoo-core odoo shell -d odoo_core <<EOF
cron = env['ir.cron'].search([('model', '=', 'mail.mail')])
for c in cron:
    c.active = True
    print(f"Enabled cron: {c.name}")
env.cr.commit()
EOF
```

---

## API-Based Email (Advanced)

For maximum reliability, use API-based sending with an OCA module.

### Available OCA Modules

| Module | Provider | Repository |
|--------|----------|------------|
| `mail_tracking_mailgun` | Mailgun | OCA/social |
| `mail_tracking` | Multiple | OCA/social |

### Installation

1. Add OCA/social to your module sources
2. Update oca.lock.json:
```json
{
  "social": {
    "url": "https://github.com/OCA/social",
    "branch": "18.0",
    "modules": ["mail_tracking_mailgun"]
  }
}
```

3. Install the module:
```bash
docker exec odoo-core odoo -d odoo_core -i mail_tracking_mailgun --stop-after-init
```

4. Configure in Settings > Technical > Mailgun

---

## Configuration Scripts

The following scripts are available in `/scripts/`:

| Script | Purpose |
|--------|---------|
| `configure_sendgrid_smtp.py` | Configure SendGrid with port 2525 |
| `configure_mailgun_smtp.py` | Configure Mailgun with port 2525 |
| `configure_gmail_smtp.py` | Configure Gmail (requires port unblock) |
| `configure_zoho_smtp.py` | Configure Zoho (requires port unblock) |
| `diagnose_smtp.sh` | Diagnose SMTP connectivity issues |
| `audit_email_config.py` | Audit current email configuration |

### Usage

```bash
# Configure SendGrid (recommended for DigitalOcean)
docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_sendgrid_smtp.py

# Configure Mailgun
docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_mailgun_smtp.py

# Diagnose SMTP issues
./scripts/diagnose_smtp.sh

# Audit current configuration
docker exec -i odoo-core odoo shell -d odoo_core < scripts/audit_email_config.py
```

---

## Environment Variables

Add these to your `.env` file for configuration management:

```bash
# Email Provider (sendgrid, mailgun, gmail, zoho)
SMTP_PROVIDER=sendgrid

# SMTP Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=2525
SMTP_USER=apikey
SMTP_PASSWORD=your-api-key-here
SMTP_ENCRYPTION=starttls

# Email Addresses
MAIL_CATCHALL_DOMAIN=insightpulseai.com
MAIL_DEFAULT_FROM=notifications
MAIL_FORCE_FROM=notifications@insightpulseai.com
```

---

## Summary: Recommended Approach

For **DigitalOcean deployments**, use this priority order:

1. **SendGrid via Port 2525** (Fastest, DigitalOcean partner)
   - Sign up: https://signup.sendgrid.com/
   - Run: `docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_sendgrid_smtp.py`

2. **Mailgun via Port 2525** (More features, better for high volume)
   - Sign up: https://www.mailgun.com/
   - Run: `docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_mailgun_smtp.py`

3. **Request Port Unblock** (Last resort)
   - See: `docs/DIGITALOCEAN_SMTP_UNBLOCK_REQUEST.md`
   - Wait 24-48 hours

**Remember**: Always configure SPF, DKIM, and DMARC DNS records for deliverability!

---

## Related Documentation

- `DIGITALOCEAN_SMTP_UNBLOCK_REQUEST.md` - Port unblock request template
- `EMAIL_AND_OAUTH_SETUP.md` - Gmail/OAuth configuration
- `DEPLOYMENT_GUIDE.md` - Full deployment instructions

---

**Last Updated**: 2026-01-05
**Maintained By**: DevOps Team
