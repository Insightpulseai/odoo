#!/usr/bin/env python3
"""
Odoo Addons Path Policy Validator

Validates that Odoo addons are placed in canonical locations only.
Prevents orphaned modules, nested addons, and non-standard paths.

Canonical Paths:
    - addons/ipai/<module>/     - IPAI custom modules
    - addons/OCA/<repo>/        - OCA repository checkouts
    - addons/oca/<submodule>/   - OCA git submodules

Usage:
    python validate_addons_path.py [--fix] [--verbose]

Exit Codes:
    0 - All addons in canonical paths
    1 - Policy violations found
    2 - Script execution error
"""

import argparse
import os
import sys
from pathlib import Path
from typing import NamedTuple, Optional


# ============================================================================
# Configuration
# ============================================================================

# Canonical addon base paths (relative to repo root)
CANONICAL_BASES = [
    "addons/ipai",
    "addons/OCA",
    "addons/oca",
]

# Paths that should NEVER contain addons
FORBIDDEN_ADDON_PATHS = [
    ".",              # Root directory
    "apps",           # Application code, not addons
    "packages",       # NPM packages
    "lib",            # Libraries
    "src",            # Source code
    "docker",         # Docker configs
    "scripts",        # Scripts
    "docs",           # Documentation
    "tests",          # Top-level tests
    ".github",        # GitHub workflows
    "node_modules",   # NPM modules
    "spec",           # Specifications
    "sandbox",        # Sandbox/experimental
]

# Directories to skip entirely during scanning
SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".github",
    "node_modules",
    ".venv",
    "venv",
    ".eggs",
    "dist",
    "build",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    ".turbo",
}

# Maximum nesting depth for addons
MAX_ADDON_DEPTH = 3  # e.g., addons/OCA/server-tools/module_name


# ============================================================================
# Result Types
# ============================================================================

class PolicyViolation(NamedTuple):
    """A policy violation found during scanning."""
    severity: str  # "error", "warning"
    path: str
    message: str
    suggestion: str


class PolicyReport(NamedTuple):
    """Complete policy validation report."""
    violations: list
    orphaned_modules: list
    nested_addons: list
    modules_in_canonical: int


# ============================================================================
# Detection Functions
# ============================================================================

def find_repo_root() -> Path:
    """Find the repository root by looking for .git directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def should_skip_dir(dirname: str) -> bool:
    """Check if directory should be skipped during scanning."""
    if dirname in SKIP_DIRS:
        return True
    if dirname.startswith("."):
        return True
    if dirname.endswith(".egg-info"):
        return True
    return False


def is_odoo_module(path: Path) -> bool:
    """Check if a directory is an Odoo module."""
    return (path / "__manifest__.py").exists() or (path / "__openerp__.py").exists()


def is_in_canonical_path(module_path: Path, repo_root: Path) -> bool:
    """Check if module is in a canonical addon path."""
    try:
        rel_path = module_path.relative_to(repo_root)
    except ValueError:
        return False

    rel_str = str(rel_path)
    for base in CANONICAL_BASES:
        if rel_str.startswith(base + "/"):
            return True
    return False


def get_canonical_suggestion(module_path: Path, repo_root: Path) -> str:
    """Suggest the correct canonical path for a module."""
    module_name = module_path.name

    # Determine if it looks like an OCA module or IPAI module
    if module_name.startswith("ipai_"):
        return f"addons/ipai/{module_name}/"
    elif module_name.startswith("l10n_") or module_name.startswith("account_"):
        return f"addons/OCA/<appropriate-repo>/{module_name}/"
    else:
        return f"addons/ipai/{module_name}/ or addons/OCA/<repo>/{module_name}/"


def get_nesting_depth(module_path: Path, repo_root: Path) -> int:
    """Calculate how deep a module is nested."""
    try:
        rel_path = module_path.relative_to(repo_root)
        return len(rel_path.parts)
    except ValueError:
        return 999  # Very deep if can't calculate


def is_canonical_base(path: Path, repo_root: Path) -> bool:
    """Check if a path is a canonical addon base directory."""
    try:
        rel_path = str(path.relative_to(repo_root))
        return rel_path in CANONICAL_BASES
    except ValueError:
        return False


def check_nested_addon(module_path: Path, repo_root: Path) -> Optional[PolicyViolation]:
    """Check if a module is nested inside another module (addon within addon).

    Note: Canonical base directories (addons/ipai, addons/oca, addons/OCA) are allowed
    to have __manifest__.py files as namespace modules without triggering nesting errors.
    """
    current = module_path.parent
    while current != repo_root and current != current.parent:
        # Skip nesting check if current directory is a canonical base
        if is_canonical_base(current, repo_root):
            current = current.parent
            continue
        if is_odoo_module(current):
            return PolicyViolation(
                severity="error",
                path=str(module_path.relative_to(repo_root)),
                message=f"Module is nested inside another module: {current.relative_to(repo_root)}",
                suggestion="Move to a flat structure under addons/ipai/ or addons/OCA/<repo>/"
            )
        current = current.parent
    return None


def scan_for_modules(start_path: Path, repo_root: Path, max_depth: int = 10) -> list:
    """Recursively scan for Odoo modules starting from a path."""
    modules = []

    if max_depth <= 0:
        return modules

    if not start_path.is_dir():
        return modules

    try:
        for item in start_path.iterdir():
            if not item.is_dir():
                continue
            if should_skip_dir(item.name):
                continue

            if is_odoo_module(item):
                modules.append(item)
                # Don't scan inside modules (would find nested addons)
            else:
                # Recurse into subdirectories
                modules.extend(scan_for_modules(item, repo_root, max_depth - 1))
    except PermissionError:
        pass

    return modules


def scan_forbidden_paths(repo_root: Path) -> list:
    """Scan forbidden paths for misplaced addons."""
    orphaned = []

    for forbidden_rel in FORBIDDEN_ADDON_PATHS:
        if forbidden_rel == ".":
            # Check root directory only (not recursively)
            for item in repo_root.iterdir():
                if item.is_dir() and not should_skip_dir(item.name):
                    if is_odoo_module(item):
                        orphaned.append(item)
        else:
            forbidden_path = repo_root / forbidden_rel
            if forbidden_path.exists() and forbidden_path.is_dir():
                # Scan this path for modules
                modules = scan_for_modules(forbidden_path, repo_root, max_depth=5)
                orphaned.extend(modules)

    return orphaned


def scan_canonical_paths(repo_root: Path) -> tuple:
    """Scan canonical paths and check for issues."""
    modules_in_canonical = 0
    nested_addons = []

    for base_rel in CANONICAL_BASES:
        base_path = repo_root / base_rel
        if not base_path.exists():
            continue

        modules = scan_for_modules(base_path, repo_root, max_depth=MAX_ADDON_DEPTH)

        for module in modules:
            modules_in_canonical += 1

            # Check for nested addon
            nested_violation = check_nested_addon(module, repo_root)
            if nested_violation:
                nested_addons.append(nested_violation)

            # Check depth
            depth = get_nesting_depth(module, repo_root)
            if depth > MAX_ADDON_DEPTH + 1:  # +1 for the module itself
                nested_addons.append(PolicyViolation(
                    severity="warning",
                    path=str(module.relative_to(repo_root)),
                    message=f"Module is nested too deep ({depth} levels)",
                    suggestion="Consider flattening the directory structure"
                ))

    return modules_in_canonical, nested_addons


def run_policy_check(repo_root: Path) -> PolicyReport:
    """Run full policy validation."""
    violations = []

    # Scan forbidden paths for orphaned modules
    orphaned_modules = scan_forbidden_paths(repo_root)

    for orphan in orphaned_modules:
        rel_path = orphan.relative_to(repo_root)
        violations.append(PolicyViolation(
            severity="error",
            path=str(rel_path),
            message="Module found outside canonical addon paths",
            suggestion=get_canonical_suggestion(orphan, repo_root)
        ))

    # Scan canonical paths for issues
    modules_in_canonical, nested_addons = scan_canonical_paths(repo_root)

    # Add nested addon violations
    violations.extend(nested_addons)

    return PolicyReport(
        violations=violations,
        orphaned_modules=[str(m.relative_to(repo_root)) for m in orphaned_modules],
        nested_addons=[v.path for v in nested_addons if v.severity == "error"],
        modules_in_canonical=modules_in_canonical
    )


# ============================================================================
# Output Formatting
# ============================================================================

def format_violation(violation: PolicyViolation) -> str:
    """Format a single violation for output."""
    icons = {"error": "❌", "warning": "⚠️"}
    icon = icons.get(violation.severity, "•")
    lines = [
        f"  {icon} [{violation.severity.upper()}] {violation.path}",
        f"     Message: {violation.message}",
        f"     Suggestion: {violation.suggestion}"
    ]
    return "\n".join(lines)


def print_report(report: PolicyReport, verbose: bool = False) -> None:
    """Print policy validation report."""
    print("\n" + "=" * 70)
    print("Odoo Addons Path Policy Report")
    print("=" * 70)

    print(f"\nModules in canonical paths: {report.modules_in_canonical}")

    if report.orphaned_modules:
        print(f"\n🔴 ORPHANED MODULES ({len(report.orphaned_modules)}):")
        print("   These modules are outside canonical addon paths:")
        for path in report.orphaned_modules:
            print(f"     - {path}")

    if report.nested_addons:
        print(f"\n🔴 NESTED ADDONS ({len(report.nested_addons)}):")
        print("   These modules are incorrectly nested inside other modules:")
        for path in report.nested_addons:
            print(f"     - {path}")

    errors = [v for v in report.violations if v.severity == "error"]
    warnings = [v for v in report.violations if v.severity == "warning"]

    if verbose and report.violations:
        print(f"\n📋 DETAILED VIOLATIONS ({len(report.violations)}):")
        for violation in report.violations:
            print(format_violation(violation))

    print("\n" + "-" * 70)
    print(f"Canonical addon bases: {', '.join(CANONICAL_BASES)}")

    if errors:
        print(f"\n❌ FAILED: {len(errors)} policy error(s) found")
    elif warnings:
        print(f"\n⚠️ PASSED with {len(warnings)} warning(s)")
    else:
        print("\n✅ PASSED: All addons in canonical paths")
    print("-" * 70 + "\n")


# ============================================================================
# CLI
# ============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Odoo addons path policy"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed violation information"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show errors (suppress warnings)"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (auto-detected if not specified)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    # Find repo root
    if args.root:
        repo_root = args.root
    else:
        repo_root = find_repo_root()

    print(f"Scanning: {repo_root}")

    # Run policy check
    try:
        report = run_policy_check(repo_root)
    except Exception as e:
        print(f"❌ Policy check failed with error: {e}", file=sys.stderr)
        return 2

    # Print report
    if not args.quiet:
        print_report(report, verbose=args.verbose)
    elif report.violations:
        errors = [v for v in report.violations if v.severity == "error"]
        for error in errors:
            print(f"❌ {error.path}: {error.message}")

    # Exit code
    errors = [v for v in report.violations if v.severity == "error"]
    warnings = [v for v in report.violations if v.severity == "warning"]

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
