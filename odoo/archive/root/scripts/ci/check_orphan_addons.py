#!/usr/bin/env python3
"""
check_orphan_addons.py — Orphan addons gate.

Detects `addons/ipai_*` directories at the REPO ROOT that are NOT in the
canonical addons-path (`addons/ipai/`).  These modules are invisible to Odoo
and accumulate silently.

Any such directory must be:
  a) Moved to `addons/ipai/<module_name>/` (preferred), OR
  b) Listed in `ssot/odoo/orphan_addons_allowlist.yaml` with a migration plan.

Exit codes:
  0 — PASS: no unlisted orphans found
  2 — ERROR: allowlist file missing or YAML parse error
  3 — FAIL: unlisted orphan directories found

SSOT: ssot/odoo/orphan_addons_allowlist.yaml
Rule: CLAUDE.md §Module Philosophy — addons-path is addons/ipai/ only.

Usage:
  python3 scripts/ci/check_orphan_addons.py [--repo-root PATH]
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ALLOWLIST_REL = "ssot/odoo/orphan_addons_allowlist.yaml"
SCHEMA_EXPECTED = "ssot.odoo.orphan_addons_allowlist.v1"
VERSION_EXPECTED = "1.0"
ADDONS_ROOT_REL = "addons"
CANONICAL_DIR = "ipai"  # addons/ipai/ is the canonical destination


def load_allowlist(allowlist_path: Path) -> list[str]:
    """Load and validate the allowlist YAML.  Returns list of allowed module names."""
    if not allowlist_path.exists():
        print(f"ERROR: Allowlist file not found: {allowlist_path}", file=sys.stderr)
        print(
            f"  Create it with: schema: {SCHEMA_EXPECTED}",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        with open(allowlist_path) as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: YAML parse error in {allowlist_path}: {exc}", file=sys.stderr)
        sys.exit(2)

    # Schema check
    schema = data.get("schema")
    if schema != SCHEMA_EXPECTED:
        print(
            f"ERROR: {allowlist_path}: expected schema={SCHEMA_EXPECTED!r}, "
            f"got {schema!r}",
            file=sys.stderr,
        )
        sys.exit(2)

    version = str(data.get("version", ""))
    if version != VERSION_EXPECTED:
        print(
            f"ERROR: {allowlist_path}: expected version={VERSION_EXPECTED!r}, "
            f"got {version!r}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Unknown top-level keys check
    allowed_keys = {"schema", "version", "notes", "modules"}
    unknown = set(data.keys()) - allowed_keys
    if unknown:
        print(
            f"ERROR: {allowlist_path}: unknown top-level keys: {sorted(unknown)}",
            file=sys.stderr,
        )
        sys.exit(2)

    modules = data.get("modules") or []
    if not isinstance(modules, list):
        print(
            f"ERROR: {allowlist_path}: 'modules' must be a list",
            file=sys.stderr,
        )
        sys.exit(2)

    # Validate each module entry
    allowed_module_keys = {"name", "reason", "migration_target", "ticket"}
    names = []
    seen = set()
    for i, entry in enumerate(modules):
        if not isinstance(entry, dict):
            print(
                f"ERROR: {allowlist_path}: modules[{i}] must be a mapping",
                file=sys.stderr,
            )
            sys.exit(2)
        unknown_mod = set(entry.keys()) - allowed_module_keys
        if unknown_mod:
            print(
                f"ERROR: {allowlist_path}: modules[{i}] has unknown keys: "
                f"{sorted(unknown_mod)}",
                file=sys.stderr,
            )
            sys.exit(2)
        name = entry.get("name")
        if not name:
            print(
                f"ERROR: {allowlist_path}: modules[{i}] missing 'name' field",
                file=sys.stderr,
            )
            sys.exit(2)
        if name in seen:
            print(
                f"ERROR: {allowlist_path}: duplicate module name: {name!r}",
                file=sys.stderr,
            )
            sys.exit(2)
        if not entry.get("reason"):
            print(
                f"ERROR: {allowlist_path}: modules[{i}] ({name!r}) missing 'reason' field",
                file=sys.stderr,
            )
            sys.exit(2)
        seen.add(name)
        names.append(name)

    return names


def find_orphans(addons_root: Path) -> list[str]:
    """Return sorted list of ipai_* directory names at addons/ root (not in addons/ipai/)."""
    if not addons_root.is_dir():
        return []
    orphans = []
    for entry in sorted(addons_root.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith("ipai_") and name != CANONICAL_DIR:
            orphans.append(name)
    return orphans


def main() -> int:
    parser = argparse.ArgumentParser(description="Orphan addons gate")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: current directory)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    allowlist_path = repo_root / ALLOWLIST_REL
    addons_root = repo_root / ADDONS_ROOT_REL

    allowlist = load_allowlist(allowlist_path)
    allowlist_set = set(allowlist)

    orphans = find_orphans(addons_root)

    unlisted = [m for m in orphans if m not in allowlist_set]
    allowlisted = [m for m in orphans if m in allowlist_set]

    if unlisted:
        print(
            f"\nFAIL: orphan-addons-gate — {len(unlisted)} unlisted orphan "
            f"director{'y' if len(unlisted) == 1 else 'ies'} in {ADDONS_ROOT_REL}/\n"
        )
        print(
            "  These modules are invisible to Odoo (not in addons-path).\n"
            "  Action required (choose one):\n"
            f"    a) Move to addons/ipai/<module_name>/  (preferred)\n"
            f"    b) Add to {ALLOWLIST_REL} with 'reason' + 'migration_target'\n"
        )
        for m in unlisted:
            print(f"  ORPHAN: addons/{m}/")

        print(
            f"\n  Allowlisted orphans (not failing): {len(allowlisted)}\n"
            f"  Unlisted orphans (FAILING):        {len(unlisted)}\n"
            f"  Total orphans found:               {len(orphans)}\n"
        )
        return 3

    # All orphans are accounted for
    n = len(orphans)
    print(
        f"PASS: orphan-addons-gate — "
        f"{n} orphan director{'y' if n == 1 else 'ies'} found, "
        f"all allowlisted ({ALLOWLIST_REL})"
    )
    if orphans:
        print(
            f"\n  ⚠ {n} legacy orphan(s) still pending migration to addons/ipai/:"
        )
        for m in allowlisted:
            print(f"    addons/{m}/")
        print(
            "\n  These are allowlisted legacy directories.\n"
            "  Open a follow-up PR to migrate them to addons/ipai/.\n"
        )
    else:
        print("  No orphan directories exist — addons/ is clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
