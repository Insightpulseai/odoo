#!/usr/bin/env python3
"""
Generate Module Health Report

This script analyzes all IPAI modules and generates:
1. docs/module-health/MODULES_PROD_STATUS.md - Human-readable status
2. docs/module-health/modules_status.json - Machine-readable for CI

Usage:
    python scripts/generate_module_health_report.py
    python scripts/generate_module_health_report.py --addons-path addons/ipai
    python scripts/generate_module_health_report.py --json-only

Requirements:
    - Python 3.10+
    - No external dependencies (stdlib only)
"""
import argparse
import ast
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Odoo server major version
ODOO_MAJOR_VERSION = 18

# Known issue signatures
KNOWN_DEPENDENCY_RULES = {
    "ipai_theme_tbwa_backend": {
        "required": ["ipai_platform_theme"],
        "reason": "Theme backend requires ipai_platform_theme tokens module",
        "block": True,
    },
    "ipai_ocr_expense": {
        "optional": ["hr_expense"],
        "reason": "OCR expense works best with hr_expense module",
        "block": False,
    },
}

# Deprecated patterns
DEPRECATED_PATTERNS = [
    r"\.backup$",
    r"_backup$",
    r"_deprecated$",
    r"_retired$",
    r"_old$",
    r"^backup_",
]

# Experimental patterns
EXPERIMENTAL_PATTERNS = [
    r"_experimental$",
    r"_wip$",
    r"_dev$",
    r"_test$",
]

# Valid IPAI prefixes
VALID_IPAI_PREFIXES = [
    "ipai_finance_", "ipai_platform_", "ipai_workspace_",
    "ipai_dev_studio_", "ipai_studio_", "ipai_industry_",
    "ipai_workos_", "ipai_theme_", "ipai_web_theme_",
    "ipai_ce_", "ipai_v18_", "ipai_master_", "ipai_agent_",
    "ipai_ask_", "ipai_ai_", "ipai_bir_", "ipai_ocr_",
    "ipai_ppm_", "ipai_project_", "ipai_srm_", "ipai_superset_",
    "ipai_portal_", "ipai_default_", "ipai_auth_", "ipai_close_",
    "ipai_expense_", "ipai_equipment_", "ipai_assets_",
    "ipai_advisor_", "ipai_clarity_", "ipai_custom_",
    "ipai_chatgpt_", "ipai_marketing_", "ipai_module_",
    "ipai_test_",
]


def parse_manifest(manifest_path: Path) -> dict[str, Any]:
    """Parse a Python manifest file safely."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Parse as Python literal
        return ast.literal_eval(content)
    except Exception as e:
        return {"_error": str(e)}


def scan_for_tree_patterns(module_path: Path) -> bool:
    """Check if module contains tree view patterns."""
    for xml_file in module_path.rglob("*.xml"):
        try:
            content = xml_file.read_text(encoding="utf-8")
            if re.search(r"<tree\b", content) or re.search(r"view_mode.*tree", content):
                return True
        except (IOError, OSError):
            continue
    return False


def compute_module_risk(
    name: str,
    manifest: dict[str, Any],
    module_path: Path,
    all_modules: set[str],
) -> dict[str, Any]:
    """Compute risk assessment for a module."""
    score = 0
    reasons = []
    stage = "stable"
    block = False
    v18_compat_required = False

    # Check for manifest parse error
    if "_error" in manifest:
        return {
            "stage": "deprecated",
            "score": 100,
            "blocked": True,
            "reasons": [f"Manifest parse error: {manifest['_error']}"],
            "deps_missing": [],
            "v18_compat_required": False,
        }

    version = manifest.get("version", "0.0.0")
    depends = manifest.get("depends", [])

    # Check 1: Version major mismatch
    try:
        major = int(version.split(".")[0])
        if major != ODOO_MAJOR_VERSION:
            if major > ODOO_MAJOR_VERSION:
                score += 60
                reasons.append(
                    f"Module version {major}.x requires Odoo {major}, server is {ODOO_MAJOR_VERSION}"
                )
                stage = "experimental"
                block = True
            else:
                score += 40
                reasons.append(
                    f"Module version {major}.x may need migration to Odoo {ODOO_MAJOR_VERSION}"
                )
                stage = "beta"
    except (ValueError, IndexError):
        score += 30
        reasons.append(f"Invalid version format: {version}")
        stage = "beta"

    # Check 2: Deprecated patterns
    for pattern in DEPRECATED_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            score += 80
            reasons.append(f"Module name matches deprecated pattern: {pattern}")
            stage = "deprecated"
            block = True
            break

    # Check 3: Experimental patterns
    if stage != "deprecated":
        for pattern in EXPERIMENTAL_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                score += 40
                reasons.append(f"Module name matches experimental pattern: {pattern}")
                stage = "experimental"
                break

    # Check 4: Missing dependencies
    missing_deps = [d for d in depends if d not in all_modules]
    if missing_deps:
        score += 30
        reasons.append(f"Unmet dependencies: {', '.join(missing_deps)}")
        if stage not in ("deprecated", "experimental"):
            stage = "beta"

    # Check 5: Known dependency rules
    if name in KNOWN_DEPENDENCY_RULES:
        rule = KNOWN_DEPENDENCY_RULES[name]
        required = rule.get("required", [])
        missing_required = [d for d in required if d not in all_modules]
        if missing_required:
            score += 40
            reasons.append(rule["reason"])
            if stage not in ("deprecated",):
                stage = "beta"
            if rule.get("block"):
                block = True

    # Check 6: V18 tree→list patterns
    if name.startswith("ipai_") and scan_for_tree_patterns(module_path):
        score += 25
        reasons.append("Module may contain 'tree' view patterns; ipai_v18_compat recommended")
        v18_compat_required = True
        if stage == "stable":
            stage = "beta"

    # Check 7: IPAI naming conventions
    if name.startswith("ipai_"):
        if not any(name.startswith(prefix) for prefix in VALID_IPAI_PREFIXES):
            score += 5
            reasons.append(f"IPAI module '{name}' doesn't match known domain prefixes")

    # Normalize score
    score = min(100, max(0, score))

    # Adjust stage based on score
    if stage == "stable":
        if score >= 60:
            stage = "experimental"
        elif score >= 30:
            stage = "beta"

    return {
        "stage": stage,
        "score": score,
        "blocked": block,
        "reasons": reasons,
        "deps_missing": missing_deps,
        "v18_compat_required": v18_compat_required,
        "version": version,
        "depends": depends,
    }


def generate_reports(addons_path: str, output_dir: str) -> dict[str, Any]:
    """Generate health reports for all modules in addons path."""
    addons_dir = Path(addons_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Discover all modules
    modules: dict[str, dict[str, Any]] = {}
    all_module_names: set[str] = set()

    for manifest_path in addons_dir.glob("*/__manifest__.py"):
        module_name = manifest_path.parent.name
        all_module_names.add(module_name)

    # Also add known Odoo base modules
    base_modules = {
        "base", "web", "mail", "contacts", "project", "hr", "hr_expense",
        "account", "sale", "purchase", "stock", "crm", "website",
    }
    all_module_names.update(base_modules)

    # Analyze each module
    for manifest_path in sorted(addons_dir.glob("*/__manifest__.py")):
        module_name = manifest_path.parent.name
        manifest = parse_manifest(manifest_path)
        module_path = manifest_path.parent

        risk = compute_module_risk(
            module_name, manifest, module_path, all_module_names
        )

        modules[module_name] = {
            "name": module_name,
            "display_name": manifest.get("name", module_name),
            "summary": manifest.get("summary", ""),
            "category": manifest.get("category", "Uncategorized"),
            "license": manifest.get("license", "Unknown"),
            "installable": manifest.get("installable", True),
            **risk,
        }

    # Generate JSON report
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "odoo_version": ODOO_MAJOR_VERSION,
        "addons_path": str(addons_dir.absolute()),
        "total_modules": len(modules),
        "summary": {
            "stable": len([m for m in modules.values() if m["stage"] == "stable"]),
            "beta": len([m for m in modules.values() if m["stage"] == "beta"]),
            "experimental": len([m for m in modules.values() if m["stage"] == "experimental"]),
            "deprecated": len([m for m in modules.values() if m["stage"] == "deprecated"]),
            "blocked": len([m for m in modules.values() if m["blocked"]]),
        },
        "modules": modules,
    }

    json_path = output_path / "modules_status.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Generated: {json_path}")

    # Generate Markdown report
    md_lines = [
        "# Module Production Readiness Status",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Odoo Version:** {ODOO_MAJOR_VERSION}",
        f"**Addons Path:** `{addons_dir}`",
        "",
        "## Summary",
        "",
        "| Stage | Count | Percentage |",
        "|-------|-------|------------|",
    ]

    total = len(modules)
    for stage_name, count in report_data["summary"].items():
        if stage_name == "blocked":
            continue
        pct = f"{count / total * 100:.1f}%" if total > 0 else "0%"
        emoji = {"stable": "✅", "beta": "⚠️", "experimental": "🧪", "deprecated": "☠️"}.get(
            stage_name, ""
        )
        md_lines.append(f"| {stage_name.title()} {emoji} | {count} | {pct} |")

    md_lines.extend([
        "",
        f"**Blocked Modules:** {report_data['summary']['blocked']}",
        "",
        "---",
        "",
        "## High-Risk Modules",
        "",
        "Modules with risk score ≥ 40:",
        "",
        "| Module | Stage | Score | Blocked | Issues |",
        "|--------|-------|-------|---------|--------|",
    ])

    high_risk = sorted(
        [m for m in modules.values() if m["score"] >= 40],
        key=lambda x: x["score"],
        reverse=True,
    )

    for mod in high_risk[:30]:
        reasons_str = "; ".join(mod["reasons"])[:80]
        blocked_icon = "🚫" if mod["blocked"] else "✓"
        md_lines.append(
            f"| `{mod['name']}` | {mod['stage']} | {mod['score']} | {blocked_icon} | {reasons_str} |"
        )

    if not high_risk:
        md_lines.append("| _(none)_ | - | - | - | - |")

    # Blocked modules section
    blocked = [m for m in modules.values() if m["blocked"]]
    if blocked:
        md_lines.extend([
            "",
            "---",
            "",
            "## Blocked Modules",
            "",
            "These modules are blocked from install/upgrade:",
            "",
        ])
        for mod in sorted(blocked, key=lambda x: x["name"]):
            reasons_str = "; ".join(mod["reasons"])
            md_lines.append(f"- **`{mod['name']}`**: {reasons_str}")

    # V18 compat needed
    v18_needed = [m for m in modules.values() if m.get("v18_compat_required")]
    if v18_needed:
        md_lines.extend([
            "",
            "---",
            "",
            "## V18 Compatibility Required",
            "",
            "These modules may need `ipai_v18_compat` for tree→list view fixes:",
            "",
        ])
        for mod in sorted(v18_needed, key=lambda x: x["name"]):
            md_lines.append(f"- `{mod['name']}`")

    # All modules table
    md_lines.extend([
        "",
        "---",
        "",
        "## All Modules",
        "",
        "| Module | Category | Stage | Score | Version |",
        "|--------|----------|-------|-------|---------|",
    ])

    for mod in sorted(modules.values(), key=lambda x: x["name"]):
        emoji = {"stable": "✅", "beta": "⚠️", "experimental": "🧪", "deprecated": "☠️"}.get(
            mod["stage"], ""
        )
        md_lines.append(
            f"| `{mod['name']}` | {mod['category']} | {mod['stage']} {emoji} | {mod['score']} | {mod['version']} |"
        )

    md_lines.extend(["", "---", "", "_Generated by `scripts/generate_module_health_report.py`_"])

    md_path = output_path / "MODULES_PROD_STATUS.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Generated: {md_path}")

    return report_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate Module Health Report for IPAI modules"
    )
    parser.add_argument(
        "--addons-path",
        default="addons/ipai",
        help="Path to addons directory (default: addons/ipai)",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/module-health",
        help="Output directory for reports (default: docs/module-health)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only generate JSON output",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit with error if any blocked modules exist",
    )

    args = parser.parse_args()

    # Ensure we're in the repo root
    if not Path(args.addons_path).exists():
        # Try from repo root
        repo_root = Path(__file__).parent.parent
        addons_path = repo_root / args.addons_path
        output_dir = repo_root / args.output_dir
    else:
        addons_path = Path(args.addons_path)
        output_dir = Path(args.output_dir)

    if not addons_path.exists():
        print(f"Error: Addons path not found: {addons_path}", file=sys.stderr)
        sys.exit(1)

    report_data = generate_reports(str(addons_path), str(output_dir))

    print("\n=== Summary ===")
    print(f"Total modules: {report_data['total_modules']}")
    for stage, count in report_data["summary"].items():
        print(f"  {stage.title()}: {count}")

    # CI check mode
    if args.check:
        blocked = report_data["summary"]["blocked"]
        if blocked > 0:
            print(f"\n❌ FAILED: {blocked} blocked module(s) detected", file=sys.stderr)
            sys.exit(1)
        else:
            print("\n✅ PASSED: No blocked modules")
            sys.exit(0)


if __name__ == "__main__":
    main()
