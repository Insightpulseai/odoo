#!/usr/bin/env python3
"""
check_secrets_ssot.py — Validate secrets SSOT registry.

Checks:
  1. YAML parses successfully
  2. Schema field matches ssot.secrets.v1
  3. Required fields present in every secret entry
  4. Every secret has >= 1 consumer
  5. Consumer format matches "store:identifier" pattern

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

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REGISTRY_PATH = "ssot/secrets/registry.yaml"
INVENTORY_PATH = "ssot/secrets/inventory.yaml"
CONSUMER_PATTERN = re.compile(r"^[a-z_/]+:.+$")


def load_registry(repo_root: Path) -> dict:
    path = repo_root / REGISTRY_PATH
    if not path.exists():
        print(f"ERROR: Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error: {e}", file=sys.stderr)
        sys.exit(2)


def validate(data: dict) -> list[str]:
    errors = []

    schema = data.get("schema", "")
    if not schema.startswith("ssot.secrets"):
        errors.append(f"Missing or invalid 'schema' field (got '{schema}')")

    schema_rules = data.get("schema_rules", {})
    required_fields = schema_rules.get("required_fields", ["purpose", "approved_stores", "consumers"])
    valid_stores = schema_rules.get("consumer_stores", [])

    secrets = data.get("secrets", {})
    if not isinstance(secrets, dict):
        errors.append("'secrets' must be a mapping (key: secret_name -> value: dict)")
        return errors

    for name, entry in secrets.items():
        if not isinstance(entry, dict):
            errors.append(f"Secret '{name}': entry must be a mapping")
            continue

        # Required fields
        for field in required_fields:
            if field not in entry:
                errors.append(f"Secret '{name}': missing required field '{field}'")

        # Consumers
        consumers = entry.get("consumers", [])
        if not consumers:
            errors.append(f"Secret '{name}': must have at least one consumer")
        else:
            for consumer in consumers:
                if not isinstance(consumer, str):
                    errors.append(f"Secret '{name}': consumer must be a string, got {type(consumer)}")
                    continue
                if not CONSUMER_PATTERN.match(consumer):
                    errors.append(
                        f"Secret '{name}': consumer '{consumer}' does not match "
                        f"'store:identifier' format"
                    )
                    continue
                store = consumer.split(":", 1)[0]
                if valid_stores and store not in valid_stores:
                    errors.append(
                        f"Secret '{name}': consumer store '{store}' not in allowed stores "
                        f"{valid_stores}"
                    )

    return errors


def load_inventory(repo_root: Path) -> dict:
    path = repo_root / INVENTORY_PATH
    if not path.exists():
        print(f"ERROR: Inventory not found: {INVENTORY_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error in inventory: {e}", file=sys.stderr)
        sys.exit(2)


VALID_STATUS_VALUES = {"working", "stale", "missing", "unknown"}
VALID_EVIDENCE_KINDS = {
    "api_call", "ssh_session", "psql_query", "ci_run",
    "smtp_e2e", "edge_fn_log", "session_log",
}


def validate_inventory(inv_data: dict, registry_secrets: set[str]) -> tuple[list[str], list[str]]:
    """Validate inventory.yaml and cross-reference against registry.

    Returns (errors, warnings).
    Errors cause exit 1. Warnings are printed but do not fail.
    """
    errors: list[str] = []
    warnings: list[str] = []

    schema = inv_data.get("schema", "")
    if schema != "ssot.secrets.inventory.v1":
        errors.append(f"Invalid 'schema' field (expected 'ssot.secrets.inventory.v1', got '{schema}')")

    inventory = inv_data.get("inventory", {})
    if not isinstance(inventory, dict):
        errors.append("'inventory' must be a mapping")
        return errors, warnings

    inv_keys = set(inventory.keys())

    # Check: every inventory entry must exist in registry
    orphan_inv = inv_keys - registry_secrets
    for key in sorted(orphan_inv):
        errors.append(f"Inventory entry '{key}' has no matching key in registry — drift detected")

    # Warn: registry entries without an inventory entry
    missing_inv = registry_secrets - inv_keys
    for key in sorted(missing_inv):
        warnings.append(f"Registry key '{key}' has no inventory entry — consider adding status")

    # Validate each inventory entry structure
    for name, entry in inventory.items():
        if not isinstance(entry, dict):
            errors.append(f"Inventory '{name}': entry must be a mapping")
            continue

        # status block
        status_block = entry.get("status")
        if not status_block or not isinstance(status_block, dict):
            errors.append(f"Inventory '{name}': missing 'status' block")
        else:
            val = status_block.get("value")
            if val not in VALID_STATUS_VALUES:
                errors.append(
                    f"Inventory '{name}': invalid status.value '{val}' "
                    f"(must be one of {sorted(VALID_STATUS_VALUES)})"
                )
            evidence = status_block.get("evidence", [])
            if not isinstance(evidence, list):
                errors.append(f"Inventory '{name}': status.evidence must be a list")
            else:
                for i, ev in enumerate(evidence):
                    if not isinstance(ev, dict):
                        errors.append(f"Inventory '{name}': evidence[{i}] must be a mapping")
                        continue
                    kind = ev.get("kind")
                    if kind and kind not in VALID_EVIDENCE_KINDS:
                        errors.append(
                            f"Inventory '{name}': evidence[{i}].kind '{kind}' "
                            f"not in {sorted(VALID_EVIDENCE_KINDS)}"
                        )

        # rotation block
        rotation = entry.get("rotation")
        if not rotation or not isinstance(rotation, dict):
            errors.append(f"Inventory '{name}': missing 'rotation' block")
        else:
            if "rotate_now" not in rotation:
                errors.append(f"Inventory '{name}': rotation.rotate_now is required")
            elif not isinstance(rotation["rotate_now"], bool):
                errors.append(f"Inventory '{name}': rotation.rotate_now must be a boolean")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Secrets SSOT registry and inventory validator")
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--check-inventory",
        action="store_true",
        help="Validate ssot/secrets/inventory.yaml and cross-reference with registry",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if args.check_inventory:
        # Load both files — registry keys are needed for cross-reference.
        # The registry has two top-level sections with different schemas:
        #   secrets:     — v1-format validated entries
        #   v2_entries:  — v2-format entries (different structure, separate YAML key)
        # Both are valid registry sources for inventory cross-reference.
        reg_data = load_registry(repo_root)
        registry_secrets = (
            set(reg_data.get("secrets", {}).keys())
            | set(reg_data.get("v2_entries", {}).keys())
        )

        inv_data = load_inventory(repo_root)
        errors, warnings = validate_inventory(inv_data, registry_secrets)

        if not args.quiet:
            for warn in warnings:
                print(f"  WARN: {warn}")
            if errors:
                print(f"Inventory validation failed ({len(errors)} errors):")
                for err in errors:
                    print(f"  ERROR: {err}")
            else:
                count = len(inv_data.get("inventory", {}))
                print(f"Inventory validation passed — {count} entries checked, {len(warnings)} warnings")

        return 1 if errors else 0

    # Default: validate registry schema
    data = load_registry(repo_root)
    errors = validate(data)

    if not args.quiet:
        if errors:
            print(f"Secrets SSOT validation failed ({len(errors)} errors):")
            for err in errors:
                print(f"  {err}")
        else:
            count = len(data.get("secrets", {}))
            print(f"Secrets SSOT validation passed — {count} secrets validated")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
