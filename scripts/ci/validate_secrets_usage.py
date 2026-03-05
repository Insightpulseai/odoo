#!/usr/bin/env python3
"""
validate_secrets_usage.py — Validate workflow secret references against SSOT registry.

Checks:
  1. All secrets referenced in workflows are registered in ssot/secrets/registry.yaml
  2. Vault paths follow convention: service/resource/key
  3. Rotation policies are documented
  4. No hardcoded secrets in workflows (basic pattern detection)
  5. Cross-reference v2_entries with workflow usage

Exit codes:
  0 — all checks pass
  1 — validation errors
  2 — registry file missing or invalid YAML
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REGISTRY_PATH = "ssot/secrets/registry.yaml"
WORKFLOWS_DIR = ".github/workflows"

# Patterns for secret detection
SECRET_REF_PATTERN = re.compile(r'secrets\.([A-Z_][A-Z0-9_]*)')
HARDCODED_SECRET_PATTERNS = [
    re.compile(r'(ghp_[a-zA-Z0-9]{36})'),  # GitHub PAT
    re.compile(r'(gho_[a-zA-Z0-9]{36})'),  # GitHub OAuth token
    re.compile(r'(ghs_[a-zA-Z0-9]{36})'),  # GitHub server token
    re.compile(r'(ghr_[a-zA-Z0-9]{36})'),  # GitHub refresh token
    re.compile(r'(sk_live_[a-zA-Z0-9]{24,})'),  # Stripe live key
    re.compile(r'(sk_test_[a-zA-Z0-9]{24,})'),  # Stripe test key
    re.compile(r'(xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24})'),  # Slack bot token
    re.compile(r'(Bearer [a-zA-Z0-9_\-\.]{20,})'),  # Bearer tokens
]

VAULT_PATH_PATTERN = re.compile(r'^[a-z_]+/[a-z_/]+/[a-z_]+$')


def load_registry(repo_root: Path) -> Tuple[Dict, Set[str]]:
    """Load registry and extract all registered secret keys."""
    path = repo_root / REGISTRY_PATH
    if not path.exists():
        print(f"ERROR: Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error: {e}", file=sys.stderr)
        sys.exit(2)

    # Collect all registered keys from both sections
    registered_keys = set()

    # v1 format secrets
    secrets = data.get("secrets", {})
    for name, entry in secrets.items():
        if isinstance(entry, dict):
            gh_secret = entry.get("github_secret_name")
            if gh_secret:
                registered_keys.add(gh_secret)
            vault_secret = entry.get("vault_secret_name")
            if vault_secret:
                registered_keys.add(vault_secret)

    # v2 format entries
    v2_entries = data.get("v2_entries", {})
    for name, entry in v2_entries.items():
        if isinstance(entry, dict):
            registered_keys.add(entry.get("key", name).upper())
            # Also check consumers for GitHub secret names
            consumers = entry.get("consumers", [])
            for consumer in consumers:
                if isinstance(consumer, dict) and consumer.get("kind") == "github_secret":
                    registered_keys.add(consumer.get("name", ""))
            storage = entry.get("storage", [])
            for store in storage:
                if isinstance(store, dict) and store.get("kind") == "github_secret":
                    registered_keys.add(store.get("name", ""))

    return data, registered_keys


def scan_workflows(repo_root: Path) -> Tuple[Set[str], List[Tuple[str, int, str]]]:
    """Scan workflows for secret references and hardcoded secrets."""
    workflows_path = repo_root / WORKFLOWS_DIR
    if not workflows_path.exists():
        print(f"ERROR: Workflows directory not found: {WORKFLOWS_DIR}", file=sys.stderr)
        sys.exit(2)

    secret_refs = set()
    hardcoded_secrets = []

    for workflow_file in workflows_path.glob("*.yml"):
        with open(workflow_file) as f:
            content = f.read()
            lines = content.splitlines()

        # Extract secret references
        for match in SECRET_REF_PATTERN.finditer(content):
            secret_refs.add(match.group(1))

        # Check for hardcoded secrets
        for line_num, line in enumerate(lines, 1):
            for pattern in HARDCODED_SECRET_PATTERNS:
                if pattern.search(line):
                    hardcoded_secrets.append((
                        workflow_file.name,
                        line_num,
                        line.strip()
                    ))

    return secret_refs, hardcoded_secrets


def validate_vault_paths(registry_data: Dict) -> List[str]:
    """Validate vault paths follow convention: service/resource/key."""
    errors = []

    # Check v1 format secrets
    secrets = registry_data.get("secrets", {})
    for name, entry in secrets.items():
        if isinstance(entry, dict):
            vault_secret = entry.get("vault_secret_name")
            if vault_secret and "vault_path" not in entry:
                errors.append(
                    f"Secret '{name}': missing vault_path field for vault secret '{vault_secret}'"
                )

    # Check v2 format entries
    v2_entries = registry_data.get("v2_entries", {})
    for name, entry in v2_entries.items():
        if isinstance(entry, dict):
            vault_path = entry.get("vault_path")
            if vault_path and not VAULT_PATH_PATTERN.match(vault_path):
                errors.append(
                    f"Secret '{name}': vault_path '{vault_path}' does not follow convention 'service/resource/key'"
                )

    return errors


def validate_rotation_policies(registry_data: Dict) -> List[str]:
    """Validate all secrets have documented rotation policies."""
    errors = []

    # Check v1 format secrets
    secrets = registry_data.get("secrets", {})
    for name, entry in secrets.items():
        if isinstance(entry, dict):
            rotation = entry.get("rotation_policy")
            if not rotation or rotation.strip() == "":
                errors.append(f"Secret '{name}': missing or empty rotation_policy")

    # Check v2 format entries
    v2_entries = registry_data.get("v2_entries", {})
    for name, entry in v2_entries.items():
        if isinstance(entry, dict):
            rotation = entry.get("rotation", {})
            if not isinstance(rotation, dict):
                errors.append(f"Secret '{name}': rotation must be a mapping")
                continue
            cadence = rotation.get("cadence")
            signal = rotation.get("signal")
            if not cadence:
                errors.append(f"Secret '{name}': missing rotation.cadence")
            if not signal:
                errors.append(f"Secret '{name}': missing rotation.signal")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Workflow secrets usage validator")
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    # Load registry
    registry_data, registered_keys = load_registry(repo_root)

    # Scan workflows
    workflow_secrets, hardcoded_secrets = scan_workflows(repo_root)

    errors = []

    # Check 1: Unregistered workflow secrets
    unregistered = workflow_secrets - registered_keys - {"GITHUB_TOKEN"}  # GITHUB_TOKEN is built-in
    for secret in sorted(unregistered):
        errors.append(f"Workflow references unregistered secret: {secret}")

    # Check 2: Hardcoded secrets
    if hardcoded_secrets:
        errors.append("Potential hardcoded secrets detected:")
        for filename, line_num, line in hardcoded_secrets:
            errors.append(f"  {filename}:{line_num} — {line[:80]}")

    # Check 3: Vault path validation
    vault_errors = validate_vault_paths(registry_data)
    errors.extend(vault_errors)

    # Check 4: Rotation policy validation
    rotation_errors = validate_rotation_policies(registry_data)
    errors.extend(rotation_errors)

    # Report results
    if not args.quiet:
        print(f"Secrets usage validation:")
        print(f"  Registered secrets: {len(registered_keys)}")
        print(f"  Workflow references: {len(workflow_secrets)}")
        print(f"  Unregistered: {len(unregistered)}")
        print(f"  Hardcoded detections: {len(hardcoded_secrets)}")
        print()

        if errors:
            print(f"Validation failed ({len(errors)} errors):")
            for err in errors:
                print(f"  ERROR: {err}")
        else:
            print("Secrets usage validation passed — all workflow secrets are registered")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
