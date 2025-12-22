#!/usr/bin/env python3
"""
=============================================================================
Odoo Module Manifest Validation Script
=============================================================================
Validates __manifest__.py files for Odoo modules to ensure they are:
1. Syntactically correct Python
2. Contain required fields (name, version, summary, depends, license)
3. Have valid version numbers
4. Reference valid module dependencies
5. Have proper installable flag

Usage:
    python scripts/validate_manifests.py [path]
    python scripts/validate_manifests.py addons/
    python scripts/validate_manifests.py src/addons/

Exit codes:
    0 - All manifests valid
    1 - Validation errors found
=============================================================================
"""

import ast
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Required manifest fields
REQUIRED_FIELDS = ['name', 'version', 'summary', 'depends']

# Recommended fields
RECOMMENDED_FIELDS = ['license', 'author', 'website', 'category']

# Valid Odoo CE licenses
VALID_LICENSES = [
    'AGPL-3',
    'GPL-3',
    'LGPL-3',
    'OEEL-1',  # Enterprise license (should trigger warning)
    'Other proprietary',
]

# OCA-recommended licenses
OCA_LICENSES = ['AGPL-3', 'GPL-3', 'LGPL-3']

# Version pattern (Odoo 18.0.x.y.z format)
VERSION_PATTERN = re.compile(r'^1[4-9]\.0\.\d+\.\d+\.\d+$')

# Enterprise module indicators
ENTERPRISE_INDICATORS = [
    'web_enterprise',
    'iap',
    'planning',
    'helpdesk',
    'sign',
    'knowledge',
    'documents',
    'spreadsheet',
    'voip',
    'appointment',
    'marketing_automation',
    'social',
    'quality_control',
    'stock_barcode',
]


class ManifestError:
    """Represents a validation error in a manifest."""

    def __init__(self, path: str, level: str, message: str):
        self.path = path
        self.level = level  # 'error', 'warning', 'info'
        self.message = message

    def __str__(self):
        return f"[{self.level.upper()}] {self.path}: {self.message}"


def find_manifests(root_path: str) -> List[Path]:
    """Find all __manifest__.py files in the given path."""
    manifests = []
    root = Path(root_path)

    if root.is_file() and root.name == '__manifest__.py':
        return [root]

    for manifest in root.rglob('__manifest__.py'):
        manifests.append(manifest)

    return manifests


def parse_manifest(manifest_path: Path) -> Tuple[Optional[Dict], Optional[str]]:
    """Parse a manifest file and return its contents."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse as Python literal
        tree = ast.parse(content, mode='eval')
        manifest = ast.literal_eval(content)

        if not isinstance(manifest, dict):
            return None, "Manifest is not a dictionary"

        return manifest, None

    except SyntaxError as e:
        return None, f"Syntax error: {e}"
    except ValueError as e:
        return None, f"Value error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def validate_manifest(manifest_path: Path) -> List[ManifestError]:
    """Validate a single manifest file."""
    errors = []
    path_str = str(manifest_path)

    # Parse manifest
    manifest, parse_error = parse_manifest(manifest_path)
    if parse_error:
        errors.append(ManifestError(path_str, 'error', parse_error))
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(ManifestError(path_str, 'error', f"Missing required field: '{field}'"))
        elif not manifest[field]:
            errors.append(ManifestError(path_str, 'error', f"Empty required field: '{field}'"))

    # Check recommended fields
    for field in RECOMMENDED_FIELDS:
        if field not in manifest:
            errors.append(ManifestError(path_str, 'warning', f"Missing recommended field: '{field}'"))

    # Validate version format
    version = manifest.get('version', '')
    if version and not VERSION_PATTERN.match(version):
        errors.append(ManifestError(
            path_str, 'warning',
            f"Version '{version}' does not follow Odoo format (e.g., 18.0.1.0.0)"
        ))

    # Check license
    license_val = manifest.get('license', '')
    if license_val:
        if license_val not in VALID_LICENSES:
            errors.append(ManifestError(
                path_str, 'warning',
                f"Unknown license: '{license_val}'"
            ))
        elif license_val == 'OEEL-1':
            errors.append(ManifestError(
                path_str, 'error',
                "Enterprise license (OEEL-1) detected - not allowed in CE deployment"
            ))
        elif license_val not in OCA_LICENSES:
            errors.append(ManifestError(
                path_str, 'info',
                f"License '{license_val}' is not OCA-recommended"
            ))

    # Check for Enterprise dependencies
    depends = manifest.get('depends', [])
    if isinstance(depends, list):
        for dep in depends:
            for indicator in ENTERPRISE_INDICATORS:
                if indicator in dep:
                    errors.append(ManifestError(
                        path_str, 'error',
                        f"Enterprise module dependency detected: '{dep}'"
                    ))
                    break

    # Check installable flag
    installable = manifest.get('installable', True)
    if not installable:
        errors.append(ManifestError(
            path_str, 'info',
            "Module is marked as not installable"
        ))

    # Check application flag consistency
    if manifest.get('application') and not manifest.get('category'):
        errors.append(ManifestError(
            path_str, 'warning',
            "Application module should have a category"
        ))

    # Check for assets (Odoo 18 style)
    if 'assets' in manifest:
        assets = manifest['assets']
        if not isinstance(assets, dict):
            errors.append(ManifestError(
                path_str, 'error',
                "'assets' must be a dictionary"
            ))

    return errors


def main():
    """Main entry point."""
    # Determine path to scan
    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
    else:
        # Default to addons directory
        scan_path = 'addons'

    if not os.path.exists(scan_path):
        print(f"Path not found: {scan_path}")
        sys.exit(1)

    print(f"Validating manifests in: {scan_path}")
    print("=" * 60)

    # Find all manifests
    manifests = find_manifests(scan_path)

    if not manifests:
        print("No __manifest__.py files found.")
        sys.exit(0)

    print(f"Found {len(manifests)} manifest file(s)")
    print()

    # Validate each manifest
    all_errors = []
    error_count = 0
    warning_count = 0
    info_count = 0

    for manifest_path in manifests:
        errors = validate_manifest(manifest_path)
        all_errors.extend(errors)

        for error in errors:
            if error.level == 'error':
                error_count += 1
            elif error.level == 'warning':
                warning_count += 1
            else:
                info_count += 1

    # Print results
    if all_errors:
        print("Validation Issues:")
        print("-" * 60)
        for error in all_errors:
            print(error)
        print()

    # Summary
    print("=" * 60)
    print(f"Summary: {len(manifests)} manifests validated")
    print(f"  Errors:   {error_count}")
    print(f"  Warnings: {warning_count}")
    print(f"  Info:     {info_count}")

    if error_count > 0:
        print()
        print("VALIDATION FAILED - Please fix errors before deployment")
        sys.exit(1)
    else:
        print()
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
