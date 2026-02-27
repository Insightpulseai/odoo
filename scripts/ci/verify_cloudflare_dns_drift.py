#!/usr/bin/env python3
"""
verify_cloudflare_dns_drift.py
─────────────────────────────
Compare the Cloudflare DNS SSOT YAML against live Cloudflare zone records.

Exit codes:
  0  No drift — SSOT matches live DNS
  1  Drift detected — records differ; see diff output
  2  Error — missing env vars, API failure, parse error

Usage:
  python3 scripts/ci/verify_cloudflare_dns_drift.py

Required env vars:
  CF_API_TOKEN   Cloudflare API token with Zone:DNS:Read permission
                 (read-only; never write access for this script)

Optional env vars:
  SSOT_FILE      Path to SSOT YAML (default: infra/cloudflare/insightpulseai.com.records.yaml)
  CF_ZONE_ID     Override zone ID from SSOT (useful in CI)
"""

import json
import os
import sys
import urllib.request
import urllib.error

try:
    import yaml  # PyYAML
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SSOT = os.path.join(REPO_ROOT, "infra", "cloudflare", "insightpulseai.com.records.yaml")
CF_API_BASE = "https://api.cloudflare.com/client/v4"


def load_ssot(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def cf_request(path: str, token: str) -> dict:
    url = f"{CF_API_BASE}{path}?per_page=200"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: Cloudflare API {e.code}: {body}", file=sys.stderr)
        sys.exit(2)


def normalize_record(r: dict) -> dict:
    """Normalize a Cloudflare API record to a comparable shape."""
    return {
        "type": r.get("type", "").upper(),
        "name": r.get("name", "").lower().rstrip("."),
        "content": r.get("content", "").strip('"').strip(),
        "proxied": r.get("proxied", False),
        "priority": r.get("priority"),  # MX only
    }


def normalize_ssot_record(r: dict, zone_name: str) -> dict:
    """Normalize an SSOT YAML record to the same comparable shape."""
    name = r.get("name", "").lower()
    # Expand "@" to the zone name
    if name == "@":
        name = zone_name
    elif not name.endswith(zone_name):
        name = f"{name}.{zone_name}"
    return {
        "type": r.get("type", "").upper(),
        "name": name,
        "content": r.get("content", "").strip('"').strip(),
        "proxied": r.get("proxied", False),
        "priority": r.get("priority"),
    }


def record_key(r: dict) -> str:
    parts = [r["type"], r["name"], r["content"]]
    if r.get("priority") is not None:
        parts.append(str(r["priority"]))
    return "|".join(parts)


def main() -> int:
    token = os.environ.get("CF_API_TOKEN")
    if not token:
        print("ERROR: CF_API_TOKEN env var is required (read-only DNS token).", file=sys.stderr)
        return 2

    ssot_path = os.environ.get("SSOT_FILE", DEFAULT_SSOT)
    if not os.path.exists(ssot_path):
        print(f"ERROR: SSOT file not found: {ssot_path}", file=sys.stderr)
        return 2

    ssot = load_ssot(ssot_path)
    zone_id = os.environ.get("CF_ZONE_ID") or ssot.get("zone", {}).get("id")
    zone_name = ssot.get("zone", {}).get("name", "")

    if not zone_id:
        print("ERROR: zone.id not found in SSOT YAML and CF_ZONE_ID not set.", file=sys.stderr)
        return 2

    print(f"Checking zone: {zone_name} ({zone_id})")
    print(f"SSOT file: {ssot_path}")

    # Fetch live records
    resp = cf_request(f"/zones/{zone_id}/dns_records", token)
    if not resp.get("success"):
        print(f"ERROR: Cloudflare API error: {resp}", file=sys.stderr)
        return 2

    live_records = {record_key(normalize_record(r)): r for r in resp.get("result", [])}

    # Build SSOT record set
    ssot_records = {}
    for r in ssot.get("records", []):
        n = normalize_ssot_record(r, zone_name)
        key = record_key(n)
        ssot_records[key] = r

    # Diff
    missing_from_live = [k for k in ssot_records if k not in live_records]
    extra_in_live = [k for k in live_records if k not in ssot_records]

    if not missing_from_live and not extra_in_live:
        print(f"✅ No drift detected. {len(ssot_records)} records match.")
        return 0

    print("\n❌ DNS DRIFT DETECTED\n")

    if missing_from_live:
        print("Records in SSOT but NOT in Cloudflare (need to be created):")
        for k in missing_from_live:
            print(f"  + {k}")

    if extra_in_live:
        print("\nRecords in Cloudflare but NOT in SSOT (untracked — add to SSOT or delete from CF):")
        for k in extra_in_live:
            r = live_records[k]
            print(f"  ? {k}  (CF id: {r.get('id', 'unknown')})")

    print("\nFix: update infra/cloudflare/insightpulseai.com.records.yaml to match live state, then re-run.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
