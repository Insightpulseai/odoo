#!/usr/bin/env python3
# scripts/verify_mailgun_domain.py
#
# Calls Mailgun Domains Verify endpoint and prints DNS verification state.
# Exits 0 only when SPF + DKIM are both valid (domain is fully verified).
#
# Required env vars:
#   MAILGUN_API_KEY  — Mailgun API key (primary account key or domain sending key)
#   MAILGUN_DOMAIN   — sending domain (default: mg.insightpulseai.com)
#
# Optional:
#   MAILGUN_API_BASE — API base URL (default: https://api.mailgun.net for US)
#                      Use https://api.eu.mailgun.net for EU regions
#
# Usage:
#   MAILGUN_API_KEY=... python3 scripts/verify_mailgun_domain.py
#   MAILGUN_API_KEY=... MAILGUN_DOMAIN=mg.example.com python3 scripts/verify_mailgun_domain.py
#   MAILGUN_API_KEY=... python3 scripts/verify_mailgun_domain.py --check-only  # no trigger, just read

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request


DEFAULT_DOMAIN   = "mg.insightpulseai.com"
DEFAULT_API_BASE = "https://api.mailgun.net"


def _basic_auth(api_key: str) -> str:
    token = base64.b64encode(f"api:{api_key}".encode()).decode()
    return f"Basic {token}"


def _mg_request(method: str, url: str, api_key: str) -> dict:
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": _basic_auth(api_key),
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        print(f"  ❌ HTTP {exc.code} {method} {url}", file=sys.stderr)
        print(f"     {body[:400]}", file=sys.stderr)
        sys.exit(1)


def check_domain(api_base: str, domain: str, api_key: str) -> dict:
    """GET /v3/domains/{domain} — returns current verification state."""
    url = f"{api_base}/v3/domains/{domain}"
    return _mg_request("GET", url, api_key)


def trigger_verify(api_base: str, domain: str, api_key: str) -> dict:
    """PUT /v4/domains/{domain}/verify — triggers re-verification."""
    url = f"{api_base}/v4/domains/{domain}/verify"
    return _mg_request("PUT", url, api_key)


def print_dns_records(records: list[dict]) -> None:
    for rec in records:
        name    = rec.get("name", "")
        rtype   = rec.get("record_type", rec.get("type", ""))
        value   = rec.get("value", rec.get("content", ""))
        valid   = rec.get("valid", "unknown")
        icon    = "✅" if valid == "valid" else "❌"
        print(f"    {icon} {rtype:8s} {name}")
        if valid != "valid":
            print(f"         expected: {str(value)[:80]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Mailgun domain DNS configuration")
    parser.add_argument("--check-only", action="store_true",
                        help="Only read current state, do not trigger re-verification")
    args = parser.parse_args()

    api_key  = os.environ.get("MAILGUN_API_KEY", "")
    domain   = os.environ.get("MAILGUN_DOMAIN", DEFAULT_DOMAIN)
    api_base = os.environ.get("MAILGUN_API_BASE", DEFAULT_API_BASE).rstrip("/")

    if not api_key:
        print("❌ MAILGUN_API_KEY env var is required.", file=sys.stderr)
        sys.exit(1)

    print(f"▶ Mailgun domain verification — {domain}")
    print(f"  API base: {api_base}")

    # Always read current state first
    info    = check_domain(api_base, domain, api_key)
    domain_data = info.get("domain", {})
    state   = domain_data.get("state", "unknown")
    print(f"  Current state: {state}")

    sending_dns = info.get("sending_dns_records", [])
    receiving_dns = info.get("receiving_dns_records", [])

    print("\n  Sending DNS records:")
    print_dns_records(sending_dns)
    if receiving_dns:
        print("\n  Receiving DNS records:")
        print_dns_records(receiving_dns)

    # Trigger re-verification unless --check-only
    if not args.check_only and state != "active":
        print("\n▶ Triggering re-verification...")
        verify_resp = trigger_verify(api_base, domain, api_key)
        msg = verify_resp.get("message", "")
        print(f"  Response: {msg}")

        # Re-read after trigger
        info        = check_domain(api_base, domain, api_key)
        domain_data = info.get("domain", {})
        state       = domain_data.get("state", "unknown")
        sending_dns = info.get("sending_dns_records", [])

        print(f"\n  Updated state: {state}")
        print("  Sending DNS records:")
        print_dns_records(sending_dns)

    # Determine exit code
    spf_ok  = any(r.get("valid") == "valid" and "spf"  in r.get("name", "").lower() for r in sending_dns)
    dkim_ok = any(r.get("valid") == "valid" and "dkim" in r.get("name", "").lower() for r in sending_dns)

    print()
    if state == "active" or (spf_ok and dkim_ok):
        print("✅ Domain verified — Mailgun outbound is ready.")
        sys.exit(0)
    else:
        print("⚠️  Domain not yet verified.")
        if not spf_ok:
            print("   SPF record not valid — ensure TXT 'v=spf1 include:mailgun.org ~all' is published for mg.insightpulseai.com")
        if not dkim_ok:
            print("   DKIM record not valid — ensure TXT mx._domainkey.mg.insightpulseai.com is published")
        print("   DNS propagation can take up to 48h. Re-run this script after propagation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
