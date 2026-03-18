#!/usr/bin/env python3
"""
Canonical Structure & Namespace Auditor

Scans the Odoo repository for violations of canonical naming and structure conventions.
Produces both human-readable and JSON reports.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent.resolve()
ADDONS_PATH = REPO_ROOT / "addons" / "ipai"

# Excluded paths
EXCLUDED_PATHS = [
    "*/tests/*",
    "*/migrations/*",
    "*/static/lib/*",
    "../oca/*",
]

# Severity levels
SEVERITY = {
    "critical": ["LINT-001", "LINT-022", "LINT-032", "LINT-062"],
    "high": ["LINT-011", "LINT-012", "LINT-031", "LINT-041"],
    "medium": ["LINT-002", "LINT-021", "LINT-042", "LINT-051"],
    "low": ["LINT-003", "LINT-023", "LINT-052"],
}

# Violation storage
violations = []


class Violation:
    def __init__(self, rule: str, path: str, message: str, line: int = None):
        self.rule = rule
        self.severity = self._get_severity(rule)
        self.path = path
        self.message = message
        self.line = line

    def _get_severity(self, rule: str) -> str:
        for sev, rules in SEVERITY.items():
            if rule in rules:
                return sev
        return "low"

    def to_dict(self) -> dict:
        result = {
            "rule": self.rule,
            "severity": self.severity,
            "path": str(self.path),
            "message": self.message,
        }
        if self.line:
            result["line"] = self.line
        return result

    def __str__(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        return f"{self.rule} ({self.severity}): {loc}\n  {self.message}"


def is_excluded(path: Path) -> bool:
    """Check if path matches exclusion patterns"""
    path_str = str(path)
    for pattern in EXCLUDED_PATHS:
        if Path(path_str).match(pattern):
            return True
    return False


# ============================================================================
# LINT-001: No Dots in Technical Names
# ============================================================================
def check_dotted_module_names() -> int:
    """Find module directories with dots in name"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        module_name = module_dir.name
        if "." in module_name:
            violations.append(
                Violation(
                    "LINT-001",
                    module_dir.relative_to(REPO_ROOT),
                    f"Module name '{module_name}' contains dots. Rename to '{module_name.replace('.', '_')}'",
                )
            )
            count += 1

    return count


# ============================================================================
# LINT-002: IPAI Prefix Required
# ============================================================================
def check_ipai_prefix() -> int:
    """Check all custom modules have ipai_ prefix"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        module_name = module_dir.name
        if not module_name.startswith("ipai_") and module_name != "ipai":
            violations.append(
                Violation(
                    "LINT-002",
                    module_dir.relative_to(REPO_ROOT),
                    f"Module '{module_name}' missing ipai_ prefix",
                )
            )
            count += 1

    return count


# ============================================================================
# LINT-003: Snake Case Only
# ============================================================================
def check_snake_case() -> int:
    """Check module names are lowercase snake_case"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        module_name = module_dir.name
        if not re.match(r"^[a-z][a-z0-9_]*$", module_name):
            violations.append(
                Violation(
                    "LINT-003",
                    module_dir.relative_to(REPO_ROOT),
                    f"Module name '{module_name}' not snake_case (lowercase with underscores only)",
                )
            )
            count += 1

    return count


# ============================================================================
# LINT-011: Use <list> Not <tree>
# ============================================================================
def check_tree_tag_usage() -> int:
    """Find <tree> tags in XML views"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        for xml_file in module_dir.rglob("*.xml"):
            if is_excluded(xml_file):
                continue

            with open(xml_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if re.search(r"<tree\b", line):
                        violations.append(
                            Violation(
                                "LINT-011",
                                xml_file.relative_to(REPO_ROOT),
                                "Use <list> instead of <tree> (Odoo 18 syntax)",
                                line_num,
                            )
                        )
                        count += 1

    return count


# ============================================================================
# LINT-012: Use view_mode="list" Not "tree"
# ============================================================================
def check_view_mode_tree() -> int:
    """Find view_mode with 'tree' instead of 'list'"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        for xml_file in module_dir.rglob("*.xml"):
            if is_excluded(xml_file):
                continue

            with open(xml_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if re.search(r"view_mode.*\btree\b", line):
                        violations.append(
                            Violation(
                                "LINT-012",
                                xml_file.relative_to(REPO_ROOT),
                                "Use view_mode with 'list' instead of 'tree'",
                                line_num,
                            )
                        )
                        count += 1

    return count


# ============================================================================
# LINT-021: Assets in static/src/ Only
# ============================================================================
def check_asset_locations() -> int:
    """Find asset files outside static/src/"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        static_dir = module_dir / "static"
        if not static_dir.exists():
            continue

        for asset_file in static_dir.rglob("*"):
            if not asset_file.is_file():
                continue
            if is_excluded(asset_file):
                continue

            # Check if it's in static/src/
            try:
                rel_path = asset_file.relative_to(static_dir / "src")
            except ValueError:
                # Not in static/src/
                if asset_file.suffix in [
                    ".js",
                    ".xml",
                    ".scss",
                    ".css",
                    ".sass",
                    ".less",
                ]:
                    violations.append(
                        Violation(
                            "LINT-021",
                            asset_file.relative_to(REPO_ROOT),
                            f"Asset file should be in static/src/ not {asset_file.relative_to(module_dir)}",
                        )
                    )
                    count += 1

    return count


# ============================================================================
# LINT-022: Assets Registered in Manifest
# ============================================================================
def check_registered_assets() -> int:
    """Check all asset files are registered in __manifest__.py"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        manifest_file = module_dir / "__manifest__.py"
        if not manifest_file.exists():
            continue

        static_src = module_dir / "static" / "src"
        if not static_src.exists():
            continue

        # Read manifest
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_content = f.read()
        except Exception:
            continue

        # Find asset files
        for asset_file in static_src.rglob("*"):
            if not asset_file.is_file():
                continue
            if is_excluded(asset_file):
                continue
            if asset_file.suffix not in [".js", ".xml", ".scss", ".css"]:
                continue

            # Check if registered
            rel_path = asset_file.relative_to(module_dir)
            asset_path = f"{module_dir.name}/{rel_path}"

            # Simple check: is the path mentioned in manifest?
            if (
                asset_path not in manifest_content
                and str(rel_path) not in manifest_content
            ):
                # Check for glob patterns like "static/src/js/**/*"
                parent_glob = f"{module_dir.name}/static/src/{asset_file.parent.relative_to(static_src).parts[0] if asset_file.parent != static_src else ''}/**/*"
                if parent_glob not in manifest_content:
                    violations.append(
                        Violation(
                            "LINT-022",
                            asset_file.relative_to(REPO_ROOT),
                            f"Asset file not registered in __manifest__.py assets dict",
                        )
                    )
                    count += 1

    return count


# ============================================================================
# LINT-023: No Inline Scripts in Views
# ============================================================================
def check_inline_scripts() -> int:
    """Find inline <script> or <link> tags in XML views"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        for xml_file in module_dir.rglob("*.xml"):
            if is_excluded(xml_file):
                continue

            with open(xml_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if re.search(r"<script[^>]*src=|<link[^>]*href=.*\.(js|css)", line):
                        violations.append(
                            Violation(
                                "LINT-023",
                                xml_file.relative_to(REPO_ROOT),
                                "Inline <script> or <link> tags found. Register in __manifest__.py instead",
                                line_num,
                            )
                        )
                        count += 1

    return count


# ============================================================================
# LINT-031: Explicit Dependencies
# ============================================================================
def check_explicit_dependencies() -> int:
    """Check for potential missing dependencies (basic heuristic)"""
    count = 0
    # This is a simplified check - full dependency analysis requires AST parsing
    # We check for common patterns that suggest missing dependencies

    known_modules = {
        "sale": ["sale.order", "sale.order.line"],
        "account": ["account.move", "account.invoice"],
        "project": ["project.project", "project.task"],
        "hr": ["hr.employee", "hr.department"],
    }

    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        manifest_file = module_dir / "__manifest__.py"
        if not manifest_file.exists():
            continue

        # Read manifest
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_content = f.read()
        except Exception:
            continue

        # Extract depends list
        depends_match = re.search(
            r"'depends'\s*:\s*\[(.*?)\]", manifest_content, re.DOTALL
        )
        if not depends_match:
            continue

        depends_str = depends_match.group(1)
        declared_deps = set(re.findall(r"'(\w+)'", depends_str))

        # Check Python files for model references
        for py_file in module_dir.rglob("*.py"):
            if is_excluded(py_file):
                continue

            with open(py_file, "r", encoding="utf-8") as f:
                py_content = f.read()

            for dep_module, model_patterns in known_modules.items():
                if dep_module in declared_deps:
                    continue

                for pattern in model_patterns:
                    if re.search(rf"['\"]{pattern}['\"]", py_content):
                        violations.append(
                            Violation(
                                "LINT-031",
                                manifest_file.relative_to(REPO_ROOT),
                                f"Module uses '{pattern}' but '{dep_module}' not in depends list",
                            )
                        )
                        count += 1
                        break

    return count


# ============================================================================
# Reporting
# ============================================================================
def generate_report(output_format: str = "human") -> str:
    """Generate audit report"""
    if output_format == "json":
        return generate_json_report()
    else:
        return generate_human_report()


def generate_human_report() -> str:
    """Generate human-readable report"""
    lines = []
    lines.append("=" * 60)
    lines.append("CANONICAL STRUCTURE AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Summary
    severity_counts = defaultdict(int)
    for v in violations:
        severity_counts[v.severity] += 1

    lines.append(f"Total violations: {len(violations)}")
    for sev in ["critical", "high", "medium", "low"]:
        count = severity_counts[sev]
        if count > 0:
            lines.append(f"  {sev.capitalize()}: {count}")
    lines.append("")

    # Group by rule
    by_rule = defaultdict(list)
    for v in violations:
        by_rule[v.rule].append(v)

    for rule in sorted(by_rule.keys()):
        rule_violations = by_rule[rule]
        sev = rule_violations[0].severity
        lines.append(f"{rule} ({sev}): {len(rule_violations)} violation(s)")

        # Show first 5 violations for this rule
        for v in rule_violations[:5]:
            loc = f"{v.path}:{v.line}" if v.line else str(v.path)
            lines.append(f"  - {loc}")
            lines.append(f"    {v.message}")

        if len(rule_violations) > 5:
            lines.append(f"  ... and {len(rule_violations) - 5} more")
        lines.append("")

    return "\n".join(lines)


def generate_json_report() -> str:
    """Generate JSON report"""
    severity_counts = defaultdict(int)
    for v in violations:
        severity_counts[v.severity] += 1

    report = {
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(violations),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"],
        },
        "violations": [v.to_dict() for v in violations],
    }

    return json.dumps(report, indent=2)


# ============================================================================
# Auto-Fix Functions
# ============================================================================
def fix_tree_tags() -> int:
    """Automatically replace <tree> with <list> and </tree> with </list>"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        for xml_file in module_dir.rglob("*.xml"):
            if is_excluded(xml_file):
                continue

            # Read file
            with open(xml_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace
            new_content = content
            new_content = re.sub(r"<tree\b", "<list", new_content)
            new_content = re.sub(r"</tree>", "</list>", new_content)

            # Write back if changed
            if new_content != content:
                with open(xml_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                count += 1
                print(f"Fixed: {xml_file.relative_to(REPO_ROOT)}")

    return count


def fix_view_mode_tree() -> int:
    """Automatically replace view_mode 'tree' with 'list'"""
    count = 0
    for module_dir in ADDONS_PATH.iterdir():
        if not module_dir.is_dir():
            continue
        if is_excluded(module_dir):
            continue

        for xml_file in module_dir.rglob("*.xml"):
            if is_excluded(xml_file):
                continue

            # Read file
            with open(xml_file, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = content

            # Pattern 1: view_mode attribute value (view_mode="tree,form")
            new_content = re.sub(
                r'(view_mode\s*=\s*["\'])([^"\']*\b)tree(\b[^"\']*["\'])',
                r"\1\2list\3",
                new_content,
            )

            # Pattern 2: view_mode field content (<field name="view_mode">tree,form</field>)
            new_content = re.sub(
                r'(<field\s+name=["\']view_mode["\']>)([^<]*\b)tree(\b[^<]*)(</field>)',
                r"\1\2list\3\4",
                new_content,
            )

            # Write back if changed
            if new_content != content:
                with open(xml_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                count += 1
                print(f"Fixed: {xml_file.relative_to(REPO_ROOT)}")

    return count


# ============================================================================
# Main
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Canonical structure auditor")
    parser.add_argument(
        "--check",
        choices=["modules", "views", "assets", "all"],
        default="all",
        help="What to check",
    )
    parser.add_argument(
        "--output",
        choices=["human", "json"],
        default="human",
        help="Output format",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix violations where possible",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code if violations found",
    )

    args = parser.parse_args()

    print(f"Scanning {ADDONS_PATH}...")
    print()

    # Run checks
    if args.check in ["modules", "all"]:
        check_dotted_module_names()
        check_ipai_prefix()
        check_snake_case()

    if args.check in ["views", "all"]:
        check_tree_tag_usage()
        check_view_mode_tree()
        check_inline_scripts()

    if args.check in ["assets", "all"]:
        check_asset_locations()
        check_registered_assets()

    if args.check == "all":
        check_explicit_dependencies()

    # Auto-fix if requested
    if args.fix:
        print("Applying automatic fixes...")
        print()
        fixed = 0
        fixed += fix_tree_tags()
        fixed += fix_view_mode_tree()
        print(f"\nFixed {fixed} files automatically")
        print("Re-run audit to see remaining violations")
        print()
        return 0

    # Generate report
    report = generate_report(args.output)
    print(report)

    # Exit code
    if args.strict and violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
