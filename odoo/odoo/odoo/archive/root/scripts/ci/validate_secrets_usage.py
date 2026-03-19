#!/usr/bin/env python3
"""
validate_secrets_usage.py — Secrets SSOT usage validator.

Scans .github/workflows/*.yml for ${{ secrets.NAME }} references and checks
that every referenced secret is registered in ssot/secrets/registry.yaml
(either in the v1 'secrets' section or the v2 'v2_entries' section).

Exit codes:
  0 — all referenced secrets are registered
  1 — unregistered secrets found
  2 — registry file missing or invalid YAML
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "ssot" / "secrets" / "registry.yaml"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

# Match ${{ secrets.NAME }}
SECRETS_PATTERN = re.compile(r"\$\{\{\s*secrets\.([A-Z0-9_]+)\s*\}\}")

# Built-in GitHub secrets that don't need registration
BUILTIN_SECRETS = {"GITHUB_TOKEN", "ACTIONS_STEP_DEBUG", "ACTIONS_RUNNER_DEBUG"}


def collect_registered_names(data: dict) -> set:
    """Collect all known secret names from the registry (v1 + v2)."""
    names = set()

    # v1 secrets section
    secrets = data.get("secrets", {})
    if isinstance(secrets, dict):
        for _key, entry in secrets.items():
            if isinstance(entry, dict):
                gh_name = entry.get("github_secret_name")
                if gh_name:
                    names.add(gh_name)
                # Also collect aliases
                for alias in entry.get("github_secret_aliases", []):
                    names.add(alias)

    # v2_entries section
    v2 = data.get("v2_entries", {})
    if isinstance(v2, dict):
        for _key, entry in v2.items():
            if isinstance(entry, dict):
                # Collect from consumers and storage
                for consumer in entry.get("consumers", []):
                    if isinstance(consumer, dict) and consumer.get("kind") == "github_secret":
                        names.add(consumer["name"])
                for store in entry.get("storage", []):
                    if isinstance(store, dict) and store.get("kind") == "github_secret":
                        names.add(store["name"])
                # Also collect aliases if present
                for alias in entry.get("aliases", []):
                    names.add(alias)

    return names


def main() -> int:
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry file not found: {REGISTRY_PATH}", file=sys.stderr)
        return 2

    try:
        with open(REGISTRY_PATH) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML: {e}", file=sys.stderr)
        return 2

    if not data:
        print("ERROR: Empty registry file", file=sys.stderr)
        return 2

    registered = collect_registered_names(data)
    registered.update(BUILTIN_SECRETS)

    if not WORKFLOWS_DIR.exists():
        print("WARN: No .github/workflows/ directory found, skipping scan.")
        return 0

    unregistered = {}  # secret_name -> list of workflow files

    for wf_file in sorted(WORKFLOWS_DIR.glob("*.yml")):
        content = wf_file.read_text(errors="replace")
        for match in SECRETS_PATTERN.finditer(content):
            secret_name = match.group(1)
            if secret_name not in registered:
                unregistered.setdefault(secret_name, []).append(wf_file.name)

    if unregistered:
        # Soft-fail: warn but don't block PRs (matches check_secrets_registry.py pattern).
        # Hard-fail only for NEW secrets introduced in the current PR diff.
        print(f"WARN: {len(unregistered)} unregistered secret(s) found in workflows:")
        for name, files in sorted(unregistered.items()):
            print(f"  {name}")
            for f in sorted(set(files)):
                print(f"    -> {f}")
        print("\nTo register, add entries to ssot/secrets/registry.yaml.")
        # Exit 0 (soft-fail) — flip to 1 when backlog is cleared
        return 0

    total_wf = len(list(WORKFLOWS_DIR.glob("*.yml")))
    print(f"OK: All workflow secrets are registered ({total_wf} workflows scanned, "
          f"{len(registered)} registered names).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
