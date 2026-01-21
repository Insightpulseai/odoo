#!/usr/bin/env python3
"""
Spec-Kit Enforcement Script

Validates that spec bundles meet Continue+ requirements:
- Required files present (constitution, prd, plan, tasks)
- No placeholders (TODO, TBD, LOREM, etc.)
- Minimum substantive content (≥100 words per file)

Usage:
    python scripts/spec-kit-enforce.py spec/<slug>/
    python scripts/spec-kit-enforce.py --check-all spec/
    python scripts/spec-kit-enforce.py --json spec/<slug>/

Exit codes:
    0 - All checks passed
    1 - Validation errors (missing files, placeholders in strict mode)
    2 - Warnings only (placeholders in default mode)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Required files in a spec bundle
REQUIRED_FILES = ["constitution.md", "prd.md", "plan.md", "tasks.md"]

# Placeholder patterns to detect
PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\bXXX\b",
    r"\bLOREM\b",
    r"\bPLACEHOLDER\b",
    r"\[FILL\s*IN\]",
    r"\[INSERT\s*HERE\]",
    r"\[YOUR\s+\w+\s*HERE\]",
]

# Minimum word count per file
MIN_WORD_COUNT = 100


@dataclass
class ValidationResult:
    """Result of validating a single spec bundle."""

    slug: str
    path: str
    valid: bool = True
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    files_checked: dict = field(default_factory=dict)

    def add_error(self, message: str):
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str):
        self.warnings.append(message)

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "path": self.path,
            "valid": self.valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "files_checked": self.files_checked,
        }


def count_words(text: str) -> int:
    """Count substantive words in text (excluding markdown syntax)."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code
    text = re.sub(r"`[^`]+`", "", text)
    # Remove markdown headers
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    # Remove markdown links
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove markdown formatting
    text = re.sub(r"[*_~]", "", text)
    # Split and count
    words = text.split()
    return len(words)


def find_placeholders(text: str, filename: str) -> list:
    """Find placeholder patterns in text."""
    placeholders = []
    lines = text.split("\n")

    for line_num, line in enumerate(lines, 1):
        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                match = re.search(pattern, line, re.IGNORECASE)
                placeholders.append(
                    {
                        "file": filename,
                        "line": line_num,
                        "pattern": match.group(0) if match else pattern,
                        "context": line.strip()[:80],
                    }
                )

    return placeholders


def validate_spec_bundle(
    spec_path: Path,
    strict_placeholders: bool = False,
    strict_content: bool = False,
) -> ValidationResult:
    """Validate a single spec bundle directory."""
    slug = spec_path.name
    result = ValidationResult(slug=slug, path=str(spec_path))

    # Check directory exists
    if not spec_path.is_dir():
        result.add_error(f"Spec directory does not exist: {spec_path}")
        return result

    # Check required files
    for required_file in REQUIRED_FILES:
        file_path = spec_path / required_file
        file_info = {"exists": False, "word_count": 0, "placeholders": []}

        if not file_path.exists():
            result.add_error(f"Missing required file: {required_file}")
        else:
            file_info["exists"] = True
            content = file_path.read_text(encoding="utf-8")

            # Check word count
            word_count = count_words(content)
            file_info["word_count"] = word_count

            if word_count < MIN_WORD_COUNT:
                msg = f"{required_file}: Only {word_count} words (minimum: {MIN_WORD_COUNT})"
                if strict_content:
                    result.add_error(msg)
                else:
                    result.add_warning(msg)

            # Check placeholders
            placeholders = find_placeholders(content, required_file)
            file_info["placeholders"] = placeholders

            if placeholders:
                for ph in placeholders:
                    msg = f"{ph['file']}:{ph['line']}: Placeholder '{ph['pattern']}' found"
                    if strict_placeholders:
                        result.add_error(msg)
                    else:
                        result.add_warning(msg)

        result.files_checked[required_file] = file_info

    return result


def validate_all_specs(
    spec_dir: Path,
    strict_placeholders: bool = False,
    strict_content: bool = False,
) -> list[ValidationResult]:
    """Validate all spec bundles in a directory."""
    results = []

    if not spec_dir.is_dir():
        return results

    for subdir in sorted(spec_dir.iterdir()):
        if subdir.is_dir() and not subdir.name.startswith("."):
            result = validate_spec_bundle(
                subdir,
                strict_placeholders=strict_placeholders,
                strict_content=strict_content,
            )
            results.append(result)

    return results


def print_result(result: ValidationResult, verbose: bool = False):
    """Print validation result in human-readable format."""
    status = "✓ PASS" if result.valid else "✗ FAIL"
    print(f"\n{status} spec/{result.slug}/")

    if result.errors:
        print("  Errors:")
        for error in result.errors:
            print(f"    - {error}")

    if result.warnings:
        print("  Warnings:")
        for warning in result.warnings:
            print(f"    - {warning}")

    if verbose:
        print("  Files:")
        for filename, info in result.files_checked.items():
            status = "✓" if info["exists"] else "✗"
            words = info.get("word_count", 0)
            print(f"    {status} {filename} ({words} words)")


def main():
    parser = argparse.ArgumentParser(
        description="Validate spec-kit bundles for Continue+"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to spec bundle or spec/ directory",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Validate all spec bundles in directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--strict-placeholders",
        action="store_true",
        help="Treat placeholders as errors (default: warnings)",
    )
    parser.add_argument(
        "--strict-content",
        action="store_true",
        help="Treat low word count as errors (default: warnings)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed file information",
    )
    parser.add_argument(
        "--allow-missing-spec",
        action="store_true",
        help="Don't fail if spec directory doesn't exist",
    )

    args = parser.parse_args()

    # Validate
    if args.check_all:
        results = validate_all_specs(
            args.path,
            strict_placeholders=args.strict_placeholders,
            strict_content=args.strict_content,
        )
    else:
        results = [
            validate_spec_bundle(
                args.path,
                strict_placeholders=args.strict_placeholders,
                strict_content=args.strict_content,
            )
        ]

    # Handle missing spec directory
    if not results and args.allow_missing_spec:
        if args.json:
            print(json.dumps({"status": "skipped", "reason": "no specs found"}))
        else:
            print("No spec bundles found (--allow-missing-spec enabled)")
        sys.exit(0)

    # Output results
    if args.json:
        output = {
            "total": len(results),
            "passed": sum(1 for r in results if r.valid),
            "failed": sum(1 for r in results if not r.valid),
            "warnings": sum(len(r.warnings) for r in results),
            "results": [r.to_dict() for r in results],
        }
        print(json.dumps(output, indent=2))
    else:
        for result in results:
            print_result(result, verbose=args.verbose)

        # Summary
        total = len(results)
        passed = sum(1 for r in results if r.valid)
        warnings = sum(len(r.warnings) for r in results)

        print(f"\n{'='*60}")
        print(
            f"Total: {total} | Passed: {passed} | Failed: {total - passed} | Warnings: {warnings}"
        )

    # Exit code
    has_errors = any(not r.valid for r in results)
    has_warnings = any(r.warnings for r in results)

    if has_errors:
        sys.exit(1)
    elif has_warnings and args.strict_placeholders:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
