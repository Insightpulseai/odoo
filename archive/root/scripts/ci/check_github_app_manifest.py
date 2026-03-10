#!/usr/bin/env python3
"""
check_github_app_manifest.py
CI gate: validates ssot/github/app-manifest.yaml against the registry and spec.

Checks:
  1. webhook.secret_ref exists in ssot/secrets/registry.yaml
  2. Every event in manifest.events is declared in spec/github-integrations/prd.md
     normalization table
  3. Every event declared in prd.md normalization table is subscribed in the manifest

Exit codes:
  0 — all checks pass
  1 — one or more violations (details printed to stdout)

Failure mode: CI.GITHUB_MANIFEST_DRIFT
Runbook:      docs/runbooks/GITHUB_APP_PROVISIONING.md
"""
import re
import sys
import yaml

MANIFEST_PATH = "ssot/github/app-manifest.yaml"
REGISTRY_PATH = "ssot/secrets/registry.yaml"
PRD_PATH      = "spec/github-integrations/prd.md"

# ── Load files ────────────────────────────────────────────────────────────────

def load_yaml(path: str) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"FAIL: file not found: {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"FAIL: YAML parse error in {path}: {e}")
        sys.exit(1)


def load_text(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"FAIL: file not found: {path}")
        sys.exit(1)

# ── Parse prd.md normalization table ─────────────────────────────────────────
# Extracts event names from the markdown table rows like:
#   | `issues` (opened/closed/assigned) | ...
#   | `pull_request` (opened/merged/closed) | ...
#   | `check_run` / `check_suite` | ...
#   | `push` (to main) | ...
#   | `installation` | ...

BULLET_EVENT_PATTERN = re.compile(r'^[-*]\s+`([a-z][a-z0-9_]*)`')

def parse_prd_events(prd_text: str) -> set[str]:
    """
    Return subscribed webhook event names from the '## Subscribed Webhook Events'
    bullet list in prd.md.

    We parse the section explicitly to avoid false positives from the Permissions
    Matrix table (which contains permission names like 'pull_requests', not events).
    """
    events: set[str] = set()
    in_section = False
    for line in prd_text.splitlines():
        stripped = line.strip()
        if re.match(r"^#+\s+Subscribed Webhook Events", stripped):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("#"):
                # Hit the next heading — section ends
                break
            m = BULLET_EVENT_PATTERN.match(stripped)
            if m:
                events.add(m.group(1))
    return events

# ── Registry key lookup ───────────────────────────────────────────────────────

def registry_keys(registry: dict) -> set[str]:
    """Return all secret/config keys from both v1 and v2 sections."""
    keys: set[str] = set()
    for section_name in ("secrets", "v2_entries"):
        section = registry.get(section_name, {})
        if isinstance(section, dict):
            keys.update(section.keys())
    return keys

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    manifest = load_yaml(MANIFEST_PATH)
    registry = load_yaml(REGISTRY_PATH)
    prd_text = load_text(PRD_PATH)

    errors: list[str] = []

    # ── Check 1: webhook.secret_ref is in registry ────────────────────────────
    webhook     = manifest.get("webhook", {}) or {}
    secret_ref  = webhook.get("secret_ref")
    reg_keys    = registry_keys(registry)

    if not secret_ref:
        errors.append(
            f"  [{MANIFEST_PATH}] webhook.secret_ref is missing"
        )
    elif secret_ref not in reg_keys:
        errors.append(
            f"  [{MANIFEST_PATH}] webhook.secret_ref='{secret_ref}' "
            f"not found in {REGISTRY_PATH}\n"
            f"  Add it under secrets: or v2_entries: before referencing."
        )

    # ── Check 2: manifest events ⊆ prd events ─────────────────────────────────
    manifest_events: list[str] = manifest.get("events", []) or []
    prd_events = parse_prd_events(prd_text)

    for event in manifest_events:
        if event not in prd_events:
            errors.append(
                f"  [{MANIFEST_PATH}] event '{event}' is subscribed in the App manifest "
                f"but not declared in {PRD_PATH} normalization table.\n"
                f"  Either add it to the PRD table or remove it from the manifest."
            )

    # ── Check 3: prd events ⊆ manifest events ─────────────────────────────────
    manifest_event_set = set(manifest_events)
    for event in prd_events:
        if event not in manifest_event_set:
            errors.append(
                f"  [{PRD_PATH}] event '{event}' declared in normalization table "
                f"but not subscribed in {MANIFEST_PATH}.\n"
                f"  Either add it to the manifest events list or remove it from the PRD."
            )

    # ── Report ────────────────────────────────────────────────────────────────
    if errors:
        print(f"FAIL: {len(errors)} GitHub App manifest violation(s):\n")
        for e in errors:
            print(e)
        print(
            f"\nRunbook: docs/runbooks/GITHUB_APP_PROVISIONING.md\n"
            f"Failure mode: CI.GITHUB_MANIFEST_DRIFT"
        )
        return 1

    n_events  = len(manifest_events)
    print(
        f"PASS: manifest valid — secret_ref='{secret_ref}' in registry; "
        f"{n_events} event(s) covered in PRD normalization table"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
