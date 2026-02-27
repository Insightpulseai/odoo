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
CONSUMER_PATTERN = re.compile(r"^[a-z_]+:.+$")


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Secrets SSOT registry validator")
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
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
