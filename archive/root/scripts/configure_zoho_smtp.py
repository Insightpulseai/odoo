#!/usr/bin/env python3
"""
configure_zoho_smtp.py - Configure Zoho SMTP for Odoo 18
Run with: docker exec -i odoo-core odoo shell -d odoo_core < configure_zoho_smtp.py

Zoho Workplace Account: business@insightpulseai.com
"""

# ============================================
# CONFIGURATION VALUES
# ============================================

SMTP_CONFIG = {
    "name": "Zoho SMTP - InsightPulse",
    "smtp_host": "smtppro.zoho.com",
    "smtp_port": 465,
    "smtp_encryption": "ssl",  # SSL/TLS
    "smtp_user": "business@insightpulseai.com",
    "smtp_pass": "",  # SET THIS IN ODOO UI: Settings → Technical → Outgoing Mail Servers
    "from_filter": "business@insightpulseai.com",
    "sequence": 10,
    "smtp_authentication": "login",
    "smtp_debug": False,
    "active": True,
}

SYSTEM_PARAMS = {
    "mail.catchall.domain": "insightpulseai.com",
    "mail.default.from": "business",
    "mail.catchall.alias": "catchall",
    "mail.bounce.alias": "bounce",
}

# ============================================
# CONFIGURE MAIL SERVER
# ============================================

print("=" * 60)
print("Zoho SMTP Configuration for Odoo 18")
print("=" * 60)

MailServer = env["ir.mail_server"].sudo()

# Check for existing Zoho server
existing = MailServer.search([("smtp_host", "=", "smtppro.zoho.com")], limit=1)

if existing:
    print(f"\n⚠️  Existing Zoho server found (ID: {existing.id})")
    print("   Updating configuration...")
    existing.write(SMTP_CONFIG)
    server = existing
else:
    print("\n📧 Creating new Zoho SMTP server...")
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

ICP = env["ir.config_parameter"].sudo()

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
print("\n⚠️  CRITICAL NEXT STEPS:")
print("1. Go to Settings > Technical > Outgoing Mail Servers")
print("2. Click on 'Zoho SMTP - InsightPulse'")
print("3. Set the Password field (your Zoho password or app password)")
print("4. Save the record")
print("5. Click 'Test Connection' button")
print("\n⚠️  NETWORK ISSUE:")
print("DigitalOcean blocks outbound SMTP ports by default.")
print("You must submit a support ticket to unblock port 465.")
print("See: docs/DIGITALOCEAN_SMTP_UNBLOCK_REQUEST.md")
print("\nTo test manually in shell:")
print(
    "   server = env['ir.mail_server'].sudo().search([('smtp_host', '=', 'smtppro.zoho.com')], limit=1)"
)
print("   server.test_smtp_connection()")
