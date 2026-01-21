#!/usr/bin/env python3
"""
configure_sendgrid_smtp.py - Configure SendGrid SMTP for Odoo 18 on DigitalOcean

This script configures SendGrid SMTP using PORT 2525, which bypasses DigitalOcean's
SMTP port blocking (ports 25, 465, 587 are blocked by default).

SendGrid is a DigitalOcean partner and provides 100 free emails/day.

Run with: docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_sendgrid_smtp.py

For Mailgun, use configure_mailgun_smtp.py instead.
"""

# ============================================
# CONFIGURATION VALUES - UPDATE THESE
# ============================================

SMTP_CONFIG = {
    "name": "SendGrid SMTP - InsightPulse",
    "smtp_host": "smtp.sendgrid.net",
    "smtp_port": 2525,  # Port 2525 bypasses DigitalOcean blocking!
    "smtp_encryption": "starttls",  # TLS (STARTTLS)
    "smtp_user": "apikey",  # SendGrid uses literal "apikey" as username
    "smtp_pass": "",  # Your SendGrid API key - SET VIA ODOO UI
    "from_filter": "@insightpulseai.net",  # Domain-based FROM filter
    "sequence": 10,
    "smtp_authentication": "login",
    "smtp_debug": False,
    "active": True,
}

SYSTEM_PARAMS = {
    "mail.catchall.domain": "insightpulseai.net",
    "mail.default.from": "notifications",
    "mail.catchall.alias": "catchall",
    "mail.bounce.alias": "bounce",
    # Force all outgoing mail to use authorized sender
    "mail.force.smtp.from": "notifications@insightpulseai.net",
}

# ============================================
# CONFIGURE MAIL SERVER
# ============================================

print("=" * 60)
print("SendGrid SMTP Configuration for Odoo 18 (DigitalOcean)")
print("=" * 60)
print("\nUsing PORT 2525 to bypass DigitalOcean SMTP blocking")

MailServer = env["ir.mail_server"].sudo()

# Check for existing SendGrid server
existing = MailServer.search([("smtp_host", "=", "smtp.sendgrid.net")], limit=1)

if existing:
    print(f"\nExisting SendGrid server found (ID: {existing.id})")
    print("   Updating configuration...")
    existing.write(SMTP_CONFIG)
    server = existing
else:
    print("\nCreating new SendGrid SMTP server...")
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

ICP = env["ir.config_parameter"].sudo()

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
print("2. Click on 'SendGrid SMTP - InsightPulse'")
print("3. Set the Password field (your SendGrid API key)")
print("4. Save the record")
print("5. Click 'Test Connection' button")
print("\nSENDGRID SETUP (if not done):")
print("1. Sign up at: https://signup.sendgrid.com/")
print("2. Create API key: Settings > API Keys > Create API Key")
print("3. Select 'Full Access' or 'Restricted Access' with Mail Send permission")
print("4. Copy the API key (shown only once!)")
print("5. Verify sender: Settings > Sender Authentication")
print("\nSENDGRID + DIGITALOCEAN:")
print("   SendGrid is a DigitalOcean partner")
print("   Free tier: 100 emails/day")
print("   Port 2525 is NOT blocked by DigitalOcean")
print("\nIMPORTANT - USERNAME:")
print("   SendGrid uses literal 'apikey' as SMTP username")
print("   Password is your actual SendGrid API key")
print("\nTo test manually in shell:")
print(
    "   server = env['ir.mail_server'].sudo().search([('smtp_host', '=', 'smtp.sendgrid.net')], limit=1)"
)
print("   server.test_smtp_connection()")
