#!/usr/bin/env python3
"""
configure_gmail_smtp.py - Configure Gmail SMTP for Odoo 18
Run with: docker exec -i odoo odoo shell -d odoo < configure_gmail_smtp.py

Gmail App Password: vzab hqzh wvhm zsgz (from Google Account)
"""

# ============================================
# CONFIGURATION VALUES
# ============================================

SMTP_CONFIG = {
    'name': 'Gmail SMTP - InsightPulse',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_encryption': 'starttls',  # TLS (STARTTLS)
    'smtp_user': 'jgtolentino88@gmail.com',  # UPDATE: Your Gmail address
    'smtp_pass': 'vzabhqzhwvhmzsgz',  # App password (no spaces)
    'from_filter': 'jgtolentino88@gmail.com',  # FROM Filtering - same as smtp_user
    'sequence': 10,  # Priority (lower = higher priority)
    'smtp_authentication': 'login',  # Username/Password auth
    'smtp_debug': False,  # Debugging off in production
    'active': True,
}

SYSTEM_PARAMS = {
    'mail.catchall.domain': 'insightpulseai.net',
    'mail.default.from': 'notifications',
    'mail.catchall.alias': 'catchall',
    'mail.bounce.alias': 'bounce',
}

# ============================================
# CONFIGURE MAIL SERVER
# ============================================

print("=" * 60)
print("Gmail SMTP Configuration for Odoo 18")
print("=" * 60)

MailServer = env['ir.mail_server'].sudo()

# Check for existing Gmail server
existing = MailServer.search([('smtp_host', '=', 'smtp.gmail.com')], limit=1)

if existing:
    print(f"\n⚠️  Existing Gmail server found (ID: {existing.id})")
    print("   Updating configuration...")
    existing.write(SMTP_CONFIG)
    server = existing
else:
    print("\n📧 Creating new Gmail SMTP server...")
    server = MailServer.create(SMTP_CONFIG)

print(f"\n✅ Mail Server configured:")
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
print("✅ Configuration Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Go to Settings > Technical > Outgoing Mail Servers")
print("2. Click on 'Gmail SMTP - InsightPulse'")
print("3. Click 'Test Connection' button")
print("4. If successful, you're ready to send emails!")
print("\nTo test manually in shell:")
print("   server = env['ir.mail_server'].sudo().search([('smtp_host', '=', 'smtp.gmail.com')], limit=1)")
print("   server.test_smtp_connection()")
