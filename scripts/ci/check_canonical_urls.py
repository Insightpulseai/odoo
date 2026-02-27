#!/usr/bin/env python3
"""
check_canonical_urls.py — Canonical URL SSOT consistency gate.

Rules enforced:
  1. active lifecycle requires backing != "none" AND health_probe defined.
  2. DEPLOYED runtime_class implies lifecycle == "active".
  3. BROKEN runtime_class cannot have lifecycle == "active"
     (must be "planned" or carry explicit activation_criteria).
  4. planned entries with an expires_at in the past fail (prevent limbo).
  5. All URLs must have url, lifecycle, runtime_class, backing, health_probe.

Exit codes:
  0  all checks pass
  1  validation errors (structural / invariant)
  2  expired planned entry (deadline passed)
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "infra/dns/canonical_urls.yaml"

REQUIRED_FIELDS = {"url", "lifecycle", "runtime_class", "backing", "health_probe"}
VALID_LIFECYCLES = {"active", "planned", "broken", "deprecated"}
VALID_CLASSES = {"DEPLOYED", "REDIRECT", "STAGED", "BROKEN"}


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_yaml(p: Path) -> dict:
    if not p.exists():
        die(f"Missing required file: {p}")
    return yaml.safe_load(p.read_text()) or {}


def check_entry(entry: dict[str, Any], errors: list[str]) -> None:
    url = entry.get("url", "<missing url>")

    # Rule 0: required fields present
    missing = REQUIRED_FIELDS - entry.keys()
    if missing:
        errors.append(f"{url}: missing required fields: {sorted(missing)}")
        return  # skip further checks if fundamental fields absent

    lifecycle = entry["lifecycle"]
    runtime_class = entry["runtime_class"]
    backing = entry["backing"]
    health_probe = entry.get("health_probe")

    # Rule 1: active requires backing != none AND health_probe
    if lifecycle == "active":
        if backing == "none":
            errors.append(
                f"{url}: lifecycle=active but backing=none "
                f"(must wire nginx_vhost, platform, or direct before activating)"
            )
        if not health_probe:
            errors.append(f"{url}: lifecycle=active but health_probe is missing")

    # Rule 2: DEPLOYED implies active
    if runtime_class == "DEPLOYED" and lifecycle != "active":
        errors.append(
            f"{url}: runtime_class=DEPLOYED requires lifecycle=active (got '{lifecycle}')"
        )

    # Rule 3: BROKEN cannot be active
    if runtime_class == "BROKEN" and lifecycle == "active":
        errors.append(
            f"{url}: runtime_class=BROKEN with lifecycle=active is contradictory — "
            f"set lifecycle=planned and document activation_criteria"
        )

    # Rule 4: Validate lifecycle and runtime_class values are known
    if lifecycle not in VALID_LIFECYCLES:
        errors.append(f"{url}: unknown lifecycle '{lifecycle}' (valid: {sorted(VALID_LIFECYCLES)})")
    if runtime_class not in VALID_CLASSES:
        errors.append(f"{url}: unknown runtime_class '{runtime_class}' (valid: {sorted(VALID_CLASSES)})")


def check_expires(entry: dict[str, Any], expired: list[str]) -> None:
    """Emit expiry errors for planned entries past their deadline."""
    url = entry.get("url", "<missing url>")
    expires_at = entry.get("expires_at")
    if not expires_at:
        return
    try:
        deadline = date.fromisoformat(str(expires_at))
    except ValueError:
        expired.append(f"{url}: invalid expires_at format '{expires_at}' (expected YYYY-MM-DD)")
        return
    if deadline < date.today():
        expired.append(
            f"{url}: planned entry expired on {expires_at} — "
            f"resolve activation_criteria or remove from SSOT"
        )


def main() -> int:
    data = load_yaml(CANONICAL)

    if data.get("schema") != "ssot.canonical_urls.v1":
        die("canonical_urls.yaml must declare schema: ssot.canonical_urls.v1")

    entries = data.get("urls", [])
    if not isinstance(entries, list):
        die("canonical_urls.yaml: 'urls' must be a list")

    errors: list[str] = []
    expired: list[str] = []

    for entry in entries:
        check_entry(entry, errors)
        check_expires(entry, expired)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)

    if expired:
        for e in expired:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)

    print(f"OK: {len(entries)} URL entries validated — all lifecycle/runtime_class invariants pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
