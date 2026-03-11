#!/usr/bin/env python3
"""
verify_smtp.py - Verify SMTP configuration in Odoo

Usage:
    ./scripts/run_odoo_shell.sh scripts/verify_smtp.py

Environment Variables (optional):
    SMTP_NAME - Server name to look for (default: "Mailgun SMTP - InsightPulse")
"""

import os

SMTP_NAME = os.getenv("SMTP_NAME", "Mailgun SMTP - InsightPulse")

print("=" * 60)
print("SMTP Configuration Verification")
print("=" * 60)

MailServer = env["ir.mail_server"].sudo()

# Search by name first
server = MailServer.search([("name", "=", SMTP_NAME)], limit=1)

if not server:
    # Fallback: search for any Mailgun server
    server = MailServer.search([("smtp_host", "ilike", "mailgun")], limit=1)

if server:
    print(f"\nSTATUS: FOUND")
    print(f"\nServer Details:")
    print(f"  ID: {server.id}")
    print(f"  Name: {server.name}")
    print(f"  Host: {server.smtp_host}")
    print(f"  Port: {server.smtp_port}")
    print(f"  User: {server.smtp_user}")
    print(f"  Encryption: {server.smtp_encryption}")
    print(f"  FROM Filter: {server.from_filter or 'Not set'}")
    print(f"  Active: {server.active}")
    print(f"  Sequence: {server.sequence}")
else:
    print(f"\nSTATUS: MISSING")
    print(f"\nNo SMTP server found with name '{SMTP_NAME}'")

    # List all servers
    all_servers = MailServer.search([])
    if all_servers:
        print(f"\nExisting servers ({len(all_servers)}):")
        for s in all_servers:
            print(
                f"  - {s.name} ({s.smtp_host}:{s.smtp_port}) [{'active' if s.active else 'inactive'}]"
            )
    else:
        print("\nNo SMTP servers configured")

# Check system parameters
print("\n" + "=" * 60)
print("System Parameters")
print("=" * 60)

ICP = env["ir.config_parameter"].sudo()
params = [
    "mail.catchall.domain",
    "mail.default.from",
    "mail.catchall.alias",
    "mail.bounce.alias",
    "mail.force.smtp.from",
]

for param in params:
    value = ICP.get_param(param, default="(not set)")
    print(f"  {param} = {value}")

print("\n" + "=" * 60)
