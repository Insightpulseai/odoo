#!/usr/bin/env python3
"""
CI gate: enforce CE/EE edition policy.

Reads ODOO_INSTALL_MODULES (comma-separated list of Odoo module names to install)
and validates each against the deny list + optional known-targets allowlist in
spec/odoo/edition_policy.yaml.

Three-layer check (applied in order):
  1. Alias normalization — maps variants (field-service, Field Service, …) to
     canonical names defined in the policy `aliases:` section.
  2. Deny check — always runs; catches EE-only modules with OCA replacement hints.
  3. Known-targets check — optional strict mode; fails on any unrecognised target.
     Enabled by:
       a) `strict.known_targets_enforced: true` in policy YAML, OR
       b) env var EDITION_POLICY_ENFORCE_KNOWN_TARGETS=1 (overrides YAML flag)

If ODOO_INSTALL_MODULES is empty or unset the check is advisory (exit 0, skip msg).
The env var is set by installer jobs and release pipelines; in normal CI runs the
gate passes silently.

Exit codes:
  0 = clean (or ODOO_INSTALL_MODULES not set → advisory skip)
  1 = violation(s): denied EE-only modules or unknown targets (strict mode)
  2 = configuration error (policy file missing or invalid YAML)

Examples:
  # Advisory skip:
  ODOO_INSTALL_MODULES="" python3 scripts/policy/check_edition_policy.py

  # Violation — EE-only module:
  ODOO_INSTALL_MODULES="documents,crm" python3 scripts/policy/check_edition_policy.py

  # Violation — alias variant:
  ODOO_INSTALL_MODULES="field-service,crm" python3 scripts/policy/check_edition_policy.py

  # Strict mode — unknown module:
  EDITION_POLICY_ENFORCE_KNOWN_TARGETS=1 ODOO_INSTALL_MODULES="crm,typo_mod" \\
    python3 scripts/policy/check_edition_policy.py

  # Clean:
  ODOO_INSTALL_MODULES="crm,sale,stock,project,hr" python3 scripts/policy/check_edition_policy.py
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
# Policy loader
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


# ---------------------------------------------------------------------------
# Alias normalization
# ---------------------------------------------------------------------------

def normalize_target(raw: str, aliases: dict) -> str:
    """
    Normalize an install target to its canonical name:
      1. Lowercase
      2. Trim leading/trailing whitespace
      3. Collapse internal whitespace to single spaces
      4. Apply aliases mapping from policy (SSOT)

    Examples:
      "Field Service"  → "field_service"
      "field-service"  → "field_service"
      "HELPDESK"       → "helpdesk"
      "crm"            → "crm"  (unchanged)
    """
    normalized = " ".join(raw.strip().lower().split())
    return aliases.get(normalized, normalized)


# ---------------------------------------------------------------------------
# Install module parser
# ---------------------------------------------------------------------------

def parse_install_modules() -> list[str]:
    raw = os.environ.get("ODOO_INSTALL_MODULES", "")
    return [m.strip() for m in raw.split(",") if m.strip()]


# ---------------------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------------------

def check_edition_policy() -> int:
    policy = load_policy()

    # --- resolve config -----------------------------------------------------
    aliases: dict = policy.get("aliases") or {}
    deny_list: list[dict] = policy.get("deny") or []
    deny_map = {entry["name"]: entry for entry in deny_list}
    deny_set = set(deny_map.keys())

    strict_cfg: dict = policy.get("strict") or {}
    enforce_known: bool = bool(strict_cfg.get("known_targets_enforced", False))
    # env override: EDITION_POLICY_ENFORCE_KNOWN_TARGETS=1|true|yes|on
    env_override = os.environ.get("EDITION_POLICY_ENFORCE_KNOWN_TARGETS", "").strip().lower()
    if env_override in ("1", "true", "yes", "on"):
        enforce_known = True

    known_targets: set = set(policy.get("known_targets") or [])

    # --- parse install target ------------------------------------------------
    install_modules = parse_install_modules()
    if not install_modules:
        print("ℹ️  ODOO_INSTALL_MODULES not set or empty — edition policy check skipped (advisory).")
        return 0

    print(f"✅ Policy file: {POLICY_FILE.relative_to(REPO_ROOT)}")
    print(f"✅ SSOT reference: {policy.get('ssot_reference', '(none)')}")
    print(f"✅ Strict mode: {'ON' if enforce_known else 'OFF (advisory)'}")
    print()
    print(f"📦 Install target ({len(install_modules)} modules): {', '.join(install_modules)}")
    print(f"🚫 Deny list ({len(deny_set)} entries): {', '.join(sorted(deny_set))}")
    print()

    # --- normalize all targets -----------------------------------------------
    normalized: list[tuple[str, str]] = []
    for raw in install_modules:
        canonical = normalize_target(raw, aliases)
        normalized.append((raw, canonical))
        if raw != canonical:
            print(f"  🔀 Alias: '{raw}' → '{canonical}'")

    # --- deny check (always runs) --------------------------------------------
    violations: list[str] = []
    for raw, t in normalized:
        if t in deny_set:
            entry = deny_map[t]
            replace = entry.get("replace_with") or {}
            oca_repo = replace.get("oca_repo")
            oca_modules = replace.get("modules") or []
            alias_note = f" (from '{raw}')" if raw != t else ""
            violations.append((t, alias_note, entry, oca_repo, oca_modules))

    # --- known-targets check (strict mode) -----------------------------------
    unknowns: list[tuple[str, str]] = []
    if enforce_known and known_targets:
        for raw, t in normalized:
            # denied modules are in known_targets; skip so deny message fires instead
            if t not in known_targets and t not in deny_set:
                unknowns.append((raw, t))

    # --- report results ------------------------------------------------------
    if not violations and not unknowns:
        print("✅ All modules pass edition policy — no EE-only modules in install target.")
        return 0

    exit_code = 1

    if unknowns:
        print("❌ UNKNOWN: Modules not in known_targets (strict mode active):\n")
        for raw, t in unknowns:
            alias_note = f" (from '{raw}')" if raw != t else ""
            print(f"  ❓ {t}{alias_note}")
            print(f"     Add to known_targets in spec/odoo/edition_policy.yaml if this is a valid CE/OCA module.")
            print()

    if violations:
        print("❌ VIOLATION: EE-only module(s) in install target:\n")
        for t, alias_note, entry, oca_repo, oca_modules in violations:
            print(f"  ❌ {t}{alias_note}")
            print(f"     Reason: {entry.get('reason', 'EE-only')}")
            if oca_repo:
                print(f"     OCA repo: {oca_repo}")
                if oca_modules:
                    print(f"     Replace with: {', '.join(oca_modules)}")
            else:
                print(f"     Replacement: use module development + config-as-code")
            print()

    print("To fix:")
    if violations:
        print("  Remove the EE-only module(s) from your install target and use the OCA")
        print(f"  alternatives listed above.")
    if unknowns:
        print("  Add unknown modules to known_targets in the policy, OR remove them from")
        print(f"  ODOO_INSTALL_MODULES if they are typos.")
    print(f"  See policy: spec/odoo/edition_policy.yaml")
    print(f"  SSOT: {policy.get('ssot_reference', 'docs/architecture/ODOO_EDITIONS_SSOT.md')}")
    print()

    return exit_code


def main():
    sys.exit(check_edition_policy())


if __name__ == "__main__":
    main()
