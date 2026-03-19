#!/usr/bin/env python3
"""
CI gate: enforce IPAI custom modules policy.

Validates that all ipai_* modules in addons/ are either:
1. In the allowlist (spec/policy/ipai_custom_modules_policy.yaml)
2. Have an approved override (spec/policy/allow_custom_modules_override.yaml)

Exit codes:
  0 = all modules valid
  1 = validation errors (disallowed modules found)
  2 = configuration error
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent

# Policy files
POLICY_FILE = REPO_ROOT / "spec/policy/ipai_custom_modules_policy.yaml"
OVERRIDE_FILE = REPO_ROOT / "spec/policy/allow_custom_modules_override.yaml"

# Addons directory
ADDONS_DIR = REPO_ROOT / "addons"


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_allowed_modules(policy: dict) -> Set[str]:
    """Extract all allowed module IDs from policy."""
    allowed = set()

    for category_name, category_data in policy.get("allowed_categories", {}).items():
        for module in category_data.get("modules", []):
            allowed.add(module["id"])

    return allowed


def get_override_modules(overrides: dict) -> Set[str]:
    """Extract all override module IDs."""
    override_set = set()

    for override in overrides.get("overrides", []):
        override_set.add(override["module_id"])

    return override_set


def get_disallowed_patterns(policy: dict) -> List[dict]:
    """Extract disallowed patterns from policy."""
    return policy.get("disallowed_patterns", {}).get("patterns", [])


def find_ipai_modules() -> Set[str]:
    """Find all ipai_* modules in addons/."""
    if not ADDONS_DIR.exists():
        return set()

    ipai_modules = set()
    for item in ADDONS_DIR.iterdir():
        if item.is_dir() and item.name.startswith("ipai_"):
            # Check if it has __manifest__.py or __openerp__.py
            if (item / "__manifest__.py").exists() or (item / "__openerp__.py").exists():
                ipai_modules.add(item.name)

    return ipai_modules


def check_disallowed_patterns(module_id: str, patterns: List[dict]) -> Optional[dict]:
    """Check if module matches any disallowed pattern."""
    for pattern_def in patterns:
        pattern = pattern_def["pattern"]
        # Convert glob-style pattern to regex
        regex_pattern = pattern.replace("*", ".*")
        if re.match(f"^{regex_pattern}$", module_id):
            return pattern_def
    return None


def validate_modules() -> int:
    """
    Validate all ipai_* modules against policy.

    Returns:
        0 if valid, 1 if violations found, 2 if config error
    """
    # Load policy
    try:
        policy = load_yaml(POLICY_FILE)
        if not policy:
            print(f"❌ ERROR: Policy file not found or empty: {POLICY_FILE}", file=sys.stderr)
            return 2
    except Exception as e:
        print(f"❌ ERROR: Failed to load policy file: {e}", file=sys.stderr)
        return 2

    # Load overrides (optional)
    overrides = load_yaml(OVERRIDE_FILE)

    # Get allowed modules
    allowed_modules = get_allowed_modules(policy)
    override_modules = get_override_modules(overrides)
    all_allowed = allowed_modules | override_modules

    # Get disallowed patterns
    disallowed_patterns = get_disallowed_patterns(policy)

    # Find actual modules
    actual_modules = find_ipai_modules()

    # Validate
    violations = []
    pattern_violations = []

    for module_id in actual_modules:
        # Check if in allowlist or overrides
        if module_id not in all_allowed:
            violations.append(module_id)

        # Check disallowed patterns
        pattern_match = check_disallowed_patterns(module_id, disallowed_patterns)
        if pattern_match:
            pattern_violations.append(
                {
                    "module": module_id,
                    "pattern": pattern_match["pattern"],
                    "reason": pattern_match["reason"],
                    "alternatives": pattern_match.get("oca_alternatives", []),
                }
            )

    # Report results
    print(f"✅ Policy file: {POLICY_FILE}")
    print(f"✅ Override file: {OVERRIDE_FILE}")
    print(f"✅ Addons directory: {ADDONS_DIR}")
    print()
    print(f"📊 Found {len(actual_modules)} ipai_* modules")
    print(
        f"📊 Allowed modules: {len(allowed_modules)} (policy) + {len(override_modules)} (overrides)"
    )
    print()

    if not violations and not pattern_violations:
        print("✅ All ipai_* modules are valid!")
        print()
        print("Modules:")
        for module_id in sorted(actual_modules):
            source = "override" if module_id in override_modules else "policy"
            print(f"  ✅ {module_id} ({source})")
        return 0

    # Report violations
    if violations:
        print("❌ VIOLATION: Disallowed custom modules found:")
        print()
        for module_id in sorted(violations):
            print(f"  ❌ {module_id}")
            print(f"     Not in allowlist or overrides")
            print(f"     Add to spec/policy/allow_custom_modules_override.yaml with justification")
            print()

    if pattern_violations:
        print("❌ VIOLATION: Modules match disallowed patterns:")
        print()
        for violation in pattern_violations:
            print(f"  ❌ {violation['module']}")
            print(f"     Pattern: {violation['pattern']}")
            print(f"     Reason: {violation['reason']}")
            if violation["alternatives"]:
                print(f"     OCA alternatives: {', '.join(violation['alternatives'])}")
            print()

    print()
    print("To fix:")
    print("1. Remove disallowed modules, OR")
    print("2. Add override entry to spec/policy/allow_custom_modules_override.yaml with:")
    print("   - module_id")
    print(
        "   - category (platform_glue, ai_surface, compliance_local_overlays, design_system, data_contracts)"
    )
    print("   - justification (why OCA doesn't cover this)")
    print("   - decision_test_satisfied (all 5 criteria)")
    print("   - approved_by + approved_date")
    print()

    return 1


def main():
    """Main entry point."""
    exit_code = validate_modules()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
