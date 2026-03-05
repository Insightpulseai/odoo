#!/usr/bin/env python3
"""
validate_org_taxonomy.py — Org Repository Taxonomy SSOT validator.

Reads ssot/github/org_repos.yaml and validates:
  1. Every repo entry has required fields: tier, category, lifecycle, data_classification
  2. Tier values are 0-4
  3. Category values are from the allowed set
  4. Lifecycle values are from the allowed set
  5. data_classification values are from the allowed set

Exit codes:
  0 — all checks pass
  1 — validation failures found
  2 — YAML file missing or invalid
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = REPO_ROOT / "ssot" / "github" / "org_repos.yaml"

REQUIRED_FIELDS = {"tier", "category", "lifecycle", "data_classification"}
ALLOWED_TIERS = {0, 1, 2, 3, 4}
ALLOWED_CATEGORIES = {"governance", "primitive", "console", "product", "ui", "lab"}
ALLOWED_LIFECYCLES = {"active", "incubating", "deprecated", "archived"}
ALLOWED_CLASSIFICATIONS = {"public", "internal", "restricted"}


def main() -> int:
    if not TAXONOMY_PATH.exists():
        print(f"ERROR: Taxonomy file not found: {TAXONOMY_PATH}", file=sys.stderr)
        return 2

    try:
        with open(TAXONOMY_PATH) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML: {e}", file=sys.stderr)
        return 2

    if not data or "repos" not in data:
        print("ERROR: Missing 'repos' key in taxonomy file", file=sys.stderr)
        return 2

    errors = []
    repos = data["repos"]

    for i, repo in enumerate(repos):
        name = repo.get("name", f"<index {i}>")

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in repo:
                errors.append(f"  {name}: missing required field '{field}'")

        # Validate tier
        tier = repo.get("tier")
        if tier is not None and tier not in ALLOWED_TIERS:
            errors.append(f"  {name}: invalid tier '{tier}' (must be 0-4)")

        # Validate category
        category = repo.get("category")
        if category is not None and category not in ALLOWED_CATEGORIES:
            errors.append(
                f"  {name}: invalid category '{category}' "
                f"(allowed: {sorted(ALLOWED_CATEGORIES)})"
            )

        # Validate lifecycle
        lifecycle = repo.get("lifecycle")
        if lifecycle is not None and lifecycle not in ALLOWED_LIFECYCLES:
            errors.append(
                f"  {name}: invalid lifecycle '{lifecycle}' "
                f"(allowed: {sorted(ALLOWED_LIFECYCLES)})"
            )

        # Validate data_classification
        classification = repo.get("data_classification")
        if classification is not None and classification not in ALLOWED_CLASSIFICATIONS:
            errors.append(
                f"  {name}: invalid data_classification '{classification}' "
                f"(allowed: {sorted(ALLOWED_CLASSIFICATIONS)})"
            )

    # Check for duplicate repo names
    names = [r.get("name") for r in repos if r.get("name")]
    seen = set()
    for n in names:
        if n in seen:
            errors.append(f"  {n}: duplicate repo name")
        seen.add(n)

    if errors:
        print(f"FAIL: {len(errors)} taxonomy validation error(s):")
        for e in errors:
            print(e)
        return 1

    print(f"OK: {len(repos)} repos validated, all fields present and valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
