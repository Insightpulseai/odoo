#!/usr/bin/env python3
"""
Validate Addons Manifest — Odoo 19.0 CE

Validates config/addons.manifest.yaml against the actual repo state:
  1. Manifest ↔ oca-aggregate.yml sync (repos must match)
  2. No duplicate module names across OCA repos
  3. Must-have modules exist on disk (if addons/oca/ is hydrated)
  4. IPAI modules have valid __manifest__.py
  5. Addon path order matches SSOT invariant

Usage:
    python scripts/odoo/validate_addons_manifest.py [--check-hydrated]

Exit codes:
    0 - All validations pass
    1 - Validation errors found
    2 - Script execution error

Requires: PyYAML (pip install pyyaml)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ============================================================================
# Configuration
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "config" / "addons.manifest.yaml"
AGGREGATE_PATH = REPO_ROOT / "oca-aggregate.yml"
OCA_ROOT = REPO_ROOT / "addons" / "oca"
IPAI_ROOT = REPO_ROOT / "addons" / "ipai"
DOCKERFILE_PATH = REPO_ROOT / "docker" / "Dockerfile.unified"

# SSOT invariant: addon path order
EXPECTED_PATH_ORDER = [
    "/usr/lib/python3/dist-packages/odoo/addons",  # CE core
    "/opt/odoo/addons/oca",                          # OCA flattened
    "/opt/odoo/addons/ipai",                         # IPAI custom
]


# ============================================================================
# Helpers
# ============================================================================

class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def log(self, msg: str) -> None:
        self.info.append(msg)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARN:  {w}")
        for i in self.info:
            lines.append(f"  INFO:  {i}")
        return "\n".join(lines)


def load_yaml(path: Path) -> Any:
    with open(path) as f:
        return yaml.safe_load(f)


def extract_aggregate_repos(agg: dict) -> set[str]:
    """Extract repo names from oca-aggregate.yml keys."""
    repos = set()
    for key in agg:
        # Keys are like ./addons/oca/server-tools
        parts = key.strip("./").split("/")
        if len(parts) >= 3 and parts[0] == "addons" and parts[1] == "oca":
            repos.add(parts[2])
    return repos


def find_modules_on_disk(repo_dir: Path) -> set[str]:
    """Find all module directories with __manifest__.py in a repo dir."""
    modules = set()
    if not repo_dir.is_dir():
        return modules
    for entry in repo_dir.iterdir():
        if entry.is_dir() and (entry / "__manifest__.py").is_file():
            modules.add(entry.name)
    return modules


# ============================================================================
# Validators
# ============================================================================

def validate_manifest_schema(manifest: dict, result: ValidationResult) -> None:
    """Check manifest has required top-level keys."""
    required = ["version", "odoo_version", "oca_repositories", "addon_roots"]
    for key in required:
        if key not in manifest:
            result.error(f"Missing required key: {key}")

    if manifest.get("version") != 2:
        result.error(f"Expected manifest version 2, got {manifest.get('version')}")

    if manifest.get("odoo_version") != "19.0":
        result.warn(f"Odoo version is {manifest.get('odoo_version')}, expected 19.0")

    result.log(f"Manifest version: {manifest.get('version')}")
    result.log(f"Odoo version: {manifest.get('odoo_version')}")


def validate_repo_sync(manifest: dict, result: ValidationResult) -> None:
    """Validate manifest repos match oca-aggregate.yml."""
    if not AGGREGATE_PATH.is_file():
        result.warn("oca-aggregate.yml not found — skipping sync check")
        return

    agg = load_yaml(AGGREGATE_PATH)
    agg_repos = extract_aggregate_repos(agg)

    manifest_repos = set()
    for entry in manifest.get("oca_repositories", []):
        manifest_repos.add(entry["repo"])

    # Repos in aggregate but not in manifest
    missing_in_manifest = agg_repos - manifest_repos
    for repo in sorted(missing_in_manifest):
        result.error(f"Repo in oca-aggregate.yml but not in manifest: {repo}")

    # Repos in manifest but not in aggregate
    extra_in_manifest = manifest_repos - agg_repos
    for repo in sorted(extra_in_manifest):
        result.error(f"Repo in manifest but not in oca-aggregate.yml: {repo}")

    result.log(f"OCA repos in manifest: {len(manifest_repos)}")
    result.log(f"OCA repos in aggregate: {len(agg_repos)}")
    if not missing_in_manifest and not extra_in_manifest:
        result.log("Manifest ↔ aggregate sync: OK")


def validate_no_duplicate_modules(result: ValidationResult, check_hydrated: bool) -> None:
    """Check for duplicate module names across OCA repos."""
    if not check_hydrated or not OCA_ROOT.is_dir():
        result.log("OCA not hydrated — skipping duplicate module check")
        return

    module_to_repos: dict[str, list[str]] = {}
    for repo_dir in sorted(OCA_ROOT.iterdir()):
        if not repo_dir.is_dir():
            continue
        repo_name = repo_dir.name
        for mod_dir in repo_dir.iterdir():
            if mod_dir.is_dir() and (mod_dir / "__manifest__.py").is_file():
                mod_name = mod_dir.name
                module_to_repos.setdefault(mod_name, []).append(repo_name)

    total_modules = sum(len(repos) for repos in module_to_repos.values())
    duplicates = {mod: repos for mod, repos in module_to_repos.items() if len(repos) > 1}

    for mod, repos in sorted(duplicates.items()):
        result.error(f"Duplicate module '{mod}' in repos: {', '.join(repos)}")

    result.log(f"Total OCA modules on disk: {total_modules}")
    if not duplicates:
        result.log("No duplicate module names found")


def validate_must_have_modules(manifest: dict, result: ValidationResult, check_hydrated: bool) -> None:
    """Check that must-have modules exist on disk."""
    if not check_hydrated or not OCA_ROOT.is_dir():
        result.log("OCA not hydrated — skipping must-have module check")
        return

    missing_count = 0
    found_count = 0

    for entry in manifest.get("oca_repositories", []):
        repo_name = entry["repo"]
        must_have = entry.get("must_have")
        if not must_have:
            continue

        repo_dir = OCA_ROOT / repo_name
        if not repo_dir.is_dir():
            result.error(f"Repo directory missing: addons/oca/{repo_name}")
            missing_count += len(must_have)
            continue

        disk_modules = find_modules_on_disk(repo_dir)
        for mod in must_have:
            if mod in disk_modules:
                found_count += 1
            else:
                result.error(f"Must-have module missing: {mod} (repo: {repo_name})")
                missing_count += 1

    result.log(f"Must-have modules found: {found_count}")
    if missing_count:
        result.log(f"Must-have modules missing: {missing_count}")
    else:
        result.log("All must-have modules present on disk")


def validate_ipai_modules(result: ValidationResult) -> None:
    """Check IPAI modules have valid __manifest__.py."""
    if not IPAI_ROOT.is_dir():
        result.warn("addons/ipai/ not found — skipping IPAI validation")
        return

    valid = 0
    invalid = 0

    for entry in sorted(IPAI_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name == "__pycache__":
            continue

        manifest_file = entry / "__manifest__.py"
        if not manifest_file.is_file():
            result.warn(f"IPAI dir without __manifest__.py: {entry.name}")
            invalid += 1
            continue

        # Check naming convention
        if not entry.name.startswith("ipai_") and not entry.name.startswith("cts_"):
            result.warn(f"Non-standard IPAI module name: {entry.name} (expected ipai_* or cts_*)")

        valid += 1

    result.log(f"IPAI modules with __manifest__.py: {valid}")
    if invalid:
        result.log(f"IPAI dirs without __manifest__.py: {invalid}")


def validate_dockerfile_path_order(result: ValidationResult) -> None:
    """Check Dockerfile addon path order matches SSOT invariant."""
    if not DOCKERFILE_PATH.is_file():
        result.warn("docker/Dockerfile.unified not found — skipping path order check")
        return

    content = DOCKERFILE_PATH.read_text()

    # Find ODOO_ADDONS_PATH line
    match = re.search(r"ODOO_ADDONS_PATH=(.+?)(?:\s|$)", content)
    if not match:
        result.error("ODOO_ADDONS_PATH not found in Dockerfile")
        return

    actual_paths = [p.strip() for p in match.group(1).split(",")]
    if actual_paths == EXPECTED_PATH_ORDER:
        result.log("Dockerfile addon path order: OK")
    else:
        result.error(
            f"Dockerfile addon path order mismatch.\n"
            f"    Expected: {','.join(EXPECTED_PATH_ORDER)}\n"
            f"    Actual:   {','.join(actual_paths)}"
        )


def validate_repo_entries(manifest: dict, result: ValidationResult) -> None:
    """Check each repo entry has required fields."""
    required_fields = ["repo", "url", "ref", "tier", "purpose"]

    for i, entry in enumerate(manifest.get("oca_repositories", [])):
        for field in required_fields:
            if field not in entry:
                result.error(f"Repo entry #{i} missing field: {field}")

        # Validate URL format
        url = entry.get("url", "")
        if url and not url.startswith("https://github.com/OCA/"):
            result.warn(f"Non-OCA URL for repo {entry.get('repo', '?')}: {url}")

        # Validate tier range
        tier = entry.get("tier")
        if tier is not None and (tier < 0 or tier > 9):
            result.error(f"Invalid tier {tier} for repo {entry.get('repo', '?')}")


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate addons manifest")
    parser.add_argument(
        "--check-hydrated",
        action="store_true",
        help="Also validate modules on disk (requires gitaggregate to have run)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show info-level messages",
    )
    args = parser.parse_args()

    result = ValidationResult()

    # Load manifest
    if not MANIFEST_PATH.is_file():
        print(f"ERROR: Manifest not found: {MANIFEST_PATH}", file=sys.stderr)
        return 2

    try:
        manifest = load_yaml(MANIFEST_PATH)
    except Exception as e:
        print(f"ERROR: Failed to parse manifest: {e}", file=sys.stderr)
        return 2

    # Run validators
    print("=" * 60)
    print("Addons Manifest Validation")
    print("=" * 60)

    validate_manifest_schema(manifest, result)
    validate_repo_entries(manifest, result)
    validate_repo_sync(manifest, result)
    validate_no_duplicate_modules(result, args.check_hydrated)
    validate_must_have_modules(manifest, result, args.check_hydrated)
    validate_ipai_modules(result)
    validate_dockerfile_path_order(result)

    # Output
    print()
    if args.verbose or not result.ok:
        print(result.summary())
        print()

    if result.ok:
        print(f"PASS — {len(result.info)} checks passed, {len(result.warnings)} warnings")
        return 0
    else:
        print(f"FAIL — {len(result.errors)} errors, {len(result.warnings)} warnings")
        return 1


if __name__ == "__main__":
    sys.exit(main())
