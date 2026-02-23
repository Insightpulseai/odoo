#!/usr/bin/env python3
"""
CI gate: enforce CE/EE edition policy.

Reads ODOO_INSTALL_MODULES (comma-separated list of Odoo module names to install)
and validates each against the deny list in spec/odoo/edition_policy.yaml.

If ODOO_INSTALL_MODULES is empty or unset the check is advisory (exit 0, skip msg).
The env var is set by installer jobs and release pipelines; in normal CI runs the
gate passes silently.

Exit codes:
  0 = clean (or ODOO_INSTALL_MODULES not set → advisory skip)
  1 = violation(s): EE-only modules in install target
  2 = configuration error (policy file missing or invalid YAML)

Usage:
  python3 scripts/policy/check_edition_policy.py

  # Advisory skip:
  ODOO_INSTALL_MODULES="" python3 scripts/policy/check_edition_policy.py

  # Violation example:
  ODOO_INSTALL_MODULES="documents,crm,sale" python3 scripts/policy/check_edition_policy.py

  # Clean example:
  ODOO_INSTALL_MODULES="crm,sale,project" python3 scripts/policy/check_edition_policy.py
"""

import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError as e:
    raise SystemExit("pyyaml missing. Run: pip install pyyaml") from e

# ---------------------------------------------------------------------------
# Paths (REPO_ROOT relative — mirrors check_custom_modules.py pattern)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.parent
POLICY_FILE = REPO_ROOT / "spec/odoo/edition_policy.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_policy() -> dict:
    if not POLICY_FILE.exists():
        print(f"❌ ERROR: Edition policy file not found: {POLICY_FILE}", file=sys.stderr)
        sys.exit(2)
    try:
        with POLICY_FILE.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not data:
            print(f"❌ ERROR: Edition policy file is empty: {POLICY_FILE}", file=sys.stderr)
            sys.exit(2)
        return data
    except yaml.YAMLError as e:
        print(f"❌ ERROR: Failed to parse edition policy: {e}", file=sys.stderr)
        sys.exit(2)


def parse_install_modules() -> list[str]:
    raw = os.environ.get("ODOO_INSTALL_MODULES", "")
    return [m.strip() for m in raw.split(",") if m.strip()]


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

def check_edition_policy() -> int:
    policy = load_policy()

    install_modules = parse_install_modules()
    if not install_modules:
        print("ℹ️  ODOO_INSTALL_MODULES not set or empty — edition policy check skipped (advisory).")
        return 0

    deny_list: list[dict] = policy.get("deny", [])
    deny_map = {entry["name"]: entry for entry in deny_list}
    deny_set = set(deny_map.keys())

    print(f"✅ Policy file: {POLICY_FILE.relative_to(REPO_ROOT)}")
    print(f"✅ SSOT reference: {policy.get('ssot_reference', '(none)')}")
    print()
    print(f"📦 Install target ({len(install_modules)} modules): {', '.join(install_modules)}")
    print(f"🚫 Deny list ({len(deny_set)} entries): {', '.join(sorted(deny_set))}")
    print()

    violations = []
    for mod in install_modules:
        if mod in deny_set:
            violations.append(mod)

    if not violations:
        print("✅ All modules pass edition policy — no EE-only modules in install target.")
        return 0

    print("❌ VIOLATION: EE-only module(s) in install target:\n")
    for mod in violations:
        entry = deny_map[mod]
        replace = entry.get("replace_with", {})
        oca_repo = replace.get("oca_repo")
        oca_modules = replace.get("modules", [])

        print(f"  ❌ {mod}")
        print(f"     Reason: {entry.get('reason', 'EE-only')}")
        if oca_repo:
            print(f"     OCA repo: {oca_repo}")
            if oca_modules:
                print(f"     Replace with: {', '.join(oca_modules)}")
        else:
            print(f"     Replacement: use module development + config-as-code")
        print()

    print("To fix:")
    print("  Remove the EE-only module(s) from your install target and use the OCA")
    print(f"  alternatives listed above. See policy: spec/odoo/edition_policy.yaml")
    print(f"  SSOT: {policy.get('ssot_reference', 'docs/architecture/ODOO_EDITIONS_SSOT.md')}")
    print()

    return 1


def main():
    sys.exit(check_edition_policy())


if __name__ == "__main__":
    main()
