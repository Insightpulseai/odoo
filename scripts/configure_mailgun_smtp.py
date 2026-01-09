#!/usr/bin/env python3
"""
configure_mailgun_smtp.py - Configure Mailgun SMTP for Odoo 18 on DigitalOcean

This script configures Mailgun SMTP using PORT 2525, which bypasses DigitalOcean's
SMTP port blocking (ports 25, 465, 587 are blocked by default).

Run with: docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_mailgun_smtp.py

For SendGrid, use configure_sendgrid_smtp.py instead.
"""

# ============================================
# CONFIGURATION VALUES - UPDATE THESE
# ============================================

SMTP_CONFIG = {
    'name': 'Mailgun SMTP - InsightPulse',
    'smtp_host': 'smtp.mailgun.org',
    'smtp_port': 2525,  # Port 2525 bypasses DigitalOcean blocking!
    'smtp_encryption': 'starttls',  # TLS (STARTTLS)
    'smtp_user': 'postmaster@mg.insightpulseai.net',  # Mailgun SMTP user
    'smtp_pass': '',  # SET VIA ODOO UI after running this script
    'from_filter': '@mg.insightpulseai.net',  # Domain-based FROM filter
    'sequence': 10,
    'smtp_authentication': 'login',
    'smtp_debug': False,
    'active': True,
}

SYSTEM_PARAMS = {
    'mail.catchall.domain': 'mg.insightpulseai.net',
    'mail.default.from': 'notifications',
    'mail.catchall.alias': 'catchall',
    'mail.bounce.alias': 'bounce',
    # Force all outgoing mail to use authorized sender
    'mail.force.smtp.from': 'postmaster@mg.insightpulseai.net',
}

# ============================================
# CONFIGURE MAIL SERVER
# ============================================

print("=" * 60)
print("Mailgun SMTP Configuration for Odoo 18 (DigitalOcean)")
print("=" * 60)
print("\nUsing PORT 2525 to bypass DigitalOcean SMTP blocking")

MailServer = env['ir.mail_server'].sudo()

# Check for existing Mailgun server
existing = MailServer.search([('smtp_host', '=', 'smtp.mailgun.org')], limit=1)

if existing:
    print(f"\nExisting Mailgun server found (ID: {existing.id})")
    print("   Updating configuration...")
    existing.write(SMTP_CONFIG)
    server = existing
else:
    print("\nCreating new Mailgun SMTP server...")
    server = MailServer.create(SMTP_CONFIG)

print(f"\nMail Server configured:")
print(f"   ID: {server.id}")
print(f"   Name: {server.name}")
print(f"   Host: {server.smtp_host}:{server.smtp_port}")
print(f"   Encryption: {server.smtp_encryption}")
print(f"   User: {server.smtp_user}")
print(f"   FROM Filter: {server.from_filter or 'Not set'}")

# ============================================
# CONFIGURE SYSTEM PARAMETERS
# ============================================

print("\n" + "=" * 60)
print("System Parameters Configuration")
print("=" * 60)

ICP = env['ir.config_parameter'].sudo()

for key, value in SYSTEM_PARAMS.items():
    ICP.set_param(key, value)
    print(f"   {key} = {value}")

# ============================================
# COMMIT CHANGES
# ============================================

env.cr.commit()

print("\n" + "=" * 60)
print("Configuration Complete!")
print("=" * 60)
print("\nNEXT STEPS:")
print("1. Go to Settings > Technical > Outgoing Mail Servers")
print("2. Click on 'Mailgun SMTP - InsightPulse'")
print("3. Set the Password field (your Mailgun SMTP password)")
print("4. Save the record")
print("5. Click 'Test Connection' button")
print("\nMAILGUN SETUP (if not done):")
print("1. Sign up at: https://www.mailgun.com/")
print("2. Add your domain: Sending > Domains > Add Domain")
print("3. Configure DNS records (SPF, DKIM, MX)")
print("4. Get SMTP credentials: Sending > Domain Settings > SMTP credentials")
print("\nPORT 2525 INFO:")
print("   Port 2525 is an alternative SMTP submission port")
print("   It works on DigitalOcean without requesting port unblock")
print("   Mailgun, SendGrid, and Brevo all support port 2525")
print("\nTo test manually in shell:")
print("   server = env['ir.mail_server'].sudo().search([('smtp_host', '=', 'smtp.mailgun.org')], limit=1)")
print("   server.test_smtp_connection()")
