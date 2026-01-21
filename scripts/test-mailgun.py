#!/usr/bin/env python3
"""
Test Mailgun email sending configuration.

Usage:
    python scripts/test-mailgun.py <recipient-email>

Environment variables:
    MAILGUN_API_KEY - Your Mailgun API key (required)
    MAILGUN_DOMAIN  - Sending domain (default: mg.insightpulseai.net)

Example:
    MAILGUN_API_KEY=key-xxx python scripts/test-mailgun.py you@example.com
"""

import os
import sys
import json
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)


def send_test_email(recipient: str) -> bool:
    """Send a test email via Mailgun API."""

    api_key = os.environ.get("MAILGUN_API_KEY")
    domain = os.environ.get("MAILGUN_DOMAIN", "mg.insightpulseai.net")

    if not api_key:
        print("ERROR: MAILGUN_API_KEY environment variable is required")
        return False

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    hostname = os.uname().nodename if hasattr(os, "uname") else "unknown"

    print("=== Mailgun Email Test ===")
    print(f"Domain: {domain}")
    print(f"Recipient: {recipient}")
    print(f"Timestamp: {timestamp}")
    print()

    url = f"https://api.mailgun.net/v3/{domain}/messages"

    data = {
        "from": f"InsightPulse AI <postmaster@{domain}>",
        "to": recipient,
        "subject": f"[Test] Mailgun Configuration Verified - {timestamp}",
        "text": f"""This is a test email from InsightPulse AI.

Sent at: {timestamp}
Domain: {domain}
Server: {hostname}

If you received this email, your Mailgun configuration is working correctly.

--
InsightPulse AI Platform
https://insightpulseai.net""",
    }

    print("Sending test email...")

    try:
        response = requests.post(url, auth=("api", api_key), data=data, timeout=30)

        print()
        print("Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(response.text)

        print()
        print(f"HTTP Status: {response.status_code}")

        if response.status_code == 200:
            print()
            print("✅ SUCCESS: Email queued for delivery")
            print(f"Check {recipient} inbox (and spam folder) for the test email.")
            return True
        else:
            print()
            print(f"❌ FAILED: HTTP {response.status_code}")
            print("Check your API key and domain configuration.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("ERROR: Recipient email required")
        print("Usage: python scripts/test-mailgun.py <recipient-email>")
        sys.exit(1)

    recipient = sys.argv[1]
    success = send_test_email(recipient)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
