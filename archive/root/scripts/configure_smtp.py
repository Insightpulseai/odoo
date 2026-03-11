#!/usr/bin/env python3
"""
configure_smtp.py - Configure SMTP server in Odoo from environment variables

This script reads SMTP configuration from environment variables (no hardcoded secrets)
and creates/updates the mail server in Odoo.

Environment Variables:
    SMTP_NAME       - Server name (default: "Mailgun SMTP - InsightPulse")
    SMTP_HOST       - SMTP hostname (required)
    SMTP_PORT       - SMTP port (default: 2525)
    SMTP_USER       - SMTP username (required)
    SMTP_PASSWORD   - SMTP password (required)
    SMTP_ENCRYPTION - Encryption type: starttls, ssl, or false (default: starttls)
    SMTP_FROM_FILTER - FROM filter domain (optional)
    MAIL_CATCHALL_DOMAIN - Catchall domain for system params (optional)
    MAIL_FORCE_FROM - Force FROM address (optional)

Usage:
    export SMTP_HOST=smtp.mailgun.org
    export SMTP_PORT=2525
    export SMTP_USER=postmaster@mg.example.com
    export SMTP_PASSWORD=your-password-here
    ./scripts/run_odoo_shell.sh scripts/configure_smtp.py
"""

import os
import sys

# ============================================
# READ CONFIGURATION FROM ENVIRONMENT
# ============================================

SMTP_NAME = os.getenv("SMTP_NAME", "Mailgun SMTP - InsightPulse")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_ENCRYPTION = os.getenv("SMTP_ENCRYPTION", "starttls")
SMTP_FROM_FILTER = os.getenv("SMTP_FROM_FILTER", "")

# System parameters (optional)
MAIL_CATCHALL_DOMAIN = os.getenv("MAIL_CATCHALL_DOMAIN", "")
MAIL_FORCE_FROM = os.getenv("MAIL_FORCE_FROM", "")

# ============================================
# VALIDATE REQUIRED VARIABLES
# ============================================

print("=" * 60)
print("SMTP Configuration for Odoo")
print("=" * 60)

missing = []
if not SMTP_HOST:
    missing.append("SMTP_HOST")
if not SMTP_USER:
    missing.append("SMTP_USER")
if not SMTP_PASSWORD:
    missing.append("SMTP_PASSWORD")

if missing:
    print(f"\nERROR: Missing required environment variables: {', '.join(missing)}")
    print("\nRequired variables:")
    print("  SMTP_HOST     - SMTP server hostname")
    print("  SMTP_USER     - SMTP username")
    print("  SMTP_PASSWORD - SMTP password")
    print("\nOptional variables:")
    print("  SMTP_NAME       - Server name (default: Mailgun SMTP - InsightPulse)")
    print("  SMTP_PORT       - Port number (default: 2525)")
    print("  SMTP_ENCRYPTION - starttls, ssl, or false (default: starttls)")
    sys.exit(1)

# Normalize encryption value
if SMTP_ENCRYPTION.lower() in ("false", "0", "", "none"):
    SMTP_ENCRYPTION = False

print(f"\nConfiguration:")
print(f"  Name: {SMTP_NAME}")
print(f"  Host: {SMTP_HOST}:{SMTP_PORT}")
print(f"  User: {SMTP_USER}")
print(f"  Encryption: {SMTP_ENCRYPTION}")
print(f"  FROM Filter: {SMTP_FROM_FILTER or 'Not set'}")

# ============================================
# CONFIGURE MAIL SERVER
# ============================================

MailServer = env["ir.mail_server"].sudo()

# Search for existing server by name
server = MailServer.search([("name", "=", SMTP_NAME)], limit=1)

vals = {
    "name": SMTP_NAME,
    "smtp_host": SMTP_HOST,
    "smtp_port": SMTP_PORT,
    "smtp_user": SMTP_USER,
    "smtp_pass": SMTP_PASSWORD,
    "smtp_encryption": SMTP_ENCRYPTION,
    "smtp_authentication": "login",
    "smtp_debug": False,
    "active": True,
}

if SMTP_FROM_FILTER:
    vals["from_filter"] = SMTP_FROM_FILTER

if server:
    print(f"\nUpdating existing server (ID: {server.id})...")
    server.write(vals)
else:
    print("\nCreating new SMTP server...")
    server = MailServer.create(vals)
    print(f"Created server (ID: {server.id})")

# ============================================
# CONFIGURE SYSTEM PARAMETERS (OPTIONAL)
# ============================================

if MAIL_CATCHALL_DOMAIN or MAIL_FORCE_FROM:
    print("\n" + "=" * 60)
    print("System Parameters")
    print("=" * 60)

    ICP = env["ir.config_parameter"].sudo()

    if MAIL_CATCHALL_DOMAIN:
        ICP.set_param("mail.catchall.domain", MAIL_CATCHALL_DOMAIN)
        print(f"  mail.catchall.domain = {MAIL_CATCHALL_DOMAIN}")

    if MAIL_FORCE_FROM:
        ICP.set_param("mail.force.smtp.from", MAIL_FORCE_FROM)
        print(f"  mail.force.smtp.from = {MAIL_FORCE_FROM}")

# ============================================
# TEST CONNECTION
# ============================================

print("\n" + "=" * 60)
print("Testing SMTP Connection")
print("=" * 60)

try:
    # Try different test methods (varies by Odoo version)
    for method in ("test_smtp_connection", "_test_smtp_connection", "test_connection"):
        if hasattr(server, method):
            getattr(server, method)()
            print("\nSUCCESS: SMTP connection test passed!")
            break
    else:
        print("\nWARNING: No test method available, skipping connection test")
except Exception as e:
    print(f"\nERROR: SMTP connection test failed: {e}")
    print("Check your credentials and network connectivity")

# ============================================
# COMMIT CHANGES
# ============================================

env.cr.commit()

print("\n" + "=" * 60)
print(f"DONE: SMTP configured - {SMTP_NAME} ({SMTP_HOST}:{SMTP_PORT})")
print("=" * 60)
