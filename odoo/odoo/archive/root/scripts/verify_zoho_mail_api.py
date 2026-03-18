#!/usr/bin/env python3
"""verify_zoho_mail_api.py — smoke-test the Zoho Mail API directly.

Run OUTSIDE Odoo (no Odoo DB needed) to confirm credentials work:

    python scripts/verify_zoho_mail_api.py

Reads credentials from environment variables:
    ZOHO_CLIENT_ID
    ZOHO_CLIENT_SECRET
    ZOHO_REFRESH_TOKEN
    ZOHO_ACCOUNT_ID
    ZOHO_FROM_EMAIL   (default: no-reply@insightpulseai.com)
    ZOHO_TEST_TO      (default: same as FROM)
"""

import json
import os
import sys
import time

import requests

CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN", "")
ACCOUNT_ID = os.environ.get("ZOHO_ACCOUNT_ID", "")
FROM_EMAIL = os.environ.get("ZOHO_FROM_EMAIL", "no-reply@insightpulseai.com")
TEST_TO = os.environ.get("ZOHO_TEST_TO", FROM_EMAIL)
ACCOUNTS_BASE = os.environ.get("ZOHO_ACCOUNTS_BASE", "https://accounts.zoho.com")
MAIL_BASE = os.environ.get("ZOHO_MAIL_BASE", "https://mail.zoho.com")


def fail(msg):
    print(f"❌ FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def check():
    missing = [k for k, v in {
        "ZOHO_CLIENT_ID": CLIENT_ID,
        "ZOHO_CLIENT_SECRET": CLIENT_SECRET,
        "ZOHO_REFRESH_TOKEN": REFRESH_TOKEN,
        "ZOHO_ACCOUNT_ID": ACCOUNT_ID,
    }.items() if not v]
    if missing:
        fail(f"Missing env vars: {', '.join(missing)}")


def refresh_token():
    print("▶ Step 1: Refreshing access token...")
    resp = requests.post(
        f"{ACCOUNTS_BASE}/oauth/v2/token",
        data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
        },
        timeout=15,
    )
    if not resp.ok:
        fail(f"Token refresh failed ({resp.status_code}): {resp.text}")
    data = resp.json()
    if "error" in data:
        fail(f"Token error: {data['error']}")
    access_token = data["access_token"]
    expires_in = data.get("expires_in", 3600)
    print(f"  ✅ access_token obtained (expires_in={expires_in}s)")
    return access_token


def send_test(access_token):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    print(f"▶ Step 2: Sending test email to {TEST_TO!r}...")
    payload = {
        "fromAddress": FROM_EMAIL,
        "toAddress": TEST_TO,
        "subject": f"[ipai_zoho_mail_api] verify smoke test — {stamp}",
        "content": f"<p>Smoke test from <code>scripts/verify_zoho_mail_api.py</code>.</p><p>Timestamp: {stamp}</p>",
        "mailFormat": "html",
    }
    resp = requests.post(
        f"{MAIL_BASE}/api/accounts/{ACCOUNT_ID}/messages",
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )
    if not resp.ok:
        fail(f"Send failed ({resp.status_code}): {resp.text}")
    result = resp.json()
    code = result.get("status", {}).get("code")
    msg_id = result.get("data", {}).get("messageId", "?")
    if code != 200:
        fail(f"Zoho returned non-200 status code {code}: {json.dumps(result, indent=2)}")
    print(f"  ✅ Sent — messageId={msg_id}")
    return msg_id


def main():
    check()
    access_token = refresh_token()
    msg_id = send_test(access_token)
    print()
    print("✅ PASS — Zoho Mail API is working")
    print(f"   from:      {FROM_EMAIL}")
    print(f"   to:        {TEST_TO}")
    print(f"   messageId: {msg_id}")
    print()
    print("Next: install module in Odoo and test meeting invites + task notifications.")


if __name__ == "__main__":
    main()
