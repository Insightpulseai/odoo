#!/usr/bin/env python3
"""
DNS Provider Claims Gate (schema: ssot.dns.provider_claim.v1)
=============================================================
Enforces the DNS lifecycle state machine by validating all subdomain records
in infra/dns/subdomain-registry.yaml against these rules:

  lifecycle=active  → provider_claim MUST be present with:
                        provider   ∈ {cloudflare, vercel, digitalocean, other}
                        status     == "claimed"
                        claimed_at == YYYY-MM-DD (required)
                        claim_ref  != "" (required, non-empty)

  lifecycle=planned → provider_claim is optional.
                      If present and expires_at is set and in the past → FAIL.
                      (Forces resolution of stale planned records.)

  No lifecycle set  → treated as "active" for backward compatibility.

Exit codes
----------
  0  All checks passed.
  1  One or more validation failures found.
  2  SSOT file not found or YAML/date parse error.

State machine
-------------
  planned (unclaimed)
      ↓  operator claims domain in provider dashboard
      ↓  commits: status=claimed, claimed_at=<date>, claim_ref=<id>, lifecycle=active
  active  (claimed)
      ↓  record is provisioned by Terraform on merge

To operate: python3 scripts/ci/check_dns_provider_claims.py [--ssot PATH]
"""

from __future__ import annotations

import argparse
import glob
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed — run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ─── Allowed enumerations ────────────────────────────────────────────────────

ALLOWED_PROVIDERS = {"cloudflare", "vercel", "digitalocean", "other"}
ALLOWED_STATUSES  = {"unclaimed", "claimed"}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def parse_date(value: Any, field: str, record_name: str) -> date | None:
    """Parse a YYYY-MM-DD string to date; emit error and exit on bad format."""
    if value is None:
        return None
    try:
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        print(
            f"ERROR: {field}={value!r} on record '{record_name}' is not a valid YYYY-MM-DD date.",
            file=sys.stderr,
        )
        sys.exit(2)


# ─── Validation ──────────────────────────────────────────────────────────────

Failure = tuple[str, str, str]  # (ssot_file, record_name, message)


def validate_record(
    record: dict,
    ssot_path: str,
    today: date,
) -> list[Failure]:
    """Return a list of (ssot_path, record_name, error_message) for this record."""
    failures: list[Failure] = []
    name = record.get("name", "<unnamed>")

    lifecycle = record.get("lifecycle", "active")  # backward-compat default
    claim: dict | None = record.get("provider_claim")

    # ── active records ───────────────────────────────────────────────────────
    if lifecycle == "active":
        if not claim:
            failures.append((ssot_path, name,
                "lifecycle=active requires a provider_claim block"))
            return failures  # can't validate further without claim

        # provider enum
        provider = claim.get("provider")
        if provider not in ALLOWED_PROVIDERS:
            failures.append((ssot_path, name,
                f"provider_claim.provider={provider!r} is not in {sorted(ALLOWED_PROVIDERS)}"))

        # status must be "claimed"
        status = claim.get("status")
        if status not in ALLOWED_STATUSES:
            failures.append((ssot_path, name,
                f"provider_claim.status={status!r} is not in {sorted(ALLOWED_STATUSES)}"))
        elif status != "claimed":
            failures.append((ssot_path, name,
                f"lifecycle=active requires provider_claim.status='claimed', got {status!r}. "
                "Set lifecycle=planned until the domain is claimed."))

        # claimed_at — required when status=claimed
        if status == "claimed" or status is None:
            claimed_at_raw = claim.get("claimed_at")
            if not claimed_at_raw:
                failures.append((ssot_path, name,
                    "provider_claim.claimed_at is required when status=claimed (format: YYYY-MM-DD)"))
            else:
                parse_date(claimed_at_raw, "claimed_at", name)  # validates format

            # claim_ref — required when status=claimed
            claim_ref = claim.get("claim_ref", "")
            if not str(claim_ref).strip():
                failures.append((ssot_path, name,
                    "provider_claim.claim_ref is required when status=claimed "
                    "(e.g. 'ssot:cloudflare', 'vercel:prj_<id>')"))

    # ── planned records ──────────────────────────────────────────────────────
    elif lifecycle == "planned":
        if not claim:
            # no claim block on planned → OK (not enforced for planned)
            return failures

        provider = claim.get("provider")
        if provider is not None and provider not in ALLOWED_PROVIDERS:
            failures.append((ssot_path, name,
                f"provider_claim.provider={provider!r} is not in {sorted(ALLOWED_PROVIDERS)}"))

        status = claim.get("status")
        if status is not None and status not in ALLOWED_STATUSES:
            failures.append((ssot_path, name,
                f"provider_claim.status={status!r} is not in {sorted(ALLOWED_STATUSES)}"))

        # expiry enforcement
        expires_at_raw = claim.get("expires_at")
        if expires_at_raw:
            expires_at = parse_date(expires_at_raw, "expires_at", name)
            if expires_at and expires_at < today:
                failures.append((ssot_path, name,
                    f"lifecycle=planned has expired (expires_at={expires_at_raw}, today={today}). "
                    "Resolve: claim the domain and transition to active, or remove/extend expires_at."))

    return failures


def check_file(ssot_path: str, today: date) -> tuple[list[Failure], dict[str, dict]]:
    """
    Validate all subdomains in a SSOT file.
    Returns (failures, stats) where stats = counts by lifecycle × claim_status.
    """
    try:
        with open(ssot_path) as fh:
            doc = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        print(f"ERROR: SSOT file not found: {ssot_path}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error in {ssot_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    subdomains = doc.get("subdomains") or []
    failures: list[Failure] = []

    # counters for summary table
    stats: dict[str, dict] = {
        "active":  {"claimed": 0, "unclaimed": 0, "missing": 0},
        "planned": {"claimed": 0, "unclaimed": 0, "missing": 0},
    }

    for record in subdomains:
        lc   = record.get("lifecycle", "active")
        claim = record.get("provider_claim") or {}
        st   = claim.get("status", "_missing") if record.get("provider_claim") else "_missing"

        bucket = "active" if lc == "active" else "planned"
        if st == "claimed":
            stats[bucket]["claimed"] += 1
        elif st == "unclaimed":
            stats[bucket]["unclaimed"] += 1
        else:
            stats[bucket]["missing"] += 1

        failures.extend(validate_record(record, ssot_path, today))

    return failures, stats


# ─── Summary ─────────────────────────────────────────────────────────────────

def print_summary(stats: dict[str, dict], ssot_path: str) -> None:
    total = sum(v for lc in stats.values() for v in lc.values())
    print(f"\n{'─'*62}")
    print(f"  DNS provider-claim summary  │  {ssot_path}")
    print(f"{'─'*62}")
    print(f"  {'lifecycle':<10}  {'claimed':>8}  {'unclaimed':>10}  {'no claim':>9}")
    print(f"  {'─'*10}  {'─'*8}  {'─'*10}  {'─'*9}")
    for lc, counts in stats.items():
        print(
            f"  {lc:<10}  {counts['claimed']:>8}  {counts['unclaimed']:>10}  {counts['missing']:>9}"
        )
    print(f"  {'─'*10}  {'─'*8}  {'─'*10}  {'─'*9}")
    print(f"  {'total':<10}  {sum(v['claimed'] for v in stats.values()):>8}  "
          f"{sum(v['unclaimed'] for v in stats.values()):>10}  "
          f"{sum(v['missing'] for v in stats.values()):>9}")
    print(f"{'─'*62}\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--ssot",
        default=None,
        help="Path to SSOT YAML (default: scan infra/dns/**/*.yaml)",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Override today's date (YYYY-MM-DD) — for testing expiry logic.",
    )
    args = parser.parse_args(argv)

    today: date
    if args.today:
        try:
            today = datetime.strptime(args.today, "%Y-%m-%d").date()
        except ValueError:
            print(f"ERROR: --today must be YYYY-MM-DD, got {args.today!r}", file=sys.stderr)
            sys.exit(2)
    else:
        today = date.today()

    ssot_files: list[str]
    if args.ssot:
        ssot_files = [args.ssot]
    else:
        ssot_files = sorted(
            glob.glob("infra/dns/**/*.yaml", recursive=True)
            + glob.glob("infra/dns/**/*.yml", recursive=True)
        )

    if not ssot_files:
        print("WARNING: No SSOT files found under infra/dns/ — nothing to validate.",
              file=sys.stderr)
        return 0

    all_failures: list[Failure] = []
    for path in ssot_files:
        failures, stats = check_file(path, today)
        print_summary(stats, path)
        all_failures.extend(failures)

    if all_failures:
        print(f"[FAIL] {len(all_failures)} validation error(s) found:\n")
        for ssot_path, record_name, msg in all_failures:
            print(f"  record: {record_name}")
            print(f"  file:   {ssot_path}")
            print(f"  error:  {msg}")
            print()
        print("Remediation:")
        print("  • active + unclaimed  → set lifecycle=planned until domain is claimed")
        print("  • active, no claim    → add provider_claim block with status=claimed + claimed_at + claim_ref")
        print("  • planned, expired    → resolve claim and set lifecycle=active, or extend/remove expires_at")
        return 1

    print(f"[PASS] DNS provider claim gate — {len(ssot_files)} file(s) validated, 0 failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
