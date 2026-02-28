#!/usr/bin/env python3
"""
check_canonical_urls.py -- Canonical URL SSOT consistency gate.

Validates infra/dns/canonical_urls.yaml against the following rules:

  1. Schema: every entry must have: url, lifecycle, runtime_class, backing, health_probe
  2. Lifecycle consistency: runtime_class=DEPLOYED must have lifecycle=active
  3. Lifecycle consistency: runtime_class=STAGED must have lifecycle=planned
  4. DEPLOYED entries must have backing != "none"
  5. All URLs must be https:// (no http)
  6. No duplicate URLs
  7. If runtime_class=DEPLOYED and backing=nginx_vhost, vhost_file field must be present
  8. Prints a summary table of all entries and their pass/fail status
  9. Exits 1 if any rule fails, 0 if all pass

Consumed by: .github/workflows/canonical-urls-gate.yml

Exit codes:
  0  all checks pass
  1  one or more validation rules failed
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "infra/dns/canonical_urls.yaml"

REQUIRED_FIELDS = {"url", "lifecycle", "runtime_class", "backing", "health_probe"}

_COL_URL = 48
_COL_RC = 10
_COL_LC = 10
_COL_BACKING = 14
_COL_STATUS = 6


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_yaml(p: Path) -> dict:
    if not p.exists():
        die(f"Missing required file: {p}")
    return yaml.safe_load(p.read_text()) or {}


def validate_entry(entry: dict, seen_urls: set) -> list:
    """Run all rules against a single entry. Returns a list of violation strings."""
    violations = []

    # Rule 1: required fields present
    missing = REQUIRED_FIELDS - entry.keys()
    if missing:
        violations.append(f"missing required fields: {sorted(missing)}")
        return violations

    lifecycle = entry["lifecycle"]
    runtime_class = entry["runtime_class"]
    backing = entry["backing"]
    url_val = entry["url"]

    # Rule 5: URL must be https
    if not url_val.startswith("https://"):
        violations.append(f"URL must start with https:// (got {url_val!r})")

    # Rule 6: no duplicate URLs
    if url_val in seen_urls:
        violations.append(f"duplicate URL: {url_val!r}")
    else:
        seen_urls.add(url_val)

    # Rule 2: DEPLOYED must have lifecycle=active
    if runtime_class == "DEPLOYED" and lifecycle != "active":
        violations.append(
            f"runtime_class=DEPLOYED requires lifecycle=active (got lifecycle={lifecycle!r})"
        )

    # Rule 3: STAGED must have lifecycle=planned
    if runtime_class == "STAGED" and lifecycle != "planned":
        violations.append(
            f"runtime_class=STAGED requires lifecycle=planned (got lifecycle={lifecycle!r})"
        )

    # Rule 4: DEPLOYED must have backing != none
    if runtime_class == "DEPLOYED" and backing == "none":
        violations.append(
            "runtime_class=DEPLOYED requires backing != none (got backing=none)"
        )

    # Rule 7: DEPLOYED + nginx_vhost requires vhost_file
    if runtime_class == "DEPLOYED" and backing == "nginx_vhost":
        if "vhost_file" not in entry:
            violations.append(
                "runtime_class=DEPLOYED with backing=nginx_vhost requires vhost_file field"
            )

    return violations


def _truncate(s: str, width: int) -> str:
    if len(s) <= width:
        return s
    return s[: width - 1] + "\u2026"


def print_summary_table(entries, violations_by_url):
    """Print a formatted summary table of all entries with PASS/FAIL status."""
    header = (
        f"{'URL':<{_COL_URL}}  "
        f"{'CLASS':<{_COL_RC}}  "
        f"{'LIFECYCLE':<{_COL_LC}}  "
        f"{'BACKING':<{_COL_BACKING}}  "
        f"{'STATUS':<{_COL_STATUS}}"
    )
    divider = "-" * len(header)
    print()
    print("Canonical URLs SSOT Validation Report")
    print("=" * len(header))
    print(header)
    print(divider)

    for entry in entries:
        url = entry.get("url", "<missing>")
        rc = entry.get("runtime_class", "?")
        lc = entry.get("lifecycle", "?")
        backing = entry.get("backing", "?")
        has_violations = bool(violations_by_url.get(url))
        status = "FAIL" if has_violations else "PASS"

        row = (
            f"{_truncate(url, _COL_URL):<{_COL_URL}}  "
            f"{_truncate(rc, _COL_RC):<{_COL_RC}}  "
            f"{_truncate(lc, _COL_LC):<{_COL_LC}}  "
            f"{_truncate(backing, _COL_BACKING):<{_COL_BACKING}}  "
            f"{status:<{_COL_STATUS}}"
        )
        print(row)

        if has_violations:
            for v in violations_by_url[url]:
                print(f"  -> {v}")

    print(divider)


def main() -> int:
    data = load_yaml(CANONICAL)

    if data.get("schema") != "ssot.canonical_urls.v1":
        die("canonical_urls.yaml must declare schema: ssot.canonical_urls.v1")

    entries = data.get("urls", [])
    if not isinstance(entries, list):
        die("canonical_urls.yaml: urls must be a list")

    seen_urls: set = set()
    violations_by_url: dict = {}
    all_violations: list = []

    for entry in entries:
        if not isinstance(entry, dict):
            print(f"ERROR: non-dict entry in urls list: {entry!r}", file=sys.stderr)
            all_violations.append("<non-dict entry>")
            continue

        url = entry.get("url", "<missing>")
        entry_violations = validate_entry(entry, seen_urls)
        if entry_violations:
            violations_by_url[url] = entry_violations
            all_violations.extend(entry_violations)

    print_summary_table(entries, violations_by_url)

    total = len(entries)
    failed = len(violations_by_url)
    passed = total - failed

    print()
    print(f"Entries: {total}  |  Passed: {passed}  |  Failed: {failed}")

    if all_violations:
        print(
            f"\nFAIL: {len(all_violations)} violation(s) found in "
            "infra/dns/canonical_urls.yaml",
            file=sys.stderr,
        )
        return 1

    print(f"\nOK: all {total} canonical URL entries pass SSOT validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
