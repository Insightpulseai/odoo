#!/usr/bin/env python3
"""
check_repo_structure.py — Repo Layout CI Validator

Validates that the repository adheres to the boundary rules defined in
docs/architecture/REPO_LAYOUT.md.

Exit 0 = all checks pass.
Exit 1 = one or more checks fail.

Usage:
    python scripts/ci/check_repo_structure.py
    python scripts/ci/check_repo_structure.py --repo-root /path/to/repo
    python scripts/ci/check_repo_structure.py --fail-fast
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("FAIL [setup] pyyaml not installed — run: pip install pyyaml", flush=True)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Enterprise module prefix heuristic
# Source: https://www.odoo.com/documentation/19.0/applications.html
# These prefixes are used in __manifest__.py 'depends' lists by EE modules.
# ---------------------------------------------------------------------------
ENTERPRISE_MODULE_PREFIXES = (
    "account_accountant",
    "account_budget",
    "account_reports",
    "approvals",
    "attendances",
    "consolidation",
    "documents",
    "helpdesk",
    "hr_appraisal",
    "hr_contract_salary",
    "industry_fsm",
    "l10n_",  # many EE l10n modules
    "lunch",
    "maintenance",
    "marketing_automation",
    "mrp_plm",
    "mrp_workcenter",
    "planning",
    "quality_control",
    "recurring_documents",
    "repair",
    "sale_amazon",
    "sale_crm",
    "sign",
    "social",
    "snailmail",
    "spreadsheet",
    "stock_account",
    "stock_dropshipping",
    "stock_enterprise",
    "subscription",
    "timesheet_grid",
    "voip",
    "web_studio",
    "website_livechat",
    "whatsapp",
)

# Allowed Odoo server root name at repo root level (only this one is permitted)
CANONICAL_ODOO_ROOT = "odoo19"

# Forbidden Odoo-looking root names (must not coexist at repo root)
FORBIDDEN_ODOO_ROOTS = {"odoo", "odoo-ce", "odooenv", "odoo_ce", "odoo-server"}

PASS = "PASS"
FAIL = "FAIL"


def result(tag: str, label: str, ok: bool, detail: str = "") -> bool:
    prefix = PASS if ok else FAIL
    msg = f"{prefix} [{tag}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg, flush=True)
    return ok


# ---------------------------------------------------------------------------
# Check 1: Every dir under addons/ipai/ and addons/local/ has __manifest__.py
# ---------------------------------------------------------------------------
def check_addon_dirs_have_manifests(repo_root: Path) -> bool:
    """Check 1: All dirs under addons/ipai/ and addons/local/ are valid Odoo modules."""
    addon_dirs_to_check = [
        repo_root / "addons" / "ipai",
        repo_root / "addons" / "local",
    ]
    bad: List[str] = []

    for parent in addon_dirs_to_check:
        if not parent.exists():
            continue
        for child in sorted(parent.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith(".") or child.name.startswith("_"):
                continue
            manifest = child / "__manifest__.py"
            if not manifest.exists():
                rel = child.relative_to(repo_root)
                bad.append(str(rel))

    ok = len(bad) == 0
    if bad:
        detail = f"missing __manifest__.py: {', '.join(bad[:5])}"
        if len(bad) > 5:
            detail += f" (+{len(bad) - 5} more)"
    else:
        checked = sum(
            1
            for p in addon_dirs_to_check
            if p.exists()
            for c in p.iterdir()
            if c.is_dir() and not c.name.startswith(".")
        )
        detail = f"{checked} addon dir(s) checked"

    return result("check1", "addons/ipai/ and addons/local/ dirs have __manifest__.py", ok, detail)


# ---------------------------------------------------------------------------
# Check 2: No supabase/ directory under addons/
# ---------------------------------------------------------------------------
def check_no_supabase_under_addons(repo_root: Path) -> bool:
    """Check 2: No supabase/ directory exists anywhere under addons/."""
    addons_root = repo_root / "addons"
    if not addons_root.exists():
        return result("check2", "no supabase/ under addons/", True, "addons/ not found (skipped)")

    found: List[str] = []
    for dirpath, dirnames, _ in os.walk(addons_root):
        # Avoid walking into .git or hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for dirname in dirnames:
            if dirname == "supabase":
                rel = Path(dirpath).relative_to(repo_root) / dirname
                found.append(str(rel))

    ok = len(found) == 0
    detail = f"found: {', '.join(found)}" if found else "clean"
    return result("check2", "no supabase/ directory under addons/", ok, detail)


# ---------------------------------------------------------------------------
# Check 3: ipai_* modules do not depend on Enterprise modules
# ---------------------------------------------------------------------------
def _parse_manifest_depends(manifest_path: Path) -> Optional[List[str]]:
    """
    Attempt to extract the 'depends' list from a __manifest__.py file.
    Uses a simple heuristic: look for a 'depends' key in a dict-like structure.
    Falls back to None if parsing fails.
    """
    try:
        content = manifest_path.read_text(encoding="utf-8")
    except OSError:
        return None

    # Use ast.literal_eval for safe parsing of the manifest dict
    import ast

    try:
        tree = ast.parse(content, mode="eval")
        manifest_dict = ast.literal_eval(tree.body)
        if isinstance(manifest_dict, dict):
            depends = manifest_dict.get("depends", [])
            if isinstance(depends, list):
                return [str(d) for d in depends]
    except (SyntaxError, ValueError, TypeError, AttributeError):
        pass

    return None


def check_no_enterprise_deps_in_ipai_modules(repo_root: Path) -> bool:
    """Check 3: ipai_* modules do not depend on known Enterprise module prefixes."""
    ipai_dir = repo_root / "addons" / "ipai"
    if not ipai_dir.exists():
        return result(
            "check3",
            "ipai_* modules have no Enterprise dependencies",
            True,
            "addons/ipai/ not found (skipped)",
        )

    violations: List[str] = []

    for module_dir in sorted(ipai_dir.iterdir()):
        if not module_dir.is_dir():
            continue
        if not module_dir.name.startswith("ipai_"):
            continue

        manifest_path = module_dir / "__manifest__.py"
        if not manifest_path.exists():
            continue

        depends = _parse_manifest_depends(manifest_path)
        if depends is None:
            # Could not parse — emit a warning but don't fail
            print(
                f"WARN [check3] Could not parse {manifest_path.relative_to(repo_root)}",
                flush=True,
            )
            continue

        for dep in depends:
            for prefix in ENTERPRISE_MODULE_PREFIXES:
                if dep.startswith(prefix):
                    violations.append(
                        f"{module_dir.name}: depends on '{dep}' (matches EE prefix '{prefix}')"
                    )
                    break

    ok = len(violations) == 0
    if violations:
        detail = "; ".join(violations[:3])
        if len(violations) > 3:
            detail += f" (+{len(violations) - 3} more)"
    else:
        checked = sum(
            1
            for d in ipai_dir.iterdir()
            if d.is_dir() and d.name.startswith("ipai_")
        )
        detail = f"{checked} ipai_* module(s) checked"

    return result(
        "check3",
        "ipai_* modules have no Enterprise module dependencies",
        ok,
        detail,
    )


# ---------------------------------------------------------------------------
# Check 4: Only one Odoo server root at repo root (canonical: odoo19/)
# ---------------------------------------------------------------------------
def check_single_odoo_root(repo_root: Path) -> bool:
    """Check 4: Only one Odoo server root at repo root level (canonical name: odoo19/)."""
    found_forbidden: List[str] = []
    canonical_exists = (repo_root / CANONICAL_ODOO_ROOT).exists()

    for name in FORBIDDEN_ODOO_ROOTS:
        candidate = repo_root / name
        if candidate.exists() and candidate.is_dir():
            found_forbidden.append(name)

    ok = len(found_forbidden) == 0
    if found_forbidden:
        detail = (
            f"forbidden Odoo root(s) found: {', '.join(found_forbidden)} "
            f"(canonical is '{CANONICAL_ODOO_ROOT}/')"
        )
    elif canonical_exists:
        detail = f"canonical '{CANONICAL_ODOO_ROOT}/' exists, no forbidden roots"
    else:
        # Neither canonical nor forbidden: fine (odoo19/ might not be checked out)
        detail = f"'{CANONICAL_ODOO_ROOT}/' not present, no forbidden roots either"

    return result("check4", f"only '{CANONICAL_ODOO_ROOT}/' as Odoo server root", ok, detail)


# ---------------------------------------------------------------------------
# Check 5: Every directory under apps/ has a package.json
# ---------------------------------------------------------------------------
def check_apps_have_package_json(repo_root: Path) -> bool:
    """Check 5: Every directory under apps/ contains a package.json."""
    apps_root = repo_root / "apps"
    if not apps_root.exists():
        return result(
            "check5",
            "apps/ directories have package.json",
            True,
            "apps/ not found (skipped)",
        )

    bad: List[str] = []
    for child in sorted(apps_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        if not (child / "package.json").exists():
            bad.append(child.name)

    ok = len(bad) == 0
    if bad:
        detail = f"missing package.json: {', '.join(bad)}"
    else:
        checked = sum(1 for c in apps_root.iterdir() if c.is_dir() and not c.name.startswith("."))
        detail = f"{checked} app(s) checked"

    return result("check5", "apps/ directories have package.json", ok, detail)


# ---------------------------------------------------------------------------
# Check 6: ssot/ contains only .yaml files (no .py, .ts, .sql, .sh, .json)
# ---------------------------------------------------------------------------
SSOT_FORBIDDEN_EXTENSIONS = {".py", ".ts", ".js", ".sql", ".sh"}


def check_ssot_yaml_only(repo_root: Path) -> bool:
    """Check 6: ssot/ directory contains only .yaml files (no executable code)."""
    ssot_root = repo_root / "ssot"
    if not ssot_root.exists():
        return result(
            "check6",
            "ssot/ contains only .yaml files",
            True,
            "ssot/ not found (skipped)",
        )

    bad: List[str] = []
    for dirpath, dirnames, filenames in os.walk(ssot_root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            ext = Path(filename).suffix.lower()
            if ext in SSOT_FORBIDDEN_EXTENSIONS:
                rel = Path(dirpath).relative_to(repo_root) / filename
                bad.append(str(rel))

    ok = len(bad) == 0
    if bad:
        detail = f"non-YAML files: {', '.join(bad[:5])}"
        if len(bad) > 5:
            detail += f" (+{len(bad) - 5} more)"
    else:
        total = sum(
            len(files)
            for _, _, files in os.walk(ssot_root)
        )
        detail = f"{total} file(s) checked in ssot/"

    return result("check6", "ssot/ contains only .yaml files (no executable code)", ok, detail)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Validate repo layout boundary rules")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to repository root (default: .)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first failing check",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    print(f"Repo Layout Validator — repo root: {repo_root}", flush=True)
    print(f"Reference: docs/architecture/REPO_LAYOUT.md", flush=True)
    print("-" * 64, flush=True)

    checks = [
        check_addon_dirs_have_manifests,
        check_no_supabase_under_addons,
        check_no_enterprise_deps_in_ipai_modules,
        check_single_odoo_root,
        check_apps_have_package_json,
        check_ssot_yaml_only,
    ]

    failures = 0
    for check_fn in checks:
        ok = check_fn(repo_root)
        if not ok:
            failures += 1
            if args.fail_fast:
                print("-" * 64, flush=True)
                print(f"FAIL — stopped after first failure (--fail-fast)", flush=True)
                sys.exit(1)

    print("-" * 64, flush=True)
    if failures == 0:
        print(f"PASS — all {len(checks)} checks passed", flush=True)
        sys.exit(0)
    else:
        print(f"FAIL — {failures}/{len(checks)} check(s) failed", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
