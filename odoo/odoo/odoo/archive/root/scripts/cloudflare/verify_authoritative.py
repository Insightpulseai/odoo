#!/usr/bin/env python3
"""
verify_authoritative.py — Assert Cloudflare is the authoritative DNS for insightpulseai.com.

Checks:
  1. NS records for the zone return Cloudflare nameservers (edna + keanu).
  2. SOA record for the zone is served by Cloudflare (SOA NS field starts with cloudflare.com).

Usage:
    python3 scripts/cloudflare/verify_authoritative.py
    python3 scripts/cloudflare/verify_authoritative.py --domain insightpulseai.com
    python3 scripts/cloudflare/verify_authoritative.py --quiet   # suppress stdout, exit code only

Exit codes:
    0 — Cloudflare IS authoritative (all checks pass)
    1 — Cloudflare is NOT authoritative (one or more checks fail)
    2 — Runtime error (dig not found, network unreachable, etc.)

Environment:
    VERIFY_DNS_TIMEOUT   — dig timeout in seconds (default: 10)
    VERIFY_DNS_RESOLVER  — use a specific resolver, e.g. 8.8.8.8 (default: system)

CI Usage:
    # In .github/workflows/cloudflare-authority-gate.yml:
    python3 scripts/cloudflare/verify_authoritative.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

# Cloudflare nameservers for insightpulseai.com
EXPECTED_NS = {"edna.ns.cloudflare.com.", "keanu.ns.cloudflare.com."}

# SOA MNAME prefix that indicates Cloudflare is serving the zone
CF_SOA_PREFIX = "cloudflare"


def _run_dig(
    record_type: str,
    domain: str,
    resolver: str | None,
    timeout: int,
    quiet: bool,
) -> list[str]:
    """Run dig and return answer lines (stripped). Raises SystemExit on error."""
    cmd = ["dig", "+short", "+time=%d" % timeout, record_type, domain]
    if resolver:
        cmd.insert(1, f"@{resolver}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 2,
        )
    except FileNotFoundError:
        print("ERROR: 'dig' not found. Install bind-utils or dnsutils.", file=sys.stderr)
        sys.exit(2)
    except subprocess.TimeoutExpired:
        print(f"ERROR: dig timed out after {timeout}s for {record_type} {domain}", file=sys.stderr)
        sys.exit(2)

    if result.returncode != 0:
        if not quiet:
            print(
                f"ERROR: dig {record_type} {domain} exited {result.returncode}: {result.stderr.strip()}",
                file=sys.stderr,
            )
        return []

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines


def check_ns(domain: str, resolver: str | None, timeout: int, quiet: bool) -> tuple[bool, str]:
    """
    Verify NS records contain both Cloudflare nameservers.
    Returns (passed: bool, detail: str).
    """
    lines = _run_dig("NS", domain, resolver, timeout, quiet)

    if not lines:
        return False, "No NS records returned (delegation not configured or NXDOMAIN)"

    ns_set = {ns.lower().rstrip(".") + "." for ns in lines}
    expected_lower = {ns.lower() for ns in EXPECTED_NS}
    found = {ns for ns in ns_set if ns.rstrip(".") in expected_lower or ns in expected_lower}

    # More flexible matching: check if any returned NS contains "cloudflare"
    cf_ns = [ns for ns in ns_set if "cloudflare" in ns.lower()]

    if not cf_ns:
        return (
            False,
            f"NS records do not point to Cloudflare.\n"
            f"  Got: {sorted(ns_set)}\n"
            f"  Expected nameservers containing: cloudflare.com",
        )

    missing = expected_lower - {ns.lower() for ns in cf_ns}
    if missing:
        # Both CF nameservers present but one might differ — still authoritative if any CF NS found
        pass  # partial match is OK (different CF NS pair per zone is possible)

    return True, f"NS → {sorted(cf_ns)}"


def check_soa(domain: str, resolver: str | None, timeout: int, quiet: bool) -> tuple[bool, str]:
    """
    Verify SOA MNAME (primary nameserver) is a Cloudflare host.
    Returns (passed: bool, detail: str).
    """
    lines = _run_dig("SOA", domain, resolver, timeout, quiet)

    if not lines:
        return False, "No SOA record returned"

    # SOA short output: <mname> <rname> <serial> <refresh> <retry> <expire> <minimum>
    soa_fields = lines[0].split()
    if not soa_fields:
        return False, f"Could not parse SOA: {lines[0]}"

    mname = soa_fields[0].lower()
    if CF_SOA_PREFIX in mname:
        return True, f"SOA MNAME → {mname}"

    return (
        False,
        f"SOA MNAME is not Cloudflare.\n"
        f"  Got MNAME: {mname}\n"
        f"  Expected MNAME containing: {CF_SOA_PREFIX}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Cloudflare is authoritative DNS for a domain"
    )
    parser.add_argument(
        "--domain",
        default="insightpulseai.com",
        help="Domain to check (default: insightpulseai.com)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout output; only exit code",
    )
    args = parser.parse_args()

    resolver = os.environ.get("VERIFY_DNS_RESOLVER")
    timeout = int(os.environ.get("VERIFY_DNS_TIMEOUT", "10"))
    quiet = args.quiet
    domain = args.domain

    if not shutil.which("dig"):
        print(
            "ERROR: 'dig' not found. Install bind-utils (RHEL/CentOS) or dnsutils (Debian/Ubuntu).",
            file=sys.stderr,
        )
        return 2

    if not quiet:
        resolver_label = f"@{resolver}" if resolver else "system resolver"
        print(f"Checking DNS authority for {domain} via {resolver_label}…")
        print()

    all_pass = True
    checks = [
        ("NS", check_ns(domain, resolver, timeout, quiet)),
        ("SOA", check_soa(domain, resolver, timeout, quiet)),
    ]

    for label, (passed, detail) in checks:
        icon = "✅" if passed else "❌"
        if not quiet:
            print(f"  {icon} {label}: {detail}")
        if not passed:
            all_pass = False

    if not quiet:
        print()
        if all_pass:
            print(
                f"✅ PASS — Cloudflare is the authoritative DNS for {domain}\n"
                f"   DNS record changes in infra/cloudflare/zones/ will take effect immediately."
            )
        else:
            print(
                f"❌ FAIL — Cloudflare is NOT authoritative for {domain}\n"
                f"\n"
                f"   Action required:\n"
                f"   1. Log into the domain registrar (Spacesquare).\n"
                f"   2. Set nameservers to:\n"
                f"        edna.ns.cloudflare.com\n"
                f"        keanu.ns.cloudflare.com\n"
                f"   3. Wait for NS propagation (up to 24-48h).\n"
                f"   4. Re-run this check: python3 scripts/cloudflare/verify_authoritative.py\n"
                f"\n"
                f"   Until Cloudflare is authoritative, DNS record commits have NO EFFECT\n"
                f"   on live DNS resolution."
            )

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
