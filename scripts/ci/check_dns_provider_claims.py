#!/usr/bin/env python3
"""
DNS Provider Claims Gate
========================
Fails CI if a DNS record is lifecycle=active and has an unclaimed provider_claim.

Rationale
---------
Some DNS records (e.g., Vercel CNAME) cannot resolve correctly until the
external provider claims the domain. Provisioning such a record before claiming
causes a dangling CNAME that returns NXDOMAIN-equivalent errors for users.

This gate enforces the rule:
  lifecycle=active + provider_claim.status=unclaimed → FAIL

Lifecycle state machine
-----------------------
  planned  →  Record defined in SSOT; Terraform SKIPS it.
              (safe to commit; no DNS change occurs)

  active   →  Terraform provisions/maintains the record.
              Only valid if there is no unclaimed provider_claim.

Transition path for Vercel custom domains
-----------------------------------------
1. Record is committed with lifecycle=planned + provider_claim.status=unclaimed.
2. Operator claims the domain in Vercel dashboard (Domains → Add custom domain).
3. Operator updates provider_claim.status to "claimed" in subdomain-registry.yaml.
4. Operator changes lifecycle to "active" in the same commit.
5. CI gate passes → PR merges → Terraform provisions the CNAME.

Exit codes
----------
  0  All checks passed.
  1  One or more unclaimed provider_claim entries found on active records.
  2  SSOT file not found or YAML parse error.

Usage
-----
  python3 scripts/ci/check_dns_provider_claims.py
  python3 scripts/ci/check_dns_provider_claims.py --ssot infra/dns/subdomain-registry.yaml

"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


SSOT_DEFAULT = "infra/dns/subdomain-registry.yaml"


def check_file(path: str) -> list[tuple[str, str, str]]:
    """Return list of (file, record_name, reason) for failing records."""
    failures: list[tuple[str, str, str]] = []

    try:
        with open(path, "r") as fh:
            doc = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        print(f"ERROR: SSOT file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error in {path}: {exc}", file=sys.stderr)
        sys.exit(2)

    subdomains = doc.get("subdomains") or []

    for record in subdomains:
        name = record.get("name", "<unknown>")
        lifecycle = record.get("lifecycle", "active")  # default=active for backward compat
        claim = record.get("provider_claim")

        # Skip non-active records — they are intentionally not provisioned
        if lifecycle != "active":
            continue

        # No provider_claim → nothing to validate
        if not claim:
            continue

        provider = claim.get("provider", "<unknown>")
        domain = claim.get("domain", "<unknown>")
        status = claim.get("status", "unclaimed")

        if status != "claimed":
            failures.append((
                path,
                name,
                f"provider={provider} domain={domain} claim_status={status} (must be 'claimed' before lifecycle=active)"
            ))

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--ssot",
        default=None,
        help=f"Path to SSOT YAML (default: {SSOT_DEFAULT}, or all infra/dns/**/*.yaml if not specified)",
    )
    args = parser.parse_args(argv)

    if args.ssot:
        ssot_files = [args.ssot]
    else:
        ssot_files = glob.glob("infra/dns/**/*.yaml", recursive=True) + \
                     glob.glob("infra/dns/**/*.yml", recursive=True)

    if not ssot_files:
        print(f"WARNING: No SSOT files found matching infra/dns/**/*.yaml", file=sys.stderr)
        return 0

    all_failures: list[tuple[str, str, str]] = []
    for path in sorted(ssot_files):
        all_failures.extend(check_file(path))

    if all_failures:
        print("\n[FAIL] DNS provider claim gate — unclaimed active records detected:\n")
        for fpath, record_name, reason in all_failures:
            print(f"  {fpath}  record={record_name}")
            print(f"    {reason}")
        print()
        print("Remediation: Either set lifecycle=planned until the domain is claimed,")
        print("or update provider_claim.status to 'claimed' after claiming the domain")
        print("in the provider dashboard (Vercel → Domains → Add custom domain).")
        return 1

    print("[PASS] DNS provider claim gate — all active records have valid provider claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
