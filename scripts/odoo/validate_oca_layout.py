#!/usr/bin/env python3
"""
Odoo/OCA Layout Validator

Deterministic validation of Odoo addon directory structure and naming conventions.
Enforces OCA (Odoo Community Association) standards for module layout.

Usage:
    python validate_oca_layout.py [--strict] [--fix-permissions]

Exit Codes:
    0 - All validations passed
    1 - Validation errors found
    2 - Script execution error
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple


# ============================================================================
# Configuration
# ============================================================================

# Canonical addon paths relative to repo root
CANONICAL_ADDON_PATHS = [
    "addons/ipai",      # InsightPulse AI custom modules
    "addons/OCA",       # OCA community modules (repos)
    "addons/oca",       # OCA submodules (alternative location)
]

# Valid module name pattern: snake_case, starts with letter
MODULE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

# Invalid patterns to detect
CAMEL_CASE_PATTERN = re.compile(r"[a-z][A-Z]")
KEBAB_CASE_PATTERN = re.compile(r"-")

# Required file for a valid Odoo module
REQUIRED_FILES = ["__manifest__.py"]

# Recommended subdirectories (warnings only)
RECOMMENDED_DIRS = ["models", "views", "security"]

# Optional but common subdirectories
OPTIONAL_DIRS = ["data", "demo", "wizard", "report", "static", "controllers", "tests"]

# Valid license identifiers
VALID_LICENSES = ["AGPL-3", "LGPL-3", "GPL-3", "OEEL-1", "OPL-1"]

# Directories to skip during validation
SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".github",
    "node_modules",
    ".venv",
    "venv",
    ".eggs",
    "*.egg-info",
    "dist",
    "build",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
}


# ============================================================================
# Result Types
# ============================================================================

class ValidationResult(NamedTuple):
    """Result of a single validation check."""
    level: str  # "error", "warning", "info"
    path: str
    message: str


class ValidationReport(NamedTuple):
    """Complete validation report."""
    errors: list
    warnings: list
    info: list
    modules_checked: int
    modules_valid: int


# ============================================================================
# Validators
# ============================================================================

def find_repo_root() -> Path:
    """Find the repository root by looking for .git directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    # Fallback to current directory
    return Path.cwd()


def should_skip_dir(dirname: str) -> bool:
    """Check if directory should be skipped during validation."""
    if dirname in SKIP_DIRS:
        return True
    if dirname.startswith("."):
        return True
    if dirname.endswith(".egg-info"):
        return True
    return False


def validate_module_name(name: str, path: Path) -> list:
    """Validate module name follows snake_case convention."""
    results = []

    # Check for valid pattern
    if not MODULE_NAME_PATTERN.match(name):
        # Detect specific violations
        if CAMEL_CASE_PATTERN.search(name):
            results.append(ValidationResult(
                level="error",
                path=str(path),
                message=f"Module '{name}' uses camelCase - must be snake_case"
            ))
        elif KEBAB_CASE_PATTERN.search(name):
            results.append(ValidationResult(
                level="error",
                path=str(path),
                message=f"Module '{name}' uses kebab-case - must be snake_case"
            ))
        elif name[0].isupper():
            results.append(ValidationResult(
                level="error",
                path=str(path),
                message=f"Module '{name}' starts with uppercase - must start with lowercase"
            ))
        elif name[0].isdigit():
            results.append(ValidationResult(
                level="error",
                path=str(path),
                message=f"Module '{name}' starts with digit - must start with letter"
            ))
        else:
            results.append(ValidationResult(
                level="error",
                path=str(path),
                message=f"Module '{name}' has invalid characters - use only [a-z0-9_]"
            ))

    return results


def validate_manifest_presence(module_path: Path) -> list:
    """Check that __manifest__.py exists."""
    results = []
    manifest_path = module_path / "__manifest__.py"

    if not manifest_path.exists():
        # Check for legacy __openerp__.py
        legacy_path = module_path / "__openerp__.py"
        if legacy_path.exists():
            results.append(ValidationResult(
                level="warning",
                path=str(module_path),
                message="Uses legacy __openerp__.py - should migrate to __manifest__.py"
            ))
        else:
            results.append(ValidationResult(
                level="error",
                path=str(module_path),
                message="Missing __manifest__.py - not a valid Odoo module"
            ))

    return results


def validate_manifest_content(module_path: Path) -> list:
    """Validate manifest file content."""
    results = []
    manifest_path = module_path / "__manifest__.py"

    if not manifest_path.exists():
        return results

    try:
        content = manifest_path.read_text(encoding="utf-8")

        # Parse manifest as Python dict (safe eval alternative)
        # For security, we just check for key presence via regex

        # Check for license
        if "'license'" not in content and '"license"' not in content:
            results.append(ValidationResult(
                level="warning",
                path=str(manifest_path),
                message="Missing 'license' field in manifest"
            ))
        else:
            # Check for valid license values
            license_found = False
            for lic in VALID_LICENSES:
                if f"'{lic}'" in content or f'"{lic}"' in content:
                    license_found = True
                    break
            if not license_found:
                results.append(ValidationResult(
                    level="info",
                    path=str(manifest_path),
                    message="License field present but may not be standard OCA license"
                ))

        # Check for version
        if "'version'" not in content and '"version"' not in content:
            results.append(ValidationResult(
                level="warning",
                path=str(manifest_path),
                message="Missing 'version' field in manifest"
            ))

        # Check for name
        if "'name'" not in content and '"name"' not in content:
            results.append(ValidationResult(
                level="error",
                path=str(manifest_path),
                message="Missing required 'name' field in manifest"
            ))

    except Exception as e:
        results.append(ValidationResult(
            level="error",
            path=str(manifest_path),
            message=f"Failed to read manifest: {e}"
        ))

    return results


def validate_directory_structure(module_path: Path, strict: bool = False) -> list:
    """Validate module has recommended directory structure."""
    results = []

    # Check for recommended directories
    missing_recommended = []
    for dirname in RECOMMENDED_DIRS:
        dir_path = module_path / dirname
        if not dir_path.exists():
            missing_recommended.append(dirname)

    if missing_recommended:
        level = "warning" if not strict else "error"
        results.append(ValidationResult(
            level=level,
            path=str(module_path),
            message=f"Missing recommended directories: {', '.join(missing_recommended)}"
        ))

    # Check for __init__.py in subdirectories that have .py files
    for subdir in module_path.iterdir():
        if subdir.is_dir() and not should_skip_dir(subdir.name):
            py_files = list(subdir.glob("*.py"))
            if py_files and not (subdir / "__init__.py").exists():
                results.append(ValidationResult(
                    level="error",
                    path=str(subdir),
                    message="Directory contains .py files but missing __init__.py"
                ))

    return results


def validate_init_files(module_path: Path) -> list:
    """Validate __init__.py exists at module root."""
    results = []
    init_path = module_path / "__init__.py"

    if not init_path.exists():
        results.append(ValidationResult(
            level="error",
            path=str(module_path),
            message="Missing __init__.py at module root"
        ))

    return results


def is_odoo_module(path: Path) -> bool:
    """Check if a directory is an Odoo module (has __manifest__.py or __openerp__.py)."""
    return (path / "__manifest__.py").exists() or (path / "__openerp__.py").exists()


def validate_module(module_path: Path, strict: bool = False) -> list:
    """Run all validations on a single module."""
    results = []

    module_name = module_path.name

    # Validate module name
    results.extend(validate_module_name(module_name, module_path))

    # Validate manifest presence
    results.extend(validate_manifest_presence(module_path))

    # Validate manifest content
    results.extend(validate_manifest_content(module_path))

    # Validate __init__.py
    results.extend(validate_init_files(module_path))

    # Validate directory structure
    results.extend(validate_directory_structure(module_path, strict))

    return results


def scan_addon_path(addon_path: Path, strict: bool = False) -> tuple:
    """Scan an addon path for modules and validate them."""
    results = []
    modules_checked = 0
    modules_valid = 0

    if not addon_path.exists():
        return results, 0, 0

    # Handle different directory structures
    # addons/ipai/<module>/ - direct modules
    # addons/OCA/<repo>/<module>/ - nested in repos

    for item in addon_path.iterdir():
        if not item.is_dir() or should_skip_dir(item.name):
            continue

        if is_odoo_module(item):
            # Direct module (e.g., addons/ipai/ipai_finance_ppm)
            modules_checked += 1
            module_results = validate_module(item, strict)
            results.extend(module_results)
            if not any(r.level == "error" for r in module_results):
                modules_valid += 1
        else:
            # Check if it's a repo containing modules (e.g., addons/OCA/server-tools)
            for subitem in item.iterdir():
                if subitem.is_dir() and not should_skip_dir(subitem.name):
                    if is_odoo_module(subitem):
                        modules_checked += 1
                        module_results = validate_module(subitem, strict)
                        results.extend(module_results)
                        if not any(r.level == "error" for r in module_results):
                            modules_valid += 1

    return results, modules_checked, modules_valid


def run_validation(repo_root: Path, strict: bool = False) -> ValidationReport:
    """Run full validation across all canonical addon paths."""
    all_results = []
    total_checked = 0
    total_valid = 0

    for addon_rel_path in CANONICAL_ADDON_PATHS:
        addon_path = repo_root / addon_rel_path
        results, checked, valid = scan_addon_path(addon_path, strict)
        all_results.extend(results)
        total_checked += checked
        total_valid += valid

    # Categorize results
    errors = [r for r in all_results if r.level == "error"]
    warnings = [r for r in all_results if r.level == "warning"]
    info = [r for r in all_results if r.level == "info"]

    return ValidationReport(
        errors=errors,
        warnings=warnings,
        info=info,
        modules_checked=total_checked,
        modules_valid=total_valid
    )


# ============================================================================
# Output Formatting
# ============================================================================

def format_result(result: ValidationResult) -> str:
    """Format a single validation result for output."""
    icons = {
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    icon = icons.get(result.level, "•")
    # Make path relative for cleaner output
    try:
        rel_path = Path(result.path).relative_to(Path.cwd())
    except ValueError:
        rel_path = result.path
    return f"  {icon} [{result.level.upper()}] {rel_path}: {result.message}"


def print_report(report: ValidationReport, verbose: bool = False) -> None:
    """Print validation report to stdout."""
    print("\n" + "=" * 70)
    print("Odoo/OCA Layout Validation Report")
    print("=" * 70)

    print(f"\nModules checked: {report.modules_checked}")
    print(f"Modules valid:   {report.modules_valid}")

    if report.errors:
        print(f"\n🔴 ERRORS ({len(report.errors)}):")
        for error in report.errors:
            print(format_result(error))

    if report.warnings:
        print(f"\n🟡 WARNINGS ({len(report.warnings)}):")
        for warning in report.warnings:
            print(format_result(warning))

    if verbose and report.info:
        print(f"\n🔵 INFO ({len(report.info)}):")
        for info in report.info:
            print(format_result(info))

    print("\n" + "-" * 70)
    if report.errors:
        print(f"❌ FAILED: {len(report.errors)} error(s) found")
    else:
        print("✅ PASSED: All layout validations passed")
    print("-" * 70 + "\n")


# ============================================================================
# CLI
# ============================================================================

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Odoo/OCA addon layout and naming conventions"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show info-level messages"
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

    args = parser.parse_args()

    # Find repo root
    if args.root:
        repo_root = args.root
    else:
        repo_root = find_repo_root()

    print(f"Scanning: {repo_root}")

    # Run validation
    try:
        report = run_validation(repo_root, strict=args.strict)
    except Exception as e:
        print(f"❌ Validation failed with error: {e}", file=sys.stderr)
        return 2

    # Print report
    if not args.quiet:
        print_report(report, verbose=args.verbose)
    elif report.errors:
        # In quiet mode, still show errors
        for error in report.errors:
            print(format_result(error))

    # Exit code
    if report.errors:
        return 1
    if args.strict and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
