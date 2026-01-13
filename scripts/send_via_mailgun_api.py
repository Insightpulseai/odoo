#!/usr/bin/env python3
"""
Send email via Mailgun HTTP API instead of SMTP.

Usage:
    python send_via_mailgun_api.py <recipient> <subject> <body>

Environment variables:
    MAILGUN_API_KEY - Mailgun API key (from dashboard)
    MAILGUN_DOMAIN  - Sending domain (default: mg.insightpulseai.net)
"""

import os
import sys
import requests

def send_email(to, subject, text):
    """Send email via Mailgun HTTP API."""
    api_key = os.environ.get('MAILGUN_API_KEY')
    domain = os.environ.get('MAILGUN_DOMAIN', 'mg.insightpulseai.net')

    if not api_key:
        raise ValueError("MAILGUN_API_KEY environment variable required")

    url = f"https://api.mailgun.net/v3/{domain}/messages"

    response = requests.post(
        url,
        auth=("api", api_key),
        data={
            "from": f"InsightPulse AI <noreply@{domain}>",
            "to": to,
            "subject": subject,
            "text": text
        }
    )

    if response.status_code == 200:
        print(f"✅ Email sent successfully")
        print(f"   Message ID: {response.json()['id']}")
        print(f"   Status: {response.json()['message']}")
    else:
        print(f"❌ Email send failed: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: send_via_mailgun_api.py <to> <subject> <text>")
        sys.exit(1)

    send_email(sys.argv[1], sys.argv[2], sys.argv[3])
