#!/usr/bin/env python3
"""
check_github_apps_ssot.py
CI gate: validates ssot/integrations/github_apps.yaml ↔ infra/github/apps/*/manifest.json
         and ensures all secret_refs exist in ssot/secrets/registry.yaml.

Checks:
  1. Every app declared in the SSOT has a corresponding manifest.json
  2. The webhook URL in the SSOT matches the hook_attributes.url in the manifest
  3. Every secret_ref in the SSOT exists in ssot/secrets/registry.yaml
  4. The ingest function references the expected env var names for each secret_ref
  5. All declared events are present in the manifest's default_events
  6. All declared permissions are present in the manifest's default_permissions

Exit codes:
  0 — all checks pass
  1 — one or more violations (details printed to stdout)

Failure mode: CI.GITHUB_APPS_SSOT_DRIFT
SSOT:         ssot/integrations/github_apps.yaml
Runbook:      docs/runbooks/GITHUB_APP_PROVISIONING.md
"""

import json
import re
import sys
from pathlib import Path

import yaml

SSOT_PATH    = "ssot/integrations/github_apps.yaml"
REGISTRY_PATH = "ssot/secrets/registry.yaml"
INFRA_BASE   = "infra/github/apps"
INGEST_PATH  = "supabase/functions/ops-github-webhook-ingest/index.ts"

# ── secret_ref → env var name mapping ─────────────────────────────────────────
# These are the canonical env-var names the ingest function reads.
SECRET_REF_TO_ENV: dict[str, str] = {
    "github_app_webhook_secret":  "GITHUB_APP_WEBHOOK_SECRET",
    "n8n_webhook_github_url":     "N8N_WEBHOOK_GITHUB_URL",
    "n8n_webhook_secret":         "N8N_WEBHOOK_SECRET",
    "plane_api_key":              "PLANE_API_KEY",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_yaml(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"ERROR: required file not found: {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error in {path}: {e}")
        sys.exit(1)


def load_json(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None  # type: ignore[return-value]
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parse error in {path}: {e}")
        sys.exit(1)


def registry_ids(registry: dict) -> set[str]:
    """Return the set of all secret keys in the registry.

    The registry uses two sections:
      secrets:       — v1 format (dict of dicts, keys are secret names)
      v2_entries:    — v2 extended format (same dict-of-dicts, keys are secret names)

    Both are merged to form the full known-secrets set.
    """
    ids: set[str] = set()
    for section in ("secrets", "v2_entries"):
        block = registry.get(section) or {}
        if isinstance(block, dict):
            ids.update(block.keys())
        elif isinstance(block, list):
            # Fallback: list-of-dicts with id field
            ids.update(s["id"] for s in block if isinstance(s, dict) and "id" in s)
    return ids


# ── Main validation logic ─────────────────────────────────────────────────────

def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # Load files
    ssot     = load_yaml(SSOT_PATH)
    registry = load_yaml(REGISTRY_PATH)
    reg_ids  = registry_ids(registry)

    apps: list[dict] = (ssot.get("apps") or [])
    if not apps:
        print(f"WARNING: no apps declared in {SSOT_PATH}")
        return 0

    ingest_src = ""
    try:
        with open(INGEST_PATH, "r") as f:
            ingest_src = f.read()
    except FileNotFoundError:
        errors.append(f"INGEST_MISSING: {INGEST_PATH} not found")

    for app in apps:
        app_id   = app.get("id", "<unnamed>")
        prefix   = f"[{app_id}]"

        # ── Check 1: manifest.json exists ─────────────────────────────────────
        manifest_path = Path(INFRA_BASE) / app_id / "manifest.json"
        manifest = load_json(str(manifest_path))
        if manifest is None:
            errors.append(
                f"{prefix} MANIFEST_MISSING: {manifest_path} not found. "
                f"Run: scripts/github/create-app-from-manifest.sh {app_id}"
            )
            # Can't do further manifest checks without the file
            # Still continue to check secret_refs
            manifest = {}

        # ── Check 2: Webhook URL parity ───────────────────────────────────────
        ssot_webhook_url  = (app.get("webhook") or {}).get("url", "")
        manifest_hook_url = ((manifest.get("hook_attributes") or {}).get("url") or "")
        if ssot_webhook_url and manifest_hook_url and ssot_webhook_url != manifest_hook_url:
            errors.append(
                f"{prefix} WEBHOOK_URL_DRIFT: "
                f"SSOT={ssot_webhook_url!r} ≠ manifest={manifest_hook_url!r}"
            )

        # ── Check 3: secret_refs exist in registry ────────────────────────────
        declared_refs: list[str] = app.get("secrets") or []
        for ref in declared_refs:
            if ref not in reg_ids:
                errors.append(
                    f"{prefix} SECRET_REF_MISSING: '{ref}' not found in {REGISTRY_PATH}. "
                    f"Add it under secrets: with the same id."
                )

        # ── Check 4: ingest function references env vars ──────────────────────
        if ingest_src:
            for ref in declared_refs:
                env_var = SECRET_REF_TO_ENV.get(ref)
                if env_var and env_var not in ingest_src:
                    errors.append(
                        f"{prefix} ENV_VAR_NOT_REFERENCED: secret_ref '{ref}' maps to "
                        f"env var '{env_var}' but it is not referenced in {INGEST_PATH}"
                    )

        # ── Check 5: events parity ────────────────────────────────────────────
        ssot_events    = set(app.get("events") or [])
        manifest_events = set(manifest.get("default_events") or [])
        if ssot_events and manifest_events:
            missing_in_manifest = ssot_events - manifest_events
            for ev in sorted(missing_in_manifest):
                errors.append(
                    f"{prefix} EVENT_DRIFT: event '{ev}' in SSOT but not in manifest "
                    f"default_events"
                )
            extra_in_manifest = manifest_events - ssot_events
            for ev in sorted(extra_in_manifest):
                warnings.append(
                    f"{prefix} EVENT_EXTRA: manifest has event '{ev}' not declared in SSOT "
                    f"(harmless but consider adding to SSOT)"
                )

        # ── Check 6: permissions parity ───────────────────────────────────────
        ssot_perms     = app.get("permissions") or {}
        manifest_perms = manifest.get("default_permissions") or {}
        if ssot_perms and manifest_perms:
            for perm, level in ssot_perms.items():
                manifest_level = manifest_perms.get(perm)
                if manifest_level is None:
                    errors.append(
                        f"{prefix} PERM_MISSING: permission '{perm}:{level}' declared in SSOT "
                        f"but not in manifest default_permissions"
                    )
                elif manifest_level != level:
                    errors.append(
                        f"{prefix} PERM_DRIFT: permission '{perm}' SSOT={level!r} ≠ "
                        f"manifest={manifest_level!r}"
                    )

    # ── Report ────────────────────────────────────────────────────────────────
    if warnings:
        for w in warnings:
            print(f"WARN  {w}")

    if errors:
        print(f"\n{'─' * 60}")
        print(f"FAIL  {len(errors)} violation(s) found in GitHub Apps SSOT parity check")
        print(f"{'─' * 60}")
        for e in errors:
            print(f"  ✗  {e}")
        print(f"\nRunbook: docs/runbooks/GITHUB_APP_PROVISIONING.md")
        print(f"SSOT:    {SSOT_PATH}")
        return 1

    print(f"PASS  GitHub Apps SSOT parity check: {len(apps)} app(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
