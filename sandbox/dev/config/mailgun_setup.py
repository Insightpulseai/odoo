#!/usr/bin/env python3
"""
Mailgun SMTP Configuration for Odoo
Configure outgoing mail server for mg.insightpulseai.net
"""

import os
import sys

# Odoo shell script - run with:
# docker exec -i odoo odoo shell -d odoo_dev_sandbox < sandbox/dev/config/mailgun_setup.py

# Get SMTP password from environment
smtp_password = os.getenv('MAILGUN_SMTP_PASSWORD')
if not smtp_password:
    print("❌ ERROR: MAILGUN_SMTP_PASSWORD not set in environment")
    print("Add to ~/.zshrc: export MAILGUN_SMTP_PASSWORD='your-mailgun-smtp-password'")
    sys.exit(1)

# Check if mail server already exists
existing = env['ir.mail_server'].search([
    ('smtp_host', '=', 'smtp.mailgun.org'),
    ('smtp_user', '=', 'postmaster@mg.insightpulseai.net')
], limit=1)

if existing:
    print(f"📧 Updating existing mail server: {existing.name}")
    existing.write({
        'smtp_port': 587,
        'smtp_encryption': 'starttls',
        'smtp_pass': smtp_password,
        'smtp_from': 'no-reply@mg.insightpulseai.net',
        'sequence': 10,
    })
    mail_server = existing
else:
    print("📧 Creating new Mailgun mail server...")
    mail_server = env['ir.mail_server'].create({
        'name': 'Mailgun (mg.insightpulseai.net)',
        'smtp_host': 'smtp.mailgun.org',
        'smtp_port': 587,
        'smtp_encryption': 'starttls',
        'smtp_user': 'postmaster@mg.insightpulseai.net',
        'smtp_pass': smtp_password,
        'smtp_from': 'no-reply@mg.insightpulseai.net',
        'sequence': 10,
    })

# Commit changes
env.cr.commit()

print(f"✅ Mail server configured: {mail_server.name}")
print(f"   SMTP Host: {mail_server.smtp_host}")
print(f"   SMTP Port: {mail_server.smtp_port}")
print(f"   SMTP User: {mail_server.smtp_user}")
print(f"   From: {mail_server.smtp_from}")
print("")
print("Testing SMTP connection...")

try:
    mail_server.test_smtp_connection()
    print("✅ SMTP connection test PASSED")
except Exception as e:
    print(f"❌ SMTP connection test FAILED: {e}")
    print("")
    print("Troubleshooting:")
    print("1. Verify MAILGUN_SMTP_PASSWORD is correct")
    print("2. Check Mailgun domain is verified: https://app.mailgun.com/app/sending/domains")
    print("3. Ensure DNS records are propagated: dig +short mg.insightpulseai.net MX")
