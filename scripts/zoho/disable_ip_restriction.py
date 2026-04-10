#!/usr/bin/env python3
"""
Disable Zoho Mail IP restrictions for the insightpulseai.com organization.

Zoho's "Allowed IPs" feature blocks access from any IP not on the allowlist.
This breaks mobile data access (carrier IPs rotate via CGNAT).

This script:
  1. Authenticates via OAuth2 refresh token
  2. Fetches the current org allowed-IP list
  3. Removes all allowed IPs (disables the restriction)

Credentials: sourced from env vars (populated by Azure Key Vault).
  ZOHO_MAIL_CLIENT_ID       — OAuth client ID
  ZOHO_MAIL_CLIENT_SECRET   — OAuth client secret
  ZOHO_MAIL_REFRESH_TOKEN   — OAuth refresh token
  ZOHO_MAIL_ACCOUNT_ID      — Zoho account ID (2190180000000008002)
  ZOHO_MAIL_API_BASE_URL    — API base (default: https://mail.zoho.com)

Usage:
  # Via Azure CLI (loads secrets from Key Vault):
  az keyvault secret show --vault-name kv-ipai-dev --name zoho-mail-client-id --query value -o tsv
  # ... export all vars, then:
  python3 scripts/zoho/disable_ip_restriction.py

  # Or dry-run (shows current state without changes):
  python3 scripts/zoho/disable_ip_restriction.py --dry-run
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error


def get_env(name: str, default: str = "") -> str:
    val = os.environ.get(name, default)
    if not val:
        print(f"ERROR: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    """Exchange refresh token for a new access token."""
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())

    if "access_token" not in body:
        print(f"ERROR: OAuth token refresh failed: {body}", file=sys.stderr)
        sys.exit(1)

    return body["access_token"]


def api_get(base_url: str, path: str, token: str) -> dict:
    """GET request to Zoho Mail API."""
    url = f"{base_url}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Zoho-oauthtoken {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def api_put(base_url: str, path: str, token: str, payload: dict) -> dict:
    """PUT request to Zoho Mail API."""
    url = f"{base_url}{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json",
        },
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def api_delete(base_url: str, path: str, token: str) -> dict:
    """DELETE request to Zoho Mail API."""
    url = f"{base_url}{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
        method="DELETE",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"status": {"code": e.code, "description": body}}


def main():
    dry_run = "--dry-run" in sys.argv

    client_id = get_env("ZOHO_MAIL_CLIENT_ID")
    client_secret = get_env("ZOHO_MAIL_CLIENT_SECRET")
    refresh_token = get_env("ZOHO_MAIL_REFRESH_TOKEN")
    base_url = os.environ.get("ZOHO_MAIL_API_BASE_URL", "https://mail.zoho.com")

    print("=== Zoho Mail IP Restriction Manager ===")
    print(f"API base: {base_url}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print()

    # Step 1: Get access token
    print("Refreshing OAuth access token...")
    token = refresh_access_token(client_id, client_secret, refresh_token)
    print("PASS: Access token obtained")
    print()

    # Step 2: Get organization details
    print("Fetching organization details...")
    org_resp = api_get(base_url, "/api/organization", token)

    if "data" in org_resp:
        org_data = org_resp["data"]
        org_id = org_data.get("zoid") or org_data.get("orgId") or org_data.get("identifier")
        org_name = org_data.get("companyName", org_data.get("orgName", "unknown"))
        print(f"  Org: {org_name}")
        print(f"  ID:  {org_id}")
    else:
        print(f"  Raw response: {json.dumps(org_resp, indent=2)}")
        org_id = None

    print()

    # Step 3: Get current allowed IPs
    print("Fetching allowed IPs...")
    try:
        ip_resp = api_get(base_url, "/api/organization/allowedips", token)
        allowed_ips = ip_resp.get("data", {}).get("allowedIPs", [])
        if not allowed_ips:
            allowed_ips = ip_resp.get("data", [])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("  Endpoint /api/organization/allowedips not found.")
            print("  Trying alternative: /api/organization/policy...")
            try:
                policy_resp = api_get(base_url, "/api/organization/policy", token)
                print(f"  Policy response: {json.dumps(policy_resp, indent=2)[:500]}")
                allowed_ips = policy_resp.get("data", {}).get("allowedIPs", [])
            except urllib.error.HTTPError:
                allowed_ips = []
        else:
            print(f"  ERROR: HTTP {e.code}: {e.read().decode()[:200]}")
            allowed_ips = []

    if allowed_ips:
        print(f"  Current allowed IPs ({len(allowed_ips)}):")
        for ip in allowed_ips:
            if isinstance(ip, dict):
                print(f"    - {ip.get('ip', ip)}")
            else:
                print(f"    - {ip}")
    else:
        print("  No allowed IPs configured (restriction may already be disabled)")
        print()
        print("RESULT: IP restriction appears to already be disabled.")
        print("If you're still seeing the error, check Zoho admin console manually:")
        print("  admin.zoho.com → Security → Allowed IPs")
        return

    print()

    if dry_run:
        print("DRY-RUN: Would remove all allowed IPs to disable restriction.")
        print("Run without --dry-run to execute.")
        return

    # Step 4: Remove all allowed IPs
    print("Removing all allowed IPs to disable IP restriction...")
    for ip_entry in allowed_ips:
        ip_val = ip_entry.get("ip", ip_entry) if isinstance(ip_entry, dict) else ip_entry
        ip_id = ip_entry.get("ipId", "") if isinstance(ip_entry, dict) else ""

        if ip_id:
            result = api_delete(base_url, f"/api/organization/allowedips/{ip_id}", token)
        else:
            # Try removing by IP value
            result = api_delete(
                base_url,
                f"/api/organization/allowedips?ip={urllib.parse.quote(str(ip_val))}",
                token,
            )

        status = result.get("status", {})
        code = status.get("code", 200)
        if code in (200, 204):
            print(f"  Removed: {ip_val}")
        else:
            print(f"  WARN: Could not remove {ip_val}: {status}")

    print()
    print("PASS: IP restrictions disabled. Mobile data access should now work.")
    print()
    print("If the error persists, also check Mail Policy restrictions:")
    print("  admin.zoho.com → Mail Administration → Mail Policy → Access Restriction")


if __name__ == "__main__":
    main()
