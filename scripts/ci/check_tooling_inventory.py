#!/usr/bin/env python3
"""Validate ssot/devex/tooling_inventory.yaml for structural correctness.

Checks:
  1. YAML parses without errors
  2. All entries use allowed statuses
  3. No duplicate IDs within each section
  4. MCP server secret_refs exist in ssot/secrets/registry.yaml

Exit 0 on success, 1 on any violation.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "ssot" / "devex" / "tooling_inventory.yaml"
SECRETS_REGISTRY_PATH = REPO_ROOT / "ssot" / "secrets" / "registry.yaml"


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def get_allowed_statuses(data: dict) -> set[str]:
    return set(data.get("meta", {}).get("allowed_statuses", []))


def check_statuses(data: dict, allowed: set[str]) -> list[str]:
    errors: list[str] = []

    for ext in data.get("vscode_extensions", []):
        if ext.get("status") not in allowed:
            errors.append(
                f"vscode_extensions: '{ext.get('id')}' has invalid status "
                f"'{ext.get('status')}' (allowed: {sorted(allowed)})"
            )

    for ext in data.get("docker_desktop_extensions", []):
        if ext.get("status") not in allowed:
            errors.append(
                f"docker_desktop_extensions: '{ext.get('name')}' has invalid status "
                f"'{ext.get('status')}' (allowed: {sorted(allowed)})"
            )

    mcp_statuses = allowed | {"active", "planned", "rejected"}
    for srv in data.get("mcp_servers", []):
        if srv.get("status") not in mcp_statuses:
            errors.append(
                f"mcp_servers: '{srv.get('id')}' has invalid status "
                f"'{srv.get('status')}' (allowed: {sorted(mcp_statuses)})"
            )

    return errors


def check_duplicate_ids(data: dict) -> list[str]:
    errors: list[str] = []

    vscode_ids = [e.get("id") for e in data.get("vscode_extensions", []) if e.get("id")]
    seen = set()
    for vid in vscode_ids:
        if vid in seen:
            errors.append(f"vscode_extensions: duplicate id '{vid}'")
        seen.add(vid)

    docker_names = [e.get("name") for e in data.get("docker_desktop_extensions", []) if e.get("name")]
    seen = set()
    for dn in docker_names:
        if dn in seen:
            errors.append(f"docker_desktop_extensions: duplicate name '{dn}'")
        seen.add(dn)

    mcp_ids = [s.get("id") for s in data.get("mcp_servers", []) if s.get("id")]
    seen = set()
    for mid in mcp_ids:
        if mid in seen:
            errors.append(f"mcp_servers: duplicate id '{mid}'")
        seen.add(mid)

    return errors


def check_secret_refs(data: dict) -> list[str]:
    errors: list[str] = []

    if not SECRETS_REGISTRY_PATH.exists():
        errors.append(f"secrets registry not found: {SECRETS_REGISTRY_PATH}")
        return errors

    secrets_data = load_yaml(SECRETS_REGISTRY_PATH)
    known_secrets = set(secrets_data.get("secrets", {}).keys())
    known_secrets |= set(secrets_data.get("v2_entries", {}).keys())

    for srv in data.get("mcp_servers", []):
        for ref in srv.get("secret_refs", []):
            if ref not in known_secrets:
                errors.append(
                    f"mcp_servers: '{srv.get('id')}' references secret '{ref}' "
                    f"not found in ssot/secrets/registry.yaml"
                )

    return errors


def main() -> int:
    if not INVENTORY_PATH.exists():
        print(f"FAIL: inventory file not found: {INVENTORY_PATH}", file=sys.stderr)
        return 1

    try:
        data = load_yaml(INVENTORY_PATH)
    except yaml.YAMLError as exc:
        print(f"FAIL: YAML parse error: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("FAIL: top-level YAML must be a mapping", file=sys.stderr)
        return 1

    allowed = get_allowed_statuses(data)
    if not allowed:
        print("FAIL: meta.allowed_statuses is empty or missing", file=sys.stderr)
        return 1

    errors: list[str] = []
    errors.extend(check_statuses(data, allowed))
    errors.extend(check_duplicate_ids(data))
    errors.extend(check_secret_refs(data))

    if errors:
        print(f"FAIL: {len(errors)} violation(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK: tooling_inventory.yaml — "
        f"{len(data.get('vscode_extensions', []))} VS Code extensions, "
        f"{len(data.get('docker_desktop_extensions', []))} Docker extensions, "
        f"{len(data.get('mcp_servers', []))} MCP servers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
