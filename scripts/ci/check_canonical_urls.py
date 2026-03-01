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
  6. docs/architecture/CANONICAL_URLS.md must not introduce URLs absent from YAML
     (Markdown is documentation-only; infra/dns/canonical_urls.yaml is SSOT).

Exit codes:
  0  all checks pass
  1  validation errors (structural / invariant)
  2  expired planned entry (deadline passed)
  5  Markdown introduces a URL not present in SSOT YAML
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "infra/dns/canonical_urls.yaml"
CANON_MD = ROOT / "docs/architecture/CANONICAL_URLS.md"

REQUIRED_FIELDS = {"url", "lifecycle", "runtime_class", "backing", "health_probe"}
VALID_LIFECYCLES = {"active", "planned", "broken", "deprecated"}
VALID_CLASSES = {"DEPLOYED", "REDIRECT", "STAGED", "BROKEN"}

# Matches https?://... URLs in Markdown.
# Stops at whitespace, ), ], ', ", >, backtick, or end-of-line.
_URL_RE = re.compile(r'https?://[^\s\)\]\'\"`>]+')


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


def _extract_md_urls(md_path: Path) -> set[str]:
    """Return the set of https?:// URLs that appear in the Markdown file."""
    if not md_path.exists():
        return set()
    text = md_path.read_text()
    raw = set(_URL_RE.findall(text))
    # Normalise: strip trailing punctuation artefacts left by the regex
    cleaned: set[str] = set()
    for u in raw:
        u = u.rstrip(".,;:")
        # Skip wildcard URLs — they are pattern references, not real entries
        if "*" in u:
            continue
        cleaned.add(u)
    return cleaned


def check_markdown_drift(yaml_urls: set[str], md_drift: list[str]) -> None:
    """Rule 6: Markdown must not introduce URLs absent from the YAML SSOT."""
    if not CANON_MD.exists():
        return  # Markdown is optional — absence is not an error

    md_urls = _extract_md_urls(CANON_MD)

    # We only care about subdomain URLs (not the apex domain itself)
    # Apex https://insightpulseai.com is not tracked as a subdomain registry entry
    domain = "insightpulseai.com"
    md_domain_urls = {
        u for u in md_urls
        if domain in u
        and not u.rstrip("/") in (f"https://{domain}", f"http://{domain}")
    }
    yaml_domain_urls = {u for u in yaml_urls if domain in u}

    offenders = sorted(md_domain_urls - yaml_domain_urls)
    if offenders:
        md_drift.extend(
            [
                "Markdown introduces URLs not present in infra/dns/canonical_urls.yaml.",
                "Add them to the YAML first, then update the Markdown:",
            ]
            + [f"  - {u}" for u in offenders]
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
    md_drift: list[str] = []

    yaml_urls = {e["url"] for e in entries if isinstance(e, dict) and "url" in e}

    for entry in entries:
        check_entry(entry, errors)
        check_expires(entry, expired)

    check_markdown_drift(yaml_urls, md_drift)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)

    if expired:
        for e in expired:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)

    if md_drift:
        for e in md_drift:
            print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(5)

    print(f"OK: {len(entries)} URL entries validated — lifecycle/runtime_class invariants pass, Markdown not drifted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
