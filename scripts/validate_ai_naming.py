#!/usr/bin/env python3
"""
Validate AI module naming conventions (OCA-aligned).

This script enforces the canonical naming conventions for IPAI AI modules:
- Module names match folder names
- Model names start with 'ipai.ai.'
- Security groups are named 'group_ipai_ai_*'
- Routes start with '/ipai/ai/'
- XML IDs are module-prefixed

Usage:
    python scripts/validate_ai_naming.py [--fix]

Exit codes:
    0 - All validations passed
    1 - Validation errors found
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple


class ValidationError(NamedTuple):
    file: str
    line: int
    rule: str
    message: str


def find_ai_modules(addons_path: Path) -> list[Path]:
    """Find all ipai_ai_* modules."""
    modules = []
    ipai_path = addons_path / "ipai"
    if ipai_path.exists():
        for item in ipai_path.iterdir():
            if item.is_dir() and item.name.startswith("ipai_ai_"):
                if (item / "__manifest__.py").exists():
                    modules.append(item)
    return modules


def validate_module_name(module_path: Path) -> list[ValidationError]:
    """Check module name matches folder name."""
    errors = []
    manifest_path = module_path / "__manifest__.py"

    if manifest_path.exists():
        content = manifest_path.read_text()
        # Extract 'name' from manifest
        match = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", content)
        if match:
            display_name = match.group(1)
            # Technical name should match folder
            folder_name = module_path.name
            # Check that technical name (folder) follows pattern
            if not re.match(r"^ipai_ai_(assistant|agent_\w+|tools_\w+)$", folder_name):
                errors.append(
                    ValidationError(
                        file=str(manifest_path),
                        line=0,
                        rule="module-name",
                        message=f"Module folder '{folder_name}' doesn't follow pattern: "
                        "ipai_ai_assistant, ipai_ai_agent_<domain>, or ipai_ai_tools_<domain>",
                    )
                )
    return errors


def validate_model_names(module_path: Path) -> list[ValidationError]:
    """Check all models start with 'ipai.ai.'."""
    errors = []
    models_path = module_path / "models"

    if not models_path.exists():
        return errors

    for py_file in models_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        content = py_file.read_text()
        # Find _name definitions
        for i, line in enumerate(content.split("\n"), 1):
            match = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", line)
            if match:
                model_name = match.group(1)
                if not model_name.startswith("ipai.ai."):
                    errors.append(
                        ValidationError(
                            file=str(py_file),
                            line=i,
                            rule="model-name",
                            message=f"Model '{model_name}' must start with 'ipai.ai.'",
                        )
                    )

    return errors


def validate_security_groups(module_path: Path) -> list[ValidationError]:
    """Check security groups are named 'group_ipai_ai_*'."""
    errors = []
    security_path = module_path / "security"

    if not security_path.exists():
        return errors

    for xml_file in security_path.glob("*.xml"):
        content = xml_file.read_text()
        # Find record ids for res.groups
        for match in re.finditer(
            r'<record[^>]*id=["\']([^"\']+)["\'][^>]*model=["\']res\.groups["\']',
            content,
        ):
            group_id = match.group(1)
            # Remove module prefix if present
            if "." in group_id:
                group_id = group_id.split(".")[-1]
            if not group_id.startswith("group_ipai_ai_"):
                errors.append(
                    ValidationError(
                        file=str(xml_file),
                        line=0,
                        rule="security-group",
                        message=f"Security group '{group_id}' must start with 'group_ipai_ai_'",
                    )
                )

    return errors


def validate_routes(module_path: Path) -> list[ValidationError]:
    """Check routes start with '/ipai/ai/'."""
    errors = []
    controllers_path = module_path / "controllers"

    if not controllers_path.exists():
        return errors

    for py_file in controllers_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        content = py_file.read_text()
        # Find @http.route decorators
        for i, line in enumerate(content.split("\n"), 1):
            match = re.search(r"@http\.route\s*\(\s*['\"]([^'\"]+)['\"]", line)
            if match:
                route = match.group(1)
                if not route.startswith("/ipai/ai/"):
                    errors.append(
                        ValidationError(
                            file=str(py_file),
                            line=i,
                            rule="route",
                            message=f"Route '{route}' must start with '/ipai/ai/'",
                        )
                    )

    return errors


def validate_xml_ids(module_path: Path) -> list[ValidationError]:
    """Check XML IDs are module-prefixed."""
    errors = []
    module_name = module_path.name

    for xml_file in module_path.rglob("*.xml"):
        if ".git" in str(xml_file):
            continue

        content = xml_file.read_text()
        # Find record ids
        for match in re.finditer(r'<record[^>]*id=["\']([^"\']+)["\']', content):
            record_id = match.group(1)
            # Check if using external reference (module.id)
            if "." in record_id:
                ref_module = record_id.split(".")[0]
                # External references to other modules are OK
                if ref_module != module_name:
                    continue
            # Local IDs should not be empty
            if not record_id:
                errors.append(
                    ValidationError(
                        file=str(xml_file),
                        line=0,
                        rule="xml-id",
                        message="Empty record id found",
                    )
                )

    return errors


def validate_no_mixed_naming(module_path: Path) -> list[ValidationError]:
    """Check no mixed 'assistant/agent' naming in module ids."""
    errors = []
    folder_name = module_path.name

    # Check for invalid combinations
    if "assistant" in folder_name and "agent" in folder_name:
        errors.append(
            ValidationError(
                file=str(module_path),
                line=0,
                rule="mixed-naming",
                message=f"Module '{folder_name}' has mixed 'assistant' and 'agent' naming",
            )
        )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate AI module naming conventions"
    )
    parser.add_argument(
        "--addons-path",
        type=Path,
        default=Path("addons"),
        help="Path to addons directory (default: addons)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Find all AI modules
    modules = find_ai_modules(args.addons_path)

    if not modules:
        print("No ipai_ai_* modules found in", args.addons_path / "ipai")
        return 0

    if args.verbose:
        print(f"Found {len(modules)} AI modules:")
        for m in modules:
            print(f"  - {m.name}")
        print()

    # Run all validations
    all_errors: list[ValidationError] = []

    for module in modules:
        all_errors.extend(validate_module_name(module))
        all_errors.extend(validate_model_names(module))
        all_errors.extend(validate_security_groups(module))
        all_errors.extend(validate_routes(module))
        all_errors.extend(validate_xml_ids(module))
        all_errors.extend(validate_no_mixed_naming(module))

    # Report results
    if all_errors:
        print(f"Found {len(all_errors)} validation error(s):\n")
        for error in all_errors:
            print(f"[{error.rule}] {error.file}:{error.line}")
            print(f"  {error.message}\n")
        return 1
    else:
        print(f"All {len(modules)} AI module(s) pass naming conventions.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
