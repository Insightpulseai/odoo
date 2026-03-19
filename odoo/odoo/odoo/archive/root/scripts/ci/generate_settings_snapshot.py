#!/usr/bin/env python3
"""
generate_settings_snapshot.py
──────────────────────────────────────────────────────────────────────────────
Reads SSOT files + queries Supabase to produce a settings_snapshot artifact
and inserts it into ops.artifacts.

Used by: .github/workflows/settings-snapshot.yml

Reads (relative to repo root):
  ssot/integrations/github_apps.yaml
  ssot/integrations/_index.yaml
  ssot/parity/odoo_enterprise.yaml
  ssot/runtime/prod_settings.yaml
  infra/dns/subdomain-registry.yaml

Queries:
  ops.github_webhook_deliveries  — last 24h stats
  ops.artifacts                  — existing snapshots (dedup check)

Inserts:
  ops.artifacts  kind=settings_snapshot

Environment variables required:
  SUPABASE_URL              (or NEXT_PUBLIC_SUPABASE_URL)
  SUPABASE_SERVICE_ROLE_KEY
  GITHUB_SHA                (set by GitHub Actions)
  GITHUB_REF_NAME           (set by GitHub Actions)

Exit codes:
  0 — snapshot inserted (or identical snapshot already exists)
  1 — fatal error
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ── Config ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]

SUPABASE_URL = (
    os.environ.get("SUPABASE_URL")
    or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    or ""
)
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
GIT_SHA = os.environ.get("GITHUB_SHA", "local")
GIT_BRANCH = os.environ.get("GITHUB_REF_NAME", "local")


# ── Supabase helpers ──────────────────────────────────────────────────────────

def _headers(schema: str = "ops", write: bool = False) -> dict:
    """
    PostgREST schema routing:
      Accept-Profile  — GET/HEAD requests targeting a non-public schema
      Content-Profile — POST/PATCH/PUT/DELETE requests targeting a non-public schema
    """
    h = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    if schema != "public":
        if write:
            h["Content-Profile"] = schema
        else:
            h["Accept-Profile"] = schema
    return h


def _get(table: str, params: dict | None = None, schema: str = "ops") -> list:
    """GET from PostgREST. table = bare table name (no schema prefix)."""
    qs = "&".join(f"{k}={v}" for k, v in (params or {}).items())
    url = f"{SUPABASE_URL}/rest/v1/{table}{'?' + qs if qs else ''}"
    req = urllib.request.Request(url, headers=_headers(schema=schema, write=False))
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"WARN: GET {table} → HTTP {e.code}: {e.read()[:200]}", file=sys.stderr)
        return []


def _post(table: str, body: dict, schema: str = "ops") -> bool:
    """POST to PostgREST. table = bare table name (no schema prefix)."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(schema=schema, write=True), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            _ = resp.read()
            return True
    except urllib.error.HTTPError as e:
        print(f"ERROR: POST {table} → HTTP {e.code}: {e.read()[:400]}", file=sys.stderr)
        return False


# ── SSOT readers ─────────────────────────────────────────────────────────────

def load_yaml(rel: str) -> dict | list | None:
    path = REPO_ROOT / rel
    if not path.exists():
        print(f"WARN: {rel} not found — skipping", file=sys.stderr)
        return None
    with path.open() as f:
        return yaml.safe_load(f)


# ── Snapshot builders ─────────────────────────────────────────────────────────

def build_project(prod_settings: dict | None, dns: dict | None) -> dict:
    urls = []
    if prod_settings:
        for u in prod_settings.get("urls", {}).get("active_required", []):
            urls.append({"url": u["url"], "service": u["service"]})

    return {
        "name": "insightpulseai",
        "domain": dns.get("domain", "insightpulseai.com") if dns else "insightpulseai.com",
        "prod_url": "https://erp.insightpulseai.com",
        "db_names": {"prod": "odoo_prod", "stage": "odoo_staging", "dev": "odoo_dev"},
        "urls": urls,
    }


def build_dns(dns: dict | None) -> dict:
    if not dns:
        return {"subdomains": [], "active_count": 0, "planned_count": 0, "broken_count": 0}
    subs = dns.get("subdomains", [])
    return {
        "subdomains": [
            {
                "name": s.get("name"),
                "lifecycle": s.get("lifecycle", "unknown"),
                "type": s.get("type", "A"),
                "target": s.get("target"),
                "port": s.get("port"),
                "backing_status": s.get("backing_status"),
            }
            for s in subs
        ],
        "active_count": sum(1 for s in subs if s.get("lifecycle") == "active"),
        "planned_count": sum(1 for s in subs if s.get("lifecycle") == "planned"),
        "broken_count": sum(1 for s in subs if s.get("backing_status") == "broken"),
    }


def build_integrations(github_apps_yaml: dict | None, index_yaml: dict | list | None) -> dict:
    gh_app = {}
    if github_apps_yaml:
        apps = github_apps_yaml.get("apps", [])
        app = apps[0] if apps else {}
        wh = app.get("webhook", {})
        ledger = app.get("ledger", {})
        gh_app = {
            "id": app.get("id", "ipai-integrations"),
            "status": github_apps_yaml.get("status", "unknown"),
            "webhook": {
                "url": wh.get("url", ""),
                "active": wh.get("active", False),
            },
            "events": app.get("events", []),
            "ledger": {
                "deliveries_table": ledger.get("deliveries_table", "ops.github_webhook_deliveries"),
                "work_items_table": ledger.get("work_items_table", "ops.work_items"),
            },
        }

    all_integrations: list[dict] = []
    if isinstance(index_yaml, dict):
        for item in index_yaml.get("integrations", []):
            all_integrations.append({
                "id": item.get("id", ""),
                "display_name": item.get("display_name", ""),
                "kind": item.get("kind", ""),
                "status": item.get("status", "unknown"),
            })

    return {"github_apps": gh_app, "all": all_integrations}


def build_parity(parity_yaml: dict | None) -> dict:
    if not parity_yaml:
        return {"total": 0, "met": 0, "partial": 0, "missing": 0, "waived": 0,
                "required_missing": 0, "scope": "unknown", "features": []}

    features = parity_yaml.get("features", [])
    met = sum(1 for f in features if f.get("status") == "met")
    partial = sum(1 for f in features if f.get("status") == "partial")
    missing = sum(1 for f in features if f.get("status") == "missing")
    waived = sum(1 for f in features if f.get("status") == "waived")
    required_missing = sum(
        1 for f in features if f.get("status") == "missing" and f.get("required", False)
    )

    return {
        "total": len(features),
        "met": met,
        "partial": partial,
        "missing": missing,
        "waived": waived,
        "required_missing": required_missing,
        "scope": parity_yaml.get("scope", "Odoo 19.0 CE self-hosted"),
        "features": [
            {
                "id": f.get("id", ""),
                "category": f.get("category", ""),
                "description": f.get("description", ""),
                "required": f.get("required", False),
                "status": f.get("status", "unknown"),
                "implementation": f.get("implementation", ""),
                "module_or_ref": f.get("module_or_ref", ""),
            }
            for f in features
        ],
    }


def build_capacity(prod_settings: dict | None) -> dict:
    odoo = prod_settings.get("odoo", {}) if prod_settings else {}
    return {
        "odoo_workers": 4,  # default; override from config/prod/odoo.conf if available
        "db_max_connections": 100,
        "note": "from ssot/runtime/prod_settings.yaml; update after any worker change",
    }


def build_webhook_stats() -> dict:
    """Query ops.github_webhook_deliveries for 24h stats."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return {"total_24h": 0, "failed_24h": 0, "last_received_at": None}

    rows = _get(
        "github_webhook_deliveries",   # bare table name; schema=ops via Accept-Profile header
        {
            "received_at": "gte." + (datetime.now(timezone.utc).strftime("%Y-%m-%dT") + "00:00:00+00:00"),
            "select": "status,received_at",
            "order": "received_at.desc",
            "limit": "500",
        },
        schema="ops",
    )

    total = len(rows)
    failed = sum(1 for r in rows if r.get("status") == "failed")
    last = rows[0]["received_at"] if rows else None

    return {"total_24h": total, "failed_24h": failed, "last_received_at": last}


def build_staging(dns: dict | None) -> dict:
    if not dns:
        return {"subdomains": []}
    subs = dns.get("subdomains", [])
    staging = [
        {
            "name": s.get("name"),
            "lifecycle": s.get("lifecycle"),
            "type": s.get("type"),
            "port": s.get("port"),
        }
        for s in subs
        if s.get("lifecycle") in ("planned", "active") and s.get("name", "").startswith("stage")
    ]
    return {"subdomains": staging}


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("WARN: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. Snapshot will not be inserted.", file=sys.stderr)

    print(f"Loading SSOT files from {REPO_ROOT} …")

    github_apps_yaml = load_yaml("ssot/integrations/github_apps.yaml") or {}
    index_yaml = load_yaml("ssot/integrations/_index.yaml") or {}
    parity_yaml = load_yaml("ssot/parity/odoo_enterprise.yaml") or {}
    prod_settings = load_yaml("ssot/runtime/prod_settings.yaml") or {}
    dns_yaml = load_yaml("infra/dns/subdomain-registry.yaml") or {}

    print("Building snapshot …")
    webhook_stats = build_webhook_stats()

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": build_project(prod_settings, dns_yaml),
        "dns": build_dns(dns_yaml),
        "integrations": build_integrations(github_apps_yaml, index_yaml),
        "parity": build_parity(parity_yaml),
        "capacity": build_capacity(prod_settings),
        "staging": build_staging(dns_yaml),
        "webhook_stats": webhook_stats,
    }

    snapshot = {
        "kind": "settings_snapshot",
        "sha": GIT_SHA,
        "branch": GIT_BRANCH,
        "artifact_url": None,
        "metadata": metadata,
    }

    # Print summary
    p = metadata["parity"]
    d = metadata["dns"]
    i = metadata["integrations"]
    print(f"  Parity:  {p['met']}/{p['total']} met  ({p['required_missing']} required missing)")
    print(f"  DNS:     {d['active_count']} active  {d['planned_count']} planned  {d['broken_count']} broken")
    print(f"  GitHub:  {i['github_apps'].get('status', 'unknown')}")
    print(f"  Webhook: {webhook_stats['total_24h']} deliveries / 24h  ({webhook_stats['failed_24h']} failed)")

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        # Dry-run: write to stdout and exit 0
        print("\n[DRY RUN] Snapshot JSON (not inserted — no Supabase credentials):")
        print(json.dumps(snapshot, indent=2, default=str))
        return 0

    print("\nInserting into ops.artifacts …")
    ok = _post("artifacts", snapshot, schema="ops")
    if not ok:
        print("ERROR: Failed to insert snapshot.", file=sys.stderr)
        return 1

    print(f"✓ settings_snapshot inserted  sha={GIT_SHA[:7]}  branch={GIT_BRANCH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
