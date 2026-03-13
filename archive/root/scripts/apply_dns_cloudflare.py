#!/usr/bin/env python3
# scripts/apply_dns_cloudflare.py
#
# Idempotently upserts DNS records to Cloudflare from artifacts/dns/cloudflare_records.json.
# Records are created if missing; updated if content differs; skipped if identical.
#
# Required env vars:
#   CF_API_TOKEN   — Cloudflare API token (Zone:DNS:Edit permission)
#   CF_ZONE_NAME   — zone to operate on (e.g. insightpulseai.com); auto-derived from JSON if omitted
#
# Usage:
#   CF_API_TOKEN=... python3 scripts/apply_dns_cloudflare.py
#   CF_API_TOKEN=... python3 scripts/apply_dns_cloudflare.py --dry-run
#   CF_API_TOKEN=... python3 scripts/apply_dns_cloudflare.py --input infra/dns/custom.json

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

CF_API_BASE = "https://api.cloudflare.com/client/v4"


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def _cf_request(method: str, path: str, token: str, data: dict | None = None) -> dict:
    url = f"{CF_API_BASE}{path}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        print(f"  ❌ HTTP {exc.code} {method} {url}", file=sys.stderr)
        print(f"     {body_text[:400]}", file=sys.stderr)
        sys.exit(1)


def get_zone_id(token: str, zone_name: str) -> str:
    resp = _cf_request("GET", f"/zones?name={zone_name}&status=active", token)
    zones = resp.get("result", [])
    if not zones:
        print(f"❌ Zone '{zone_name}' not found or token has no access.", file=sys.stderr)
        sys.exit(1)
    return zones[0]["id"]


def list_records(token: str, zone_id: str, rtype: str, name: str) -> list[dict]:
    resp = _cf_request("GET", f"/zones/{zone_id}/dns_records?type={rtype}&name={name}", token)
    return resp.get("result", [])


def create_record(token: str, zone_id: str, payload: dict) -> dict:
    return _cf_request("POST", f"/zones/{zone_id}/dns_records", token, payload)


def update_record(token: str, zone_id: str, record_id: str, payload: dict) -> dict:
    return _cf_request("PATCH", f"/zones/{zone_id}/dns_records/{record_id}", token, payload)


# ── Core logic ─────────────────────────────────────────────────────────────────

def fqdn(name: str, zone: str) -> str:
    """Return fully-qualified name for Cloudflare API queries."""
    if name == "@" or name == zone:
        return zone
    if name.endswith(f".{zone}") or name == zone:
        return name
    return f"{name}.{zone}"


def upsert_record(token: str, zone_id: str, zone: str, rec: dict, dry_run: bool) -> str:
    """
    Upsert a single record. Returns 'created', 'updated', or 'ok'.
    """
    rtype   = rec["type"]
    name    = rec["name"]
    content = rec["content"]
    ttl     = rec.get("ttl", 3600)
    proxied = rec.get("proxied", False)

    full_name = fqdn(name, zone)

    existing = list_records(token, zone_id, rtype, full_name)

    payload: dict = {"type": rtype, "name": name, "content": content, "ttl": ttl}
    if rtype == "CNAME":
        payload["proxied"] = False  # email CNAMEs must NOT be proxied

    if not existing:
        if dry_run:
            print(f"  [DRY-RUN] CREATE {rtype} {full_name} → {content[:60]}")
            return "created"
        result = create_record(token, zone_id, payload)
        if result.get("success"):
            print(f"  ✅ CREATED  {rtype} {full_name} → {content[:60]}")
            return "created"
        else:
            print(f"  ❌ CREATE failed: {result.get('errors')}", file=sys.stderr)
            sys.exit(1)
    else:
        # Check if content matches
        existing_rec = existing[0]
        if existing_rec.get("content") == content:
            print(f"  ⚡ OK       {rtype} {full_name} (no change)")
            return "ok"
        if dry_run:
            print(f"  [DRY-RUN] UPDATE {rtype} {full_name}")
            print(f"             old: {existing_rec.get('content')[:60]}")
            print(f"             new: {content[:60]}")
            return "updated"
        result = update_record(token, zone_id, existing_rec["id"], payload)
        if result.get("success"):
            print(f"  ✅ UPDATED  {rtype} {full_name}")
            return "updated"
        else:
            print(f"  ❌ UPDATE failed: {result.get('errors')}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upsert DNS records to Cloudflare from JSON artifact")
    parser.add_argument("--input", default="artifacts/dns/cloudflare_records.json",
                        help="Path to cloudflare_records.json (default: artifacts/dns/cloudflare_records.json)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without making API calls")
    args = parser.parse_args()

    # Secrets from env
    token = os.environ.get("CF_API_TOKEN", "")
    if not token:
        print("❌ CF_API_TOKEN env var is required.", file=sys.stderr)
        sys.exit(1)

    # Load artifact
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}", file=sys.stderr)
        print("   Run scripts/generate-dns-artifacts.sh first.", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        artifact = json.load(f)

    zone      = os.environ.get("CF_ZONE_NAME", "") or artifact.get("zone", "")
    records   = artifact.get("records", [])

    if not zone:
        print("❌ CF_ZONE_NAME env var or 'zone' key in JSON is required.", file=sys.stderr)
        sys.exit(1)
    if not records:
        print("⚠️  No records found in artifact — nothing to apply.")
        sys.exit(0)

    print(f"▶ Cloudflare DNS apply — zone: {zone} — {len(records)} record(s)")
    if args.dry_run:
        print("  (dry-run mode: no changes will be made)")

    # Resolve zone ID
    zone_id = get_zone_id(token, zone)
    print(f"  zone_id: {zone_id}")

    # Upsert each record
    counts = {"created": 0, "updated": 0, "ok": 0}
    for rec in records:
        status = upsert_record(token, zone_id, zone, rec, args.dry_run)
        counts[status] += 1

    print(f"\n▶ Summary: {counts['created']} created, {counts['updated']} updated, {counts['ok']} unchanged")
    if counts["created"] > 0 or counts["updated"] > 0:
        print("  ⏳ DNS propagation: allow up to 5 min before running verify_mailgun_domain.py")


if __name__ == "__main__":
    main()
