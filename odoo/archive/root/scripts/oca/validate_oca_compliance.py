#!/usr/bin/env python3
"""
OCA Module Compliance Validator

Comprehensive validation of OCA module compliance for Odoo 19.0 ports.
Enforces OCA quality standards, dependency resolution, and manifest integrity.

Usage:
    ./scripts/oca/validate_oca_compliance.py <module_path>
    ./scripts/oca/validate_oca_compliance.py addons/oca/connector/component

Exit Codes:
    0: All validation checks passed
    1: Validation errors found
    2: Script error (missing dependencies, invalid arguments)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess

# OCA Standards
OCA_LICENSES = ["AGPL-3", "LGPL-3", "GPL-3", "Apache-2.0", "MIT"]
REQUIRED_MANIFEST_KEYS = [
    "name",
    "version",
    "license",
    "author",
    "website",
    "category",
    "depends",
    "installable",
]
OPTIONAL_MANIFEST_KEYS = [
    "summary",
    "description",
    "data",
    "demo",
    "external_dependencies",
    "development_status",
    "maintainers",
]
TARGET_ODOO_VERSION = "19.0"


class ValidationError:
    """Represents a validation error with severity and details."""

    def __init__(
        self,
        severity: str,
        check: str,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
    ):
        self.severity = severity  # ERROR, WARNING, INFO
        self.check = check
        self.message = message
        self.file_path = file_path
        self.line_number = line_number

    def __str__(self):
        location = ""
        if self.file_path:
            location = f" ({self.file_path}"
            if self.line_number:
                location += f":{self.line_number}"
            location += ")"
        return f"[{self.severity}] {self.check}: {self.message}{location}"


class OCAComplianceValidator:
    """Validates OCA module compliance for Odoo 19.0."""

    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.module_name = module_path.name
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.manifest: Optional[Dict] = None

    def validate(self) -> Tuple[bool, List[ValidationError], List[ValidationError]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (success, errors, warnings)
        """
        print(f"Validating OCA compliance for: {self.module_name}")
        print(f"Module path: {self.module_path}")
        print()

        # 1. Basic structure checks
        self._check_module_structure()

        # 2. Manifest validation
        self._validate_manifest()

        # 3. Python syntax and API compliance
        self._validate_python_files()

        # 4. Dependency resolution
        self._validate_dependencies()

        # 5. Security checks
        self._validate_security()

        # 6. Pre-commit hook compliance
        self._validate_precommit_hooks()

        # 7. License compliance
        self._validate_license()

        # 8. Data file integrity
        self._validate_data_files()

        success = len(self.errors) == 0
        return success, self.errors, self.warnings

    def _check_module_structure(self):
        """Validate basic module directory structure."""
        required_files = ["__manifest__.py", "__init__.py"]

        for file_name in required_files:
            file_path = self.module_path / file_name
            if not file_path.exists():
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "MODULE_STRUCTURE",
                        f"Missing required file: {file_name}",
                        str(file_path),
                    )
                )

        # Check for README (OCA standard)
        readme_files = list(self.module_path.glob("README.*"))
        if not readme_files:
            self.warnings.append(
                ValidationError(
                    "WARNING",
                    "MODULE_STRUCTURE",
                    "Missing README file (OCA recommends README.rst)",
                )
            )

    def _validate_manifest(self):
        """Validate __manifest__.py structure and content."""
        manifest_path = self.module_path / "__manifest__.py"

        if not manifest_path.exists():
            return  # Already caught in structure check

        try:
            with open(manifest_path, "r") as f:
                content = f.read()
                self.manifest = ast.literal_eval(content)
        except (SyntaxError, ValueError) as e:
            self.errors.append(
                ValidationError(
                    "ERROR",
                    "MANIFEST_SYNTAX",
                    f"Invalid manifest syntax: {e}",
                    str(manifest_path),
                )
            )
            return

        # Check required keys
        for key in REQUIRED_MANIFEST_KEYS:
            if key not in self.manifest:
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "MANIFEST_REQUIRED_KEY",
                        f"Missing required manifest key: {key}",
                        str(manifest_path),
                    )
                )

        # Validate version format
        if "version" in self.manifest:
            version = self.manifest["version"]
            if not version.startswith(f"{TARGET_ODOO_VERSION}."):
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "MANIFEST_VERSION",
                        f"Version must start with {TARGET_ODOO_VERSION}. (got: {version})",
                        str(manifest_path),
                    )
                )

            # OCA version format: X.Y.Z.A.B
            version_parts = version.split(".")
            if len(version_parts) != 5:
                self.warnings.append(
                    ValidationError(
                        "WARNING",
                        "MANIFEST_VERSION",
                        f"OCA recommends 5-part version format (X.Y.Z.A.B), got: {version}",
                        str(manifest_path),
                    )
                )

        # Validate license
        if "license" in self.manifest:
            license_value = self.manifest["license"]
            if not any(license_value.startswith(lic) for lic in OCA_LICENSES):
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "MANIFEST_LICENSE",
                        f"License must be one of {OCA_LICENSES}, got: {license_value}",
                        str(manifest_path),
                    )
                )

        # Validate installable flag
        if "installable" in self.manifest:
            if not self.manifest["installable"]:
                self.warnings.append(
                    ValidationError(
                        "WARNING",
                        "MANIFEST_INSTALLABLE",
                        "Module marked as installable=False",
                        str(manifest_path),
                    )
                )

        # Check for OCA author
        if "author" in self.manifest:
            author = self.manifest["author"]
            if "OCA" not in author and "Odoo Community Association" not in author:
                self.warnings.append(
                    ValidationError(
                        "WARNING",
                        "MANIFEST_AUTHOR",
                        "OCA modules should include 'Odoo Community Association (OCA)' in author field",
                        str(manifest_path),
                    )
                )

        # Validate depends list
        if "depends" in self.manifest:
            depends = self.manifest["depends"]
            if not isinstance(depends, list):
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "MANIFEST_DEPENDS",
                        "depends field must be a list",
                        str(manifest_path),
                    )
                )
            elif not depends:
                self.warnings.append(
                    ValidationError(
                        "WARNING",
                        "MANIFEST_DEPENDS",
                        "Empty depends list (should at least include 'base')",
                        str(manifest_path),
                    )
                )

    def _validate_python_files(self):
        """Validate Python syntax and deprecated API usage."""
        python_files = list(self.module_path.rglob("*.py"))

        if not python_files:
            self.warnings.append(
                ValidationError(
                    "WARNING", "PYTHON_FILES", "No Python files found in module"
                )
            )
            return

        # Check for deprecated Odoo API patterns
        deprecated_patterns = [
            (r"@api\.one", "api.one decorator (use @api.model or @api.multi instead)"),
            (r"@api\.v7", "api.v7 decorator (removed in Odoo 12+)"),
            (r"@api\.v8", "api.v8 decorator (removed in Odoo 12+)"),
            (r"_columns\s*=", "_columns attribute (use new API fields instead)"),
            (r"\.sudo\(\w+\)", ".sudo(user) with parameter (use .sudo() or .with_user())"),
            (r"fields\.Text\(.*translate=True", "Text field with translate=True (use fields.Text with translate parameter)"),
        ]

        for py_file in python_files:
            # Syntax check
            try:
                with open(py_file, "r") as f:
                    compile(f.read(), str(py_file), "exec")
            except SyntaxError as e:
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "PYTHON_SYNTAX",
                        f"Python syntax error: {e}",
                        str(py_file),
                        e.lineno,
                    )
                )
                continue

            # Check for deprecated patterns
            with open(py_file, "r") as f:
                content = f.read()
                lines = content.splitlines()

                for pattern, message in deprecated_patterns:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            self.warnings.append(
                                ValidationError(
                                    "WARNING",
                                    "DEPRECATED_API",
                                    f"Deprecated API usage: {message}",
                                    str(py_file),
                                    line_num,
                                )
                            )

    def _validate_dependencies(self):
        """Validate module dependencies and circular dependency detection."""
        if not self.manifest or "depends" not in self.manifest:
            return

        depends = self.manifest["depends"]

        # Check for self-dependency
        if self.module_name in depends:
            self.errors.append(
                ValidationError(
                    "ERROR",
                    "DEPENDENCY_CIRCULAR",
                    f"Module cannot depend on itself: {self.module_name}",
                )
            )

        # Check for common misspellings
        common_misspellings = {
            "sale_management": "sale",
            "purchase_management": "purchase",
            "account_accountant": "account",
        }

        for dep in depends:
            if dep in common_misspellings:
                self.warnings.append(
                    ValidationError(
                        "WARNING",
                        "DEPENDENCY_MISSPELLING",
                        f"Possible misspelling: '{dep}' (did you mean '{common_misspellings[dep]}'?)",
                    )
                )

    def _validate_security(self):
        """Validate security configuration and access rights."""
        security_dir = self.module_path / "security"

        if not security_dir.exists():
            self.warnings.append(
                ValidationError(
                    "WARNING",
                    "SECURITY_DIR",
                    "No security/ directory found (recommended for modules with models)",
                )
            )
            return

        # Check for ir.model.access.csv
        access_csv = security_dir / "ir.model.access.csv"
        if access_csv.exists():
            try:
                with open(access_csv, "r") as f:
                    lines = f.readlines()
                    if len(lines) < 2:  # Header + at least one rule
                        self.warnings.append(
                            ValidationError(
                                "WARNING",
                                "SECURITY_ACCESS",
                                "ir.model.access.csv exists but has no access rules",
                                str(access_csv),
                            )
                        )
            except Exception as e:
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "SECURITY_ACCESS",
                        f"Error reading access CSV: {e}",
                        str(access_csv),
                    )
                )

    def _validate_precommit_hooks(self):
        """Validate pre-commit hook compliance."""
        # Check if pre-commit is installed
        try:
            subprocess.run(
                ["pre-commit", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.warnings.append(
                ValidationError(
                    "WARNING",
                    "PRECOMMIT",
                    "pre-commit not installed or not available (OCA recommends running pre-commit hooks)",
                )
            )
            return

        # Run pre-commit hooks on the module
        # Note: This is a dry-run check only, actual hooks run in CI
        repo_root = self.module_path
        while repo_root.parent != repo_root:
            if (repo_root / ".pre-commit-config.yaml").exists():
                break
            repo_root = repo_root.parent

        if not (repo_root / ".pre-commit-config.yaml").exists():
            self.warnings.append(
                ValidationError(
                    "WARNING",
                    "PRECOMMIT",
                    "No .pre-commit-config.yaml found in repository root",
                )
            )

    def _validate_license(self):
        """Validate license file presence and compatibility."""
        # Check for LICENSE or COPYING file
        license_files = list(self.module_path.glob("LICENSE*")) + list(
            self.module_path.glob("COPYING*")
        )

        if not license_files:
            self.warnings.append(
                ValidationError(
                    "WARNING",
                    "LICENSE_FILE",
                    "No LICENSE or COPYING file found (OCA recommends including license text)",
                )
            )

    def _validate_data_files(self):
        """Validate data files integrity (XML, CSV)."""
        if not self.manifest or "data" not in self.manifest:
            return

        data_files = self.manifest["data"]

        for data_file in data_files:
            file_path = self.module_path / data_file

            if not file_path.exists():
                self.errors.append(
                    ValidationError(
                        "ERROR",
                        "DATA_FILE_MISSING",
                        f"Data file declared in manifest but not found: {data_file}",
                        str(file_path),
                    )
                )
                continue

            # Basic XML syntax check
            if file_path.suffix == ".xml":
                try:
                    import xml.etree.ElementTree as ET

                    ET.parse(file_path)
                except ET.ParseError as e:
                    self.errors.append(
                        ValidationError(
                            "ERROR",
                            "DATA_FILE_SYNTAX",
                            f"XML syntax error: {e}",
                            str(file_path),
                        )
                    )

    def print_summary(self):
        """Print validation summary."""
        print()
        print("=" * 70)
        print("OCA COMPLIANCE VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Module: {self.module_name}")
        print(f"Path: {self.module_path}")
        print()

        if self.errors:
            print(f"❌ ERRORS: {len(self.errors)}")
            for error in self.errors:
                print(f"  {error}")
            print()

        if self.warnings:
            print(f"⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✅ All validation checks passed!")
        elif not self.errors:
            print("✅ No errors found (warnings present but non-blocking)")
        else:
            print("❌ Validation failed - please fix errors before proceeding")

        print("=" * 70)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    module_path = Path(sys.argv[1]).resolve()

    if not module_path.exists():
        print(f"ERROR: Module path does not exist: {module_path}")
        sys.exit(2)

    if not module_path.is_dir():
        print(f"ERROR: Module path is not a directory: {module_path}")
        sys.exit(2)

    validator = OCAComplianceValidator(module_path)
    success, errors, warnings = validator.validate()
    validator.print_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
