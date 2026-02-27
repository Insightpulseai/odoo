#!/usr/bin/env python3
"""
apply_dns_from_yaml.py — Idempotent Cloudflare DNS SSOT apply.

Reads infra/dns/<yaml_file> and upserts TXT/MX records via Cloudflare API.
Safe to re-run: creates missing records, updates drifted records, skips
records that already match. Never deletes records.

Usage:
    python3 infra/cloudflare/scripts/apply_dns_from_yaml.py
    python3 infra/cloudflare/scripts/apply_dns_from_yaml.py --file infra/dns/zoho_mail_dns.yaml
    python3 infra/cloudflare/scripts/apply_dns_from_yaml.py --dry-run
    python3 infra/cloudflare/scripts/apply_dns_from_yaml.py --verify

Environment variables (required unless --verify):
    CLOUDFLARE_API_TOKEN  — zone:dns_records:edit permission
    CLOUDFLARE_ZONE_ID    — zone ID for insightpulseai.com
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_YAML = REPO_ROOT / "infra" / "dns" / "zoho_mail_dns.yaml"

CF_API = "https://api.cloudflare.com/client/v4"


# ---------------------------------------------------------------------------
# Cloudflare API helpers
# ---------------------------------------------------------------------------

def _cf_request(method: str, path: str, token: str, body: dict | None = None) -> dict:
    url = f"{CF_API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        print(f"ERROR: Cloudflare API {method} {path} → HTTP {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)


def list_dns_records(zone_id: str, token: str, rtype: str, name: str) -> list[dict]:
    """Return all existing DNS records matching type + name."""
    path = f"/zones/{zone_id}/dns_records?type={rtype}&name={name}&per_page=100"
    resp = _cf_request("GET", path, token)
    return resp.get("result", [])


def create_record(zone_id: str, token: str, record: dict) -> dict:
    path = f"/zones/{zone_id}/dns_records"
    return _cf_request("POST", path, token, record)


def update_record(zone_id: str, token: str, record_id: str, record: dict) -> dict:
    path = f"/zones/{zone_id}/dns_records/{record_id}"
    return _cf_request("PUT", path, token, record)


# ---------------------------------------------------------------------------
# YAML parsing
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> list[dict]:
    """Return list of record dicts from SSOT YAML.

    Supports two formats:
      Legacy:  domain: insightpulseai.com  + records: [...]
      Current: zone: {name: insightpulseai.com, id: ..., ...}  + records: [...]
    """
    with open(path) as f:
        doc = yaml.safe_load(f)
    # Support both "domain:" (legacy zoho_mail_dns.yaml) and "zone.name:" (insightpulseai.com/records.yaml)
    if "domain" in doc:
        domain = doc["domain"]
    elif "zone" in doc and "name" in doc["zone"]:
        domain = doc["zone"]["name"]
    else:
        raise KeyError(
            "YAML must have 'domain: <name>' or 'zone: {name: <name>}' at top level"
        )
    records = []
    for r in doc["records"]:
        rec = {
            "type": r["type"],
            "name": _resolve_name(r["name"], domain),
            "content": r["content"],
            "ttl": r.get("ttl", 3600),
        }
        if "priority" in r:
            rec["priority"] = r["priority"]
        records.append(rec)
    return records


def _resolve_name(name: str, domain: str) -> str:
    """Convert '@' → domain, 'sub' → 'sub.domain', 'sub.domain' → as-is."""
    if name == "@":
        return domain
    if "." not in name:
        return f"{name}.{domain}"
    return name


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------

def _record_fingerprint(r: dict) -> str:
    """Stable hash of the fields we care about for drift detection."""
    sig = f"{r['type']}:{r['name']}:{r['content']}:{r.get('priority', '')}"
    return hashlib.md5(sig.encode()).hexdigest()


def _safe_preview(content: str, max_len: int = 40) -> str:
    """Show a safe preview of a record value (avoids printing full DKIM key)."""
    if len(content) > max_len:
        return f"{content[:max_len]}… ({len(content)} chars)"
    return content


# ---------------------------------------------------------------------------
# Apply logic
# ---------------------------------------------------------------------------

def apply(records: list[dict], zone_id: str, token: str, dry_run: bool) -> dict:
    counts = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    for desired in records:
        rtype = desired["type"]
        name = desired["name"]
        existing = list_dns_records(zone_id, token, rtype, name)

        preview = _safe_preview(desired["content"])

        if not existing:
            # Create
            if dry_run:
                print(f"  [DRY-RUN] CREATE {rtype} {name} → {preview}")
            else:
                result = create_record(zone_id, token, desired)
                if result.get("success"):
                    print(f"  ✅ CREATED {rtype} {name} → {preview}")
                    counts["created"] += 1
                else:
                    print(f"  ❌ CREATE FAILED {rtype} {name}: {result.get('errors')}")
                    counts["errors"] += 1
        else:
            # For MX: match by content (multiple MX records exist per domain)
            # For TXT: match by name (may have multiple, find ours by content prefix)
            matched = _find_match(existing, desired)

            if matched:
                if _record_fingerprint(desired) == _record_fingerprint(_normalize(matched)):
                    print(f"  ⏭  NO-OP   {rtype} {name} → {preview}")
                    counts["skipped"] += 1
                else:
                    if dry_run:
                        print(f"  [DRY-RUN] UPDATE {rtype} {name} → {preview}")
                    else:
                        result = update_record(zone_id, token, matched["id"], desired)
                        if result.get("success"):
                            print(f"  ✅ UPDATED {rtype} {name} → {preview}")
                            counts["updated"] += 1
                        else:
                            print(f"  ❌ UPDATE FAILED {rtype} {name}: {result.get('errors')}")
                            counts["errors"] += 1
            else:
                # No matching record found for this content — create
                if dry_run:
                    print(f"  [DRY-RUN] CREATE {rtype} {name} → {preview}")
                else:
                    result = create_record(zone_id, token, desired)
                    if result.get("success"):
                        print(f"  ✅ CREATED {rtype} {name} → {preview}")
                        counts["created"] += 1
                    else:
                        print(f"  ❌ CREATE FAILED {rtype} {name}: {result.get('errors')}")
                        counts["errors"] += 1

    return counts


def _find_match(existing: list[dict], desired: dict) -> dict | None:
    """Find an existing record that best matches our desired record."""
    rtype = desired["type"]
    if rtype == "MX":
        # Match by content (each MX record has unique content)
        for r in existing:
            if r.get("content", "").lower() == desired["content"].lower():
                return r
    elif rtype == "TXT":
        # Match by content prefix (first 20 chars) — handles DKIM, SPF, DMARC
        prefix = desired["content"][:20].lower()
        for r in existing:
            if r.get("content", "")[:20].lower() == prefix:
                return r
    return None


def _normalize(cf_record: dict) -> dict:
    """Extract just the fields we compare for drift detection."""
    return {
        "type": cf_record["type"],
        "name": cf_record["name"],
        "content": cf_record.get("content", ""),
        "priority": cf_record.get("priority", ""),
    }


# ---------------------------------------------------------------------------
# Verify mode (read-only DNS query)
# ---------------------------------------------------------------------------

def verify(records: list[dict], zone_id: str, token: str) -> None:
    print("Verifying DNS records via Cloudflare API...")
    all_ok = True
    for desired in records:
        rtype = desired["type"]
        name = desired["name"]
        existing = list_dns_records(zone_id, token, rtype, name)
        matched = _find_match(existing, desired)
        preview = _safe_preview(desired["content"])
        if matched:
            print(f"  ✅ {rtype:<5} {name:<40} → {preview}")
        else:
            print(f"  ❌ {rtype:<5} {name:<40} → MISSING (expected: {preview})")
            all_ok = False
    if not all_ok:
        print("\nVerification FAILED — run without --verify to apply missing records.")
        sys.exit(1)
    print("\nAll records verified. ✅")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="Apply DNS SSOT YAML to Cloudflare")
    p.add_argument("--file", default=str(DEFAULT_YAML),
                   help=f"SSOT YAML file (default: {DEFAULT_YAML})")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would change without applying")
    p.add_argument("--verify", action="store_true",
                   help="Read-only: check if records exist in Cloudflare")
    args = p.parse_args()

    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    zone_id = os.environ.get("CLOUDFLARE_ZONE_ID", "")

    if not token or not zone_id:
        print("ERROR: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID must be set", file=sys.stderr)
        sys.exit(1)

    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"ERROR: YAML file not found: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    records = load_yaml(yaml_path)
    print(f"Loaded {len(records)} records from {yaml_path.name}")
    print(f"Zone: {zone_id[:8]}… | Token: {token[:8]}…")
    print()

    if args.verify:
        verify(records, zone_id, token)
        return 0

    if args.dry_run:
        print("--- DRY RUN (no changes will be made) ---")

    counts = apply(records, zone_id, token, dry_run=args.dry_run)
    print()
    print(f"Summary: created={counts['created']} updated={counts['updated']} "
          f"skipped={counts['skipped']} errors={counts['errors']}")
    return 1 if counts["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
