#!/usr/bin/env python3
"""Validate secrets registry structure and constraints."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    print("ERROR: missing dependency pyyaml. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REG = Path("infra/secrets/registry.yaml")

REQUIRED_KEYS = {"name", "store", "env_var", "required"}
ALLOWED_STORES = {"github_actions", "supabase_edge_secrets", "supabase_vault"}

def main() -> int:
    if not REG.exists():
        print(f"ERROR: missing {REG}")
        return 2

    data = yaml.safe_load(REG.read_text())
    if not isinstance(data, dict) or "secrets" not in data:
        print("ERROR: invalid registry structure (expected top-level 'secrets:')")
        return 2

    secrets = data["secrets"]
    if not isinstance(secrets, list) or not secrets:
        print("ERROR: 'secrets' must be a non-empty list")
        return 2

    names = set()
    errors = 0

    for i, s in enumerate(secrets):
        if not isinstance(s, dict):
            print(f"ERROR: secrets[{i}] must be a mapping")
            errors += 1
            continue

        missing = REQUIRED_KEYS - set(s.keys())
        if missing:
            print(f"ERROR: secrets[{i}] missing keys: {sorted(missing)}")
            errors += 1

        name = s.get("name")
        store = s.get("store")
        env_var = s.get("env_var")

        if not isinstance(name, str) or not name.strip():
            print(f"ERROR: secrets[{i}].name must be a non-empty string")
            errors += 1
        if name in names:
            print(f"ERROR: duplicate secret name: {name}")
            errors += 1
        names.add(name)

        if store not in ALLOWED_STORES:
            print(f"ERROR: {name}: store must be one of {sorted(ALLOWED_STORES)} (got {store})")
            errors += 1

        if not isinstance(env_var, str) or not env_var.strip():
            print(f"ERROR: {name}: env_var must be a non-empty string")
            errors += 1

        # store-specific requirements
        if store == "github_actions":
            if not s.get("repo"):
                print(f"ERROR: {name}: github_actions requires 'repo: owner/name'")
                errors += 1
        if store in {"supabase_edge_secrets", "supabase_vault"}:
            if not s.get("supabase_project_ref_env"):
                print(f"ERROR: {name}: {store} requires 'supabase_project_ref_env'")
                errors += 1

    if errors:
        print(f"FAILED: {errors} error(s)")
        return 1

    print(f"OK: secrets registry validated ({len(names)} secrets)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
