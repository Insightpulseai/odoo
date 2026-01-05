#!/usr/bin/env python3
"""
IPAI Module Audit Script

Parses all ipai_* module manifests and generates:
- inventory.json (machine-readable)
- inventory.csv (spreadsheet-friendly)
- inventory.md (human summary)

Usage:
    python scripts/audit_ipai_modules.py
"""

import ast
import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Known enterprise-only modules that should trigger warnings
ENTERPRISE_MODULES = {
    "web_studio",
    "web_enterprise",
    "knowledge",
    "helpdesk",
    "social",
    "social_facebook",
    "social_twitter",
    "social_linkedin",
    "social_instagram",
    "planning",
    "voip",
    "voip_crm",
    "industry_fsm",
    "sign",
    "mrp_plm",
    "timesheet_grid",
    "documents",
    "documents_spreadsheet",
    "appointment",
    "marketing_automation",
    "sale_subscription",
    "quality_control",
    "quality_mrp",
}

# OCA module mappings for redundancy analysis
OCA_CAPABILITY_MAP = {
    "helpdesk": ["helpdesk_mgmt", "helpdesk_ticket"],
    "dms": ["dms", "dms_field"],
    "knowledge": ["knowledge", "document_knowledge"],
    "field_service": ["fieldservice"],
    "automation": ["automation_oca", "base_automation"],
    "queue": ["queue_job"],
    "account_reports": ["account_financial_report"],
    "web_responsive": ["web_responsive"],
    "project_timeline": ["project_timeline"],
    "project_task_dependency": ["project_task_dependency"],
    "sign": ["sign"],
}


def parse_manifest(manifest_path: Path) -> dict:
    """Parse a __manifest__.py file and extract metadata."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Handle the file with coding declaration
        if content.startswith("#"):
            lines = content.split("\n")
            # Skip comment lines at the start
            for i, line in enumerate(lines):
                if line.strip().startswith("{"):
                    content = "\n".join(lines[i:])
                    break

        # Parse the manifest dict
        manifest = ast.literal_eval(content.strip())
        return manifest
    except Exception as e:
        return {"_parse_error": str(e)}


def analyze_module(module_path: Path) -> dict:
    """Analyze a single module and return metadata."""
    manifest_path = module_path / "__manifest__.py"
    module_name = module_path.name

    result = {
        "module_name": module_name,
        "path": str(module_path),
        "manifest_exists": manifest_path.exists(),
    }

    if not manifest_path.exists():
        result["status"] = "NO_MANIFEST"
        return result

    manifest = parse_manifest(manifest_path)

    if "_parse_error" in manifest:
        result["status"] = "PARSE_ERROR"
        result["error"] = manifest["_parse_error"]
        return result

    # Extract manifest fields
    result.update({
        "name": manifest.get("name", ""),
        "version": manifest.get("version", ""),
        "author": manifest.get("author", ""),
        "website": manifest.get("website", ""),
        "license": manifest.get("license", ""),
        "category": manifest.get("category", ""),
        "summary": manifest.get("summary", ""),
        "depends": manifest.get("depends", []),
        "data": manifest.get("data", []),
        "assets": manifest.get("assets", {}),
        "installable": manifest.get("installable", True),
        "application": manifest.get("application", False),
        "auto_install": manifest.get("auto_install", False),
    })

    # Check for enterprise dependencies
    enterprise_deps = [d for d in result["depends"] if d in ENTERPRISE_MODULES]
    result["enterprise_deps"] = enterprise_deps
    result["has_enterprise_deps"] = len(enterprise_deps) > 0

    # Check module structure
    result["has_models"] = (module_path / "models").is_dir()
    result["has_views"] = (module_path / "views").is_dir()
    result["has_controllers"] = (module_path / "controllers").is_dir()
    result["has_security"] = (module_path / "security").is_dir()
    result["has_static"] = (module_path / "static").is_dir()
    result["has_data"] = (module_path / "data").is_dir()
    result["has_wizard"] = (module_path / "wizard").is_dir() or (module_path / "wizards").is_dir()

    # Count Python files (complexity indicator)
    py_files = list(module_path.rglob("*.py"))
    result["python_file_count"] = len([f for f in py_files if f.name != "__init__.py"])

    # Count XML files
    xml_files = list(module_path.rglob("*.xml"))
    result["xml_file_count"] = len(xml_files)

    # Status
    if not result["installable"]:
        result["status"] = "DEPRECATED"
    elif result["has_enterprise_deps"]:
        result["status"] = "ENTERPRISE_DEP"
    else:
        result["status"] = "OK"

    return result


def classify_redundancy(module: dict) -> dict:
    """Classify module for potential redundancy with OCA/CE."""
    module_name = module["module_name"]
    depends = module.get("depends", [])

    classification = {
        "type": "unknown",
        "oca_overlap": [],
        "recommendation": "REVIEW",
        "reason": "",
    }

    # Check for overlap with OCA capabilities
    for capability, oca_modules in OCA_CAPABILITY_MAP.items():
        if capability in module_name.lower():
            classification["oca_overlap"].append({
                "capability": capability,
                "oca_modules": oca_modules,
            })

    # Classify by module structure and naming patterns
    name_lower = module_name.lower()

    # Namespace module (empty/minimal)
    if module_name == "ipai" or module.get("python_file_count", 0) == 0:
        classification["type"] = "namespace"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Namespace/container module"

    # Test fixtures
    elif "test" in name_lower or "fixture" in name_lower:
        classification["type"] = "test"
        classification["recommendation"] = "DEMOTE"
        classification["reason"] = "Test support module - should be application=False"

    # Seed/demo data modules
    elif "seed" in name_lower or "demo" in name_lower:
        classification["type"] = "seed"
        classification["recommendation"] = "DEMOTE"
        classification["reason"] = "Data seeding module - should be application=False"

    # Branding/theming
    elif "brand" in name_lower or "theme" in name_lower or "cleaner" in name_lower:
        classification["type"] = "branding"
        classification["recommendation"] = "DEMOTE"
        classification["reason"] = "Branding/UI customization - should be application=False"

    # Portal/route fixes
    elif "portal" in name_lower or "route" in name_lower or "fix" in name_lower:
        classification["type"] = "patch"
        classification["recommendation"] = "DEMOTE"
        classification["reason"] = "Technical patch - should be application=False"

    # Core business modules
    elif any(x in name_lower for x in ["finance", "ppm", "bir", "close", "tax"]):
        classification["type"] = "core_business"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Core business logic for finance/tax compliance"

    # AI/Integration modules
    elif any(x in name_lower for x in ["ai", "ask", "ocr", "superset", "agent"]):
        classification["type"] = "integration"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "AI/Integration functionality"

    # Industry verticals
    elif "industry" in name_lower or "workspace" in name_lower:
        classification["type"] = "vertical"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Industry vertical/workspace module"

    # Equipment/Asset management
    elif "equipment" in name_lower or "asset" in name_lower:
        classification["type"] = "feature"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Asset management feature"

    # SRM/Supplier
    elif "srm" in name_lower or "supplier" in name_lower:
        classification["type"] = "feature"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Supplier relationship management"

    # Expense
    elif "expense" in name_lower:
        classification["type"] = "feature"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Expense management extension"

    # Project/Program management
    elif "project" in name_lower or "program" in name_lower:
        classification["type"] = "feature"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Project/program management extension"

    # Studio-like modules (potential overlap with OCA automation)
    elif "studio" in name_lower:
        classification["type"] = "feature"
        classification["oca_overlap"].append({
            "capability": "automation",
            "oca_modules": ["automation_oca", "base_automation"],
        })
        classification["recommendation"] = "REVIEW"
        classification["reason"] = "Studio-like functionality - check OCA automation overlap"

    # Advisor/Dashboard
    elif "advisor" in name_lower or "dashboard" in name_lower:
        classification["type"] = "feature"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Analytics/advisory feature"

    # Master control
    elif "master" in name_lower or "control" in name_lower:
        classification["type"] = "integration"
        classification["recommendation"] = "KEEP"
        classification["reason"] = "Control/orchestration integration"

    # Default home
    elif "home" in name_lower or "default" in name_lower:
        classification["type"] = "branding"
        classification["recommendation"] = "DEMOTE"
        classification["reason"] = "UI customization - should be application=False"

    # Check for potential duplicates (similar names)
    else:
        classification["type"] = "unknown"
        classification["recommendation"] = "REVIEW"
        classification["reason"] = "Needs manual review"

    # Override if enterprise deps found
    if module.get("has_enterprise_deps"):
        classification["recommendation"] = "REFACTOR"
        classification["reason"] = f"Has enterprise deps: {module.get('enterprise_deps', [])}"

    return classification


def find_potential_duplicates(modules: list) -> list:
    """Find modules that might be duplicates based on naming patterns."""
    duplicates = []

    # Group by base name patterns
    name_groups = {}
    for m in modules:
        name = m["module_name"]
        # Extract base name (remove common suffixes)
        base = name
        for suffix in ["_closing", "_close", "_ppm", "_tdi", "_seed", "_automation", "_dashboard"]:
            if base.endswith(suffix):
                base = base[:-len(suffix)]
                break

        if base not in name_groups:
            name_groups[base] = []
        name_groups[base].append(name)

    # Flag groups with multiple modules
    for base, names in name_groups.items():
        if len(names) > 1:
            duplicates.append({
                "base_name": base,
                "modules": names,
                "count": len(names),
            })

    return duplicates


def generate_reports(modules: list, output_dir: Path):
    """Generate inventory reports in multiple formats."""

    # Add classification to each module
    for m in modules:
        m["classification"] = classify_redundancy(m)

    # Find duplicates
    duplicates = find_potential_duplicates(modules)

    # Generate JSON
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_modules": len(modules),
        "modules": modules,
        "potential_duplicates": duplicates,
        "summary": {
            "ok": len([m for m in modules if m.get("status") == "OK"]),
            "enterprise_deps": len([m for m in modules if m.get("status") == "ENTERPRISE_DEP"]),
            "deprecated": len([m for m in modules if m.get("status") == "DEPRECATED"]),
            "parse_error": len([m for m in modules if m.get("status") == "PARSE_ERROR"]),
            "applications": len([m for m in modules if m.get("application")]),
            "installable": len([m for m in modules if m.get("installable", True)]),
        },
        "recommendations": {
            "keep": len([m for m in modules if m["classification"]["recommendation"] == "KEEP"]),
            "demote": len([m for m in modules if m["classification"]["recommendation"] == "DEMOTE"]),
            "review": len([m for m in modules if m["classification"]["recommendation"] == "REVIEW"]),
            "refactor": len([m for m in modules if m["classification"]["recommendation"] == "REFACTOR"]),
        },
    }

    json_path = output_dir / "inventory.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Generated: {json_path}")

    # Generate CSV
    csv_path = output_dir / "inventory.csv"
    fieldnames = [
        "module_name", "name", "version", "author", "license", "category",
        "installable", "application", "auto_install",
        "depends_count", "has_enterprise_deps", "enterprise_deps",
        "python_file_count", "xml_file_count",
        "has_models", "has_views", "has_controllers",
        "status", "classification_type", "recommendation", "reason",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for m in modules:
            row = {**m}
            row["depends_count"] = len(m.get("depends", []))
            row["enterprise_deps"] = ",".join(m.get("enterprise_deps", []))
            row["classification_type"] = m["classification"]["type"]
            row["recommendation"] = m["classification"]["recommendation"]
            row["reason"] = m["classification"]["reason"]
            writer.writerow(row)
    print(f"Generated: {csv_path}")

    # Generate Markdown
    md_path = output_dir / "inventory.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# IPAI Module Inventory\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary\n\n")
        f.write(f"| Metric | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total Modules | {report['total_modules']} |\n")
        f.write(f"| OK Status | {report['summary']['ok']} |\n")
        f.write(f"| Enterprise Deps | {report['summary']['enterprise_deps']} |\n")
        f.write(f"| Applications | {report['summary']['applications']} |\n")
        f.write(f"| Installable | {report['summary']['installable']} |\n")
        f.write("\n")

        f.write("## Recommendations Summary\n\n")
        f.write(f"| Recommendation | Count |\n")
        f.write(f"|----------------|-------|\n")
        f.write(f"| KEEP | {report['recommendations']['keep']} |\n")
        f.write(f"| DEMOTE | {report['recommendations']['demote']} |\n")
        f.write(f"| REVIEW | {report['recommendations']['review']} |\n")
        f.write(f"| REFACTOR | {report['recommendations']['refactor']} |\n")
        f.write("\n")

        f.write("## Module Details\n\n")
        f.write("| Module | Version | App | Rec | Type | Reason |\n")
        f.write("|--------|---------|-----|-----|------|--------|\n")
        for m in sorted(modules, key=lambda x: x["module_name"]):
            app_flag = "Yes" if m.get("application") else "No"
            rec = m["classification"]["recommendation"]
            mtype = m["classification"]["type"]
            reason = m["classification"]["reason"][:50] + "..." if len(m["classification"]["reason"]) > 50 else m["classification"]["reason"]
            f.write(f"| {m['module_name']} | {m.get('version', '')} | {app_flag} | {rec} | {mtype} | {reason} |\n")
        f.write("\n")

        if duplicates:
            f.write("## Potential Duplicates\n\n")
            f.write("These module groups may have overlapping functionality:\n\n")
            for dup in duplicates:
                f.write(f"- **{dup['base_name']}**: {', '.join(dup['modules'])}\n")
            f.write("\n")

        # Enterprise dependency warnings
        enterprise_mods = [m for m in modules if m.get("has_enterprise_deps")]
        if enterprise_mods:
            f.write("## Enterprise Dependency Warnings\n\n")
            f.write("These modules depend on Enterprise-only modules and need refactoring:\n\n")
            for m in enterprise_mods:
                f.write(f"- **{m['module_name']}**: depends on {', '.join(m['enterprise_deps'])}\n")
            f.write("\n")

    print(f"Generated: {md_path}")

    return report


def main():
    """Main entry point."""
    # Find repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    ipai_dir = repo_root / "addons" / "ipai"
    output_dir = repo_root / "docs" / "audits" / "ipai_modules"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning IPAI modules in: {ipai_dir}")

    # Find all module directories
    modules = []
    for item in ipai_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            manifest_path = item / "__manifest__.py"
            if manifest_path.exists():
                module_data = analyze_module(item)
                modules.append(module_data)

    # Also check root ipai namespace
    root_manifest = ipai_dir / "__manifest__.py"
    if root_manifest.exists():
        module_data = analyze_module(ipai_dir)
        module_data["module_name"] = "ipai"
        modules.append(module_data)

    print(f"Found {len(modules)} modules")

    # Generate reports
    report = generate_reports(modules, output_dir)

    print("\n=== AUDIT COMPLETE ===")
    print(f"Total: {report['total_modules']} modules")
    print(f"KEEP: {report['recommendations']['keep']}")
    print(f"DEMOTE: {report['recommendations']['demote']}")
    print(f"REVIEW: {report['recommendations']['review']}")
    print(f"REFACTOR: {report['recommendations']['refactor']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
