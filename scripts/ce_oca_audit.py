#!/usr/bin/env python3
"""
Odoo 18 CE + OCA Module Auditor
Determines module availability, classification, and OCA equivalents.
"""

import ast
import csv
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Configuration
REPO_ROOT = Path("/home/user/odoo-ce")
ADDONS_ROOT = REPO_ROOT / "addons"
IPAI_NESTED = ADDONS_ROOT / "ipai"
EXTERNAL_SRC = REPO_ROOT / "external-src"
OCA_MANIFEST = ADDONS_ROOT / "oca" / "manifest.yaml"

# Odoo version
ODOO_VERSION = "18.0"

# The apps list to audit
APPS_LIST = [
    "sale_management",
    "pos_restaurant",
    "account",
    "ipai_workos_core",
    "crm",
    "mrp_workorder",
    "website",
    "stock",
    "accountant",
    "knowledge",
    "purchase",
    "point_of_sale",
    "project",
    "website_sale",
    "mrp",
    "mass_mailing",
    "timesheet_grid",
    "hr_expense",
    "web_studio",
    "hr_holidays",
    "hr_recruitment",
    "industry_fsm",
    "hr",
    "data_recycle",
    "ipai_bir_tax_compliance",
    "ipai_close_orchestration",
    "ipai_finance_ppm",
    "ipai_finance_ppm_golive",
    "ipai_month_end",
    "ipai_ppm_a1",
    "ipai_superset_connector",
    "ipai_tbwa_finance",
    "maintenance",
    "marketing_card",
    "sign",
    "helpdesk",
    "sale_subscription",
    "quality_control",
    "website_slides",
    "planning",
    "website_event",
    "mail",
    "contacts",
    "calendar",
    "social",
    "hr_appraisal",
    "fleet",
    "marketing_automation",
    "im_livechat",
    "appointment",
    "survey",
    "web_mobile",
    "repair",
    "hr_attendance",
    "mass_mailing_sms",
    "stock_barcode",
    "project_todo",
    "hr_skills",
    "voip",
    "lunch",
    "website_hr_recruitment",
    "sale_amazon",
    "hr_contract",
    "ipai_workos_affine",
]

# Known Odoo CE core modules (Odoo 18.0)
# These are available in the standard Odoo CE distribution
CE_CORE_MODULES = {
    # Base
    "base",
    "web",
    "base_setup",
    "base_import",
    "bus",
    "mail",
    "digest",
    "iap",
    "web_tour",
    "web_editor",
    "portal",
    "resource",
    # Calendar
    "calendar",
    # Contacts/CRM
    "contacts",
    "sales_team",
    "crm",
    "sale",
    "sale_management",
    "sale_crm",
    # Accounting
    "analytic",
    "account",
    "account_payment",
    # Purchase
    "purchase",
    "purchase_requisition",
    # Inventory
    "stock",
    "stock_account",
    "stock_landed_costs",
    "stock_picking_batch",
    "sale_stock",
    "sale_purchase",
    "purchase_stock",
    # Manufacturing
    "mrp",
    "maintenance",
    # Project
    "project",
    "project_todo",
    "hr_timesheet",
    "sale_timesheet",
    # HR
    "hr",
    "hr_contract",
    "hr_holidays",
    "hr_attendance",
    "hr_expense",
    "hr_recruitment",
    "hr_skills",
    # Website
    "website",
    "website_sale",
    "website_crm",
    "website_blog",
    "website_forum",
    "website_slides",
    "website_event",
    "website_hr_recruitment",
    # Marketing
    "mass_mailing",
    "mass_mailing_sms",
    # Point of Sale
    "point_of_sale",
    "pos_restaurant",
    # Others
    "survey",
    "lunch",
    "fleet",
    "repair",
    "im_livechat",
    "sms",
    "snailmail",
    "payment",
    "auth_signup",
    "auth_oauth",
    "auth_totp",
    "l10n_generic_coa",
}

# Known Enterprise-only modules
ENTERPRISE_ONLY = {
    "accountant",
    "knowledge",
    "web_studio",
    "sign",
    "helpdesk",
    "planning",
    "sale_subscription",
    "quality_control",
    "hr_appraisal",
    "marketing_automation",
    "appointment",
    "web_mobile",
    "stock_barcode",
    "voip",
    "sale_amazon",
    "industry_fsm",
    "timesheet_grid",
    "mrp_workorder",
    "data_recycle",
    "marketing_card",
    "social",
}

# OCA equivalents mapping
OCA_EQUIVALENTS = {
    "accountant": {
        "modules": [
            "account_financial_report",
            "mis_builder",
            "mis_builder_budget",
            "account_asset_management",
            "account_reconcile_oca",
        ],
        "repos": [
            "OCA/account-financial-reporting",
            "OCA/mis-builder",
            "OCA/account-financial-tools",
        ],
        "parity": "95%",
        "notes": "Full replacement except for some automated entries",
    },
    "mrp_workorder": {
        "modules": [
            "mrp_multi_level",
            "mrp_multi_level_estimate",
            "mrp_production_request",
            "mrp_workorder_sequence",
        ],
        "repos": ["OCA/manufacture"],
        "parity": "90%",
        "notes": "Missing tablet view, but core functionality covered",
    },
    "hr_appraisal": {
        "modules": ["hr_appraisal"],
        "repos": ["OCA/hr"],
        "parity": "85%",
        "notes": "Basic appraisal flow, customize for goals",
    },
    "timesheet_grid": {
        "modules": [
            "hr_timesheet_sheet",
            "hr_timesheet_task_required",
            "project_timesheet_time_control",
        ],
        "repos": ["OCA/timesheet", "OCA/project"],
        "parity": "90%",
        "notes": "Grid view via sheet, slightly different UX",
    },
    "sale_subscription": {
        "modules": ["sale_subscription"],
        "repos": ["OCA/sale-workflow"],
        "parity": "80%",
        "notes": "Core subscription logic, may need customization",
    },
    "helpdesk": {
        "modules": [
            "helpdesk_mgmt",
            "helpdesk_mgmt_timesheet",
            "helpdesk_mgmt_project",
        ],
        "repos": ["OCA/helpdesk"],
        "parity": "85%",
        "notes": "Full ticketing, SLA via custom fields",
    },
    "planning": {
        "modules": [
            "project_timeline",
            "project_stage_closed",
            "project_task_dependency",
        ],
        "repos": ["OCA/project"],
        "parity": "75%",
        "notes": "Timeline view available, Gantt needs frontend work",
    },
    "quality_control": {
        "modules": ["quality_control", "quality_control_stock"],
        "repos": ["OCA/manufacture"],
        "parity": "70%",
        "notes": "Basic QC, advanced metrics via Control Room",
    },
    "social": {
        "modules": [],
        "repos": [],
        "parity": "60%",
        "notes": "n8n workflows for posting, no unified dashboard",
        "replacement_type": "n8n",
    },
    "knowledge": {
        "modules": ["knowledge"],
        "repos": ["OCA/knowledge"],
        "parity": "70%",
        "notes": "Basic knowledge base, or use control_room.kb custom replacement",
    },
    "web_studio": {
        "modules": [],
        "repos": [],
        "parity": "50%",
        "notes": "No direct OCA equivalent; use control_room.studio custom replacement",
    },
    "sign": {
        "modules": [],
        "repos": [],
        "parity": "60%",
        "notes": "No direct OCA equivalent; use control_room.sign with DocuSign integration",
    },
    "appointment": {
        "modules": ["calendar_ics"],
        "repos": ["OCA/calendar"],
        "parity": "60%",
        "notes": "Limited OCA options; use control_room.booking custom replacement",
    },
    "industry_fsm": {
        "modules": ["fieldservice", "fieldservice_project"],
        "repos": ["OCA/field-service"],
        "parity": "80%",
        "notes": "OCA Field Service suite provides good coverage",
    },
    "stock_barcode": {
        "modules": ["stock_barcodes"],
        "repos": ["OCA/stock-logistics-barcode"],
        "parity": "70%",
        "notes": "Basic barcode scanning; or use control_room.barcode",
    },
    "web_mobile": {
        "modules": ["web_responsive"],
        "repos": ["OCA/web"],
        "parity": "50%",
        "notes": "Responsive web only; no native mobile app",
    },
    "marketing_automation": {
        "modules": ["mass_mailing_automation"],
        "repos": ["OCA/social"],
        "parity": "60%",
        "notes": "Basic automation; use n8n for complex workflows",
    },
    "voip": {
        "modules": [],
        "repos": [],
        "parity": "0%",
        "notes": "No OCA equivalent; requires third-party integration",
    },
    "sale_amazon": {
        "modules": [],
        "repos": [],
        "parity": "0%",
        "notes": "No OCA equivalent; use n8n Amazon connector",
    },
    "data_recycle": {
        "modules": ["auto_backup", "database_cleanup"],
        "repos": ["OCA/server-tools"],
        "parity": "50%",
        "notes": "Different approach; cleanup vs recycle bin",
    },
    "marketing_card": {
        "modules": [],
        "repos": [],
        "parity": "0%",
        "notes": "No OCA equivalent; Enterprise-specific feature",
    },
}


@dataclass
class ModuleInfo:
    name: str
    classification: str  # CE, OCA, custom, enterprise-only
    found_path: Optional[str] = None
    manifest_name: Optional[str] = None
    version: Optional[str] = None
    depends: List[str] = field(default_factory=list)
    is_application: bool = False
    installable: str = "Unknown"
    upgradeable: str = "Unknown"
    oca_equivalents: List[str] = field(default_factory=list)
    oca_repos: List[str] = field(default_factory=list)
    oca_parity: str = ""
    notes: str = ""


def parse_manifest(manifest_path: Path) -> Optional[Dict]:
    """Parse __manifest__.py file and return its contents."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
        return ast.literal_eval(content)
    except Exception as e:
        return None


def find_module_in_addons(module_name: str) -> Tuple[Optional[Path], str]:
    """Find a module in the local addons directories."""
    # Check main addons directory
    module_path = ADDONS_ROOT / module_name
    if module_path.exists() and (module_path / "__manifest__.py").exists():
        return module_path, "custom"

    # Check nested ipai directory
    module_path = IPAI_NESTED / module_name
    if module_path.exists() and (module_path / "__manifest__.py").exists():
        return module_path, "custom"

    # Check external-src OCA directories
    for oca_repo in EXTERNAL_SRC.iterdir():
        if oca_repo.is_dir():
            module_path = oca_repo / module_name
            if module_path.exists() and (module_path / "__manifest__.py").exists():
                return module_path, "OCA"

    return None, ""


def classify_module(module_name: str) -> ModuleInfo:
    """Classify a module and gather all relevant information."""
    info = ModuleInfo(name=module_name, classification="unknown")

    # Check if it's a custom ipai_* module
    if module_name.startswith("ipai_"):
        found_path, _ = find_module_in_addons(module_name)
        if found_path:
            info.classification = "custom"
            info.found_path = str(found_path)
            manifest = parse_manifest(found_path / "__manifest__.py")
            if manifest:
                info.manifest_name = manifest.get("name", module_name)
                info.version = manifest.get("version", "Unknown")
                info.depends = manifest.get("depends", [])
                info.is_application = manifest.get("application", False)
                info.installable = "Y" if manifest.get("installable", True) else "N"
            info.notes = "Custom IPAI module"
        else:
            info.classification = "custom"
            info.notes = "Custom IPAI module (path not found)"
        return info

    # Check if it's a CE core module
    if module_name in CE_CORE_MODULES:
        info.classification = "CE"
        info.found_path = f"/usr/lib/python3/dist-packages/odoo/addons/{module_name}"
        info.installable = "Y"
        info.notes = "Odoo CE core module"
        return info

    # Check if it's Enterprise-only
    if module_name in ENTERPRISE_ONLY:
        info.classification = "enterprise-only"
        info.notes = "Enterprise-only module (not available in CE)"

        # Add OCA equivalent info if available
        if module_name in OCA_EQUIVALENTS:
            equiv = OCA_EQUIVALENTS[module_name]
            info.oca_equivalents = equiv.get("modules", [])
            info.oca_repos = equiv.get("repos", [])
            info.oca_parity = equiv.get("parity", "")
            if equiv.get("notes"):
                info.notes += f". OCA: {equiv['notes']}"
            if equiv.get("replacement_type") == "n8n":
                info.notes += " (n8n replacement available)"

        return info

    # Check local addons
    found_path, classification = find_module_in_addons(module_name)
    if found_path:
        info.classification = classification
        info.found_path = str(found_path)
        manifest = parse_manifest(found_path / "__manifest__.py")
        if manifest:
            info.manifest_name = manifest.get("name", module_name)
            info.version = manifest.get("version", "Unknown")
            info.depends = manifest.get("depends", [])
            info.is_application = manifest.get("application", False)
            info.installable = "Y" if manifest.get("installable", True) else "N"
        return info

    # Unknown module - might be CE core we missed
    info.classification = "unknown"
    info.notes = "Module not found in any addons path"
    return info


def discover_ipai_modules() -> List[str]:
    """Discover all ipai_* modules in the repository."""
    modules = []

    # Scan main addons directory
    for item in ADDONS_ROOT.iterdir():
        if item.is_dir() and item.name.startswith("ipai_"):
            if (item / "__manifest__.py").exists():
                modules.append(item.name)

    # Scan nested ipai directory
    if IPAI_NESTED.exists():
        for item in IPAI_NESTED.iterdir():
            if item.is_dir() and item.name.startswith("ipai_"):
                if (item / "__manifest__.py").exists():
                    if item.name not in modules:
                        modules.append(item.name)

    return sorted(modules)


@dataclass
class QualityCheckResult:
    module: str
    status: str  # PASS, FAIL, WARNING
    stage: str  # static, startup, install, upgrade, ui
    error_summary: str = ""
    file_line: str = ""
    fix_recommendation: str = ""


def check_manifest_syntax(module_path: Path) -> Optional[str]:
    """Check if __manifest__.py has valid Python syntax."""
    manifest_file = module_path / "__manifest__.py"
    if not manifest_file.exists():
        return f"__manifest__.py missing"

    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        ast.literal_eval(content)
        return None
    except SyntaxError as e:
        return f"Syntax error: {e}"
    except ValueError as e:
        return f"Invalid manifest literal: {e}"


def check_init_files(module_path: Path) -> List[str]:
    """Check for proper __init__.py files."""
    issues = []

    # Check root __init__.py
    root_init = module_path / "__init__.py"
    if not root_init.exists():
        issues.append(f"Missing root __init__.py")

    # Check subdirectories that should have __init__.py
    for subdir in ["models", "wizards", "controllers", "reports"]:
        subdir_path = module_path / subdir
        if subdir_path.exists() and subdir_path.is_dir():
            subdir_init = subdir_path / "__init__.py"
            if not subdir_init.exists():
                issues.append(f"Missing {subdir}/__init__.py")

    return issues


def check_xml_wellformed(module_path: Path) -> List[str]:
    """Check if all XML files are well-formed."""
    issues = []

    for xml_file in module_path.rglob("*.xml"):
        try:
            ET.parse(xml_file)
        except ET.ParseError as e:
            rel_path = xml_file.relative_to(module_path)
            issues.append(f"XML parse error in {rel_path}: {e}")

    return issues


def check_security_csv(module_path: Path) -> List[str]:
    """Check for security/ir.model.access.csv if models are defined."""
    issues = []

    # Check if there are model definitions
    models_dir = module_path / "models"
    if not models_dir.exists():
        return issues

    has_models = False
    for py_file in models_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                if re.search(r"class\s+\w+\(models\.(Model|TransientModel)\)", content):
                    has_models = True
                    break
        except Exception:
            pass

    if has_models:
        security_csv = module_path / "security" / "ir.model.access.csv"
        if not security_csv.exists():
            issues.append(
                "Module defines models but missing security/ir.model.access.csv"
            )

    return issues


def check_python_imports(module_path: Path) -> List[str]:
    """Check if Python files can be compiled."""
    issues = []

    for py_file in module_path.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            compile(content, str(py_file), "exec")
        except SyntaxError as e:
            rel_path = py_file.relative_to(module_path)
            issues.append(f"Python syntax error in {rel_path}:{e.lineno}: {e.msg}")

    return issues


def check_dependencies(module_path: Path, all_modules: Set[str]) -> List[str]:
    """Check if all dependencies exist."""
    issues = []

    manifest = parse_manifest(module_path / "__manifest__.py")
    if not manifest:
        return issues

    depends = manifest.get("depends", [])
    for dep in depends:
        if dep not in all_modules and dep not in CE_CORE_MODULES:
            issues.append(f"Dependency '{dep}' not found in addons path")

    return issues


def quality_gate_audit(
    module_name: str, module_path: Path, all_modules: Set[str]
) -> List[QualityCheckResult]:
    """Run quality gate checks on a single module."""
    results = []

    # 1. Manifest syntax check
    manifest_issue = check_manifest_syntax(module_path)
    if manifest_issue:
        results.append(
            QualityCheckResult(
                module=module_name,
                status="FAIL",
                stage="static",
                error_summary=manifest_issue,
                file_line=f"{module_path}/__manifest__.py",
                fix_recommendation="Fix Python syntax in __manifest__.py",
            )
        )
        return results  # Cannot continue without valid manifest

    # 2. Init files check
    init_issues = check_init_files(module_path)
    for issue in init_issues:
        results.append(
            QualityCheckResult(
                module=module_name,
                status="FAIL",
                stage="static",
                error_summary=issue,
                file_line=str(module_path),
                fix_recommendation=f"Create missing __init__.py file",
            )
        )

    # 3. XML well-formedness
    xml_issues = check_xml_wellformed(module_path)
    for issue in xml_issues:
        results.append(
            QualityCheckResult(
                module=module_name,
                status="FAIL",
                stage="static",
                error_summary=issue,
                file_line=str(module_path),
                fix_recommendation="Fix XML syntax errors",
            )
        )

    # 4. Security CSV check
    security_issues = check_security_csv(module_path)
    for issue in security_issues:
        results.append(
            QualityCheckResult(
                module=module_name,
                status="WARNING",
                stage="static",
                error_summary=issue,
                file_line=f"{module_path}/security/ir.model.access.csv",
                fix_recommendation="Add security/ir.model.access.csv with model access rules",
            )
        )

    # 5. Python compilation
    python_issues = check_python_imports(module_path)
    for issue in python_issues:
        results.append(
            QualityCheckResult(
                module=module_name,
                status="FAIL",
                stage="static",
                error_summary=issue,
                file_line=str(module_path),
                fix_recommendation="Fix Python syntax errors",
            )
        )

    # 6. Dependency check
    dep_issues = check_dependencies(module_path, all_modules)
    for issue in dep_issues:
        results.append(
            QualityCheckResult(
                module=module_name,
                status="FAIL",
                stage="static",
                error_summary=issue,
                file_line=f"{module_path}/__manifest__.py",
                fix_recommendation="Add missing dependency to addons path or remove from depends",
            )
        )

    # If no issues found, module passes
    if not results:
        results.append(
            QualityCheckResult(
                module=module_name,
                status="PASS",
                stage="static",
                error_summary="All static checks passed",
                fix_recommendation="",
            )
        )

    return results


def generate_markdown_report(
    modules: List[ModuleInfo],
    quality_results: Dict[str, List[QualityCheckResult]],
    output_path: Path,
):
    """Generate markdown report."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# CE/OCA Equivalents Audit Report\n\n")
        f.write(f"**Odoo Version:** {ODOO_VERSION}\n\n")
        f.write(f"**Generated:** {os.popen('date').read().strip()}\n\n")
        f.write("**Addons Paths:**\n")
        f.write(f"- Custom: `{ADDONS_ROOT}`\n")
        f.write(f"- Custom (nested): `{IPAI_NESTED}`\n")
        f.write(f"- OCA: `{EXTERNAL_SRC}`\n")
        f.write(
            f"- CE Core: `/usr/lib/python3/dist-packages/odoo/addons` (Docker image)\n\n"
        )

        f.write("## Module Classification Summary\n\n")

        # Count by classification
        counts = {"CE": 0, "OCA": 0, "custom": 0, "enterprise-only": 0, "unknown": 0}
        for m in modules:
            counts[m.classification] = counts.get(m.classification, 0) + 1

        f.write(f"| Classification | Count |\n")
        f.write(f"|----------------|-------|\n")
        for cls, count in counts.items():
            f.write(f"| {cls} | {count} |\n")
        f.write("\n")

        f.write("## Module Details\n\n")
        f.write(
            "| Module | App Label | Classification | Found Path | Installable | Upgradeable | OCA Equivalents | Notes |\n"
        )
        f.write(
            "|--------|-----------|----------------|------------|-------------|-------------|-----------------|-------|\n"
        )

        for m in modules:
            app_label = m.manifest_name or m.name
            found_path = m.found_path or "-"
            if len(found_path) > 40:
                found_path = "..." + found_path[-37:]
            oca_equiv = ", ".join(m.oca_equivalents[:3]) if m.oca_equivalents else "-"
            notes = m.notes[:50] + "..." if len(m.notes) > 50 else m.notes

            f.write(
                f"| {m.name} | {app_label} | {m.classification} | `{found_path}` | {m.installable} | {m.upgradeable} | {oca_equiv} | {notes} |\n"
            )

        # Enterprise-only modules with compliance risk
        enterprise_modules = [
            m for m in modules if m.classification == "enterprise-only"
        ]
        if enterprise_modules:
            f.write("\n## Enterprise-Only Modules (Compliance Risk)\n\n")
            f.write(
                "These modules are Enterprise-only and require licensing or OCA alternatives:\n\n"
            )
            for m in enterprise_modules:
                f.write(f"### {m.name}\n\n")
                if m.oca_equivalents:
                    f.write(f"**OCA Equivalents:** {', '.join(m.oca_equivalents)}\n\n")
                    f.write(f"**OCA Repos:** {', '.join(m.oca_repos)}\n\n")
                    f.write(f"**Parity:** {m.oca_parity}\n\n")
                f.write(f"**Notes:** {m.notes}\n\n")

        # Quality gate results
        if quality_results:
            f.write("\n---\n\n")
            f.write("# IPAI Module Quality Gate Report\n\n")

            # Summary
            total_modules = len(quality_results)
            passed = sum(
                1
                for results in quality_results.values()
                if all(r.status == "PASS" for r in results)
            )
            failed = sum(
                1
                for results in quality_results.values()
                if any(r.status == "FAIL" for r in results)
            )
            warnings = sum(
                1
                for results in quality_results.values()
                if any(r.status == "WARNING" for r in results)
                and not any(r.status == "FAIL" for r in results)
            )

            f.write("## Summary\n\n")
            f.write(f"| Status | Count |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| PASS | {passed} |\n")
            f.write(f"| FAIL | {failed} |\n")
            f.write(f"| WARNING | {warnings} |\n")
            f.write(f"| **Total** | {total_modules} |\n\n")

            f.write("## Quality Gate Results\n\n")
            f.write(
                "| Module | Status | Stage | Error Summary | File/Line | Fix Recommendation |\n"
            )
            f.write(
                "|--------|--------|-------|---------------|-----------|--------------------|\n"
            )

            for module_name, results in sorted(quality_results.items()):
                for r in results:
                    error_summary = (
                        r.error_summary[:40] + "..."
                        if len(r.error_summary) > 40
                        else r.error_summary
                    )
                    file_line = (
                        r.file_line[-30:] if len(r.file_line) > 30 else r.file_line
                    )
                    fix = (
                        r.fix_recommendation[:30] + "..."
                        if len(r.fix_recommendation) > 30
                        else r.fix_recommendation
                    )
                    f.write(
                        f"| {r.module} | {r.status} | {r.stage} | {error_summary} | `{file_line}` | {fix} |\n"
                    )

            # Blockers section
            blockers = [
                (mod, r)
                for mod, results in quality_results.items()
                for r in results
                if r.status == "FAIL"
            ]
            if blockers:
                f.write("\n## Blockers (Must Fix)\n\n")
                for mod, r in blockers:
                    f.write(f"- **{mod}**: {r.error_summary}\n")
                    f.write(f"  - File: `{r.file_line}`\n")
                    f.write(f"  - Fix: {r.fix_recommendation}\n\n")


def generate_csv(modules: List[ModuleInfo], output_path: Path):
    """Generate CSV report."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "module",
                "app_label",
                "classification",
                "found_path",
                "installable",
                "upgradeable",
                "oca_equivalents",
                "oca_repos",
                "oca_parity",
                "notes",
            ]
        )
        for m in modules:
            writer.writerow(
                [
                    m.name,
                    m.manifest_name or m.name,
                    m.classification,
                    m.found_path or "",
                    m.installable,
                    m.upgradeable,
                    ";".join(m.oca_equivalents),
                    ";".join(m.oca_repos),
                    m.oca_parity,
                    m.notes,
                ]
            )


def generate_json(
    modules: List[ModuleInfo],
    quality_results: Dict[str, List[QualityCheckResult]],
    output_path: Path,
):
    """Generate JSON report."""
    data = {
        "environment": {
            "odoo_version": ODOO_VERSION,
            "addons_paths": {
                "custom": str(ADDONS_ROOT),
                "custom_nested": str(IPAI_NESTED),
                "oca": str(EXTERNAL_SRC),
                "ce_core": "/usr/lib/python3/dist-packages/odoo/addons",
            },
        },
        "modules": [],
        "quality_gate": {},
    }

    for m in modules:
        data["modules"].append(
            {
                "name": m.name,
                "classification": m.classification,
                "found_path": m.found_path,
                "manifest_name": m.manifest_name,
                "version": m.version,
                "depends": m.depends,
                "is_application": m.is_application,
                "installable": m.installable,
                "upgradeable": m.upgradeable,
                "oca_equivalents": m.oca_equivalents,
                "oca_repos": m.oca_repos,
                "oca_parity": m.oca_parity,
                "notes": m.notes,
            }
        )

    for module_name, results in quality_results.items():
        data["quality_gate"][module_name] = [
            {
                "status": r.status,
                "stage": r.stage,
                "error_summary": r.error_summary,
                "file_line": r.file_line,
                "fix_recommendation": r.fix_recommendation,
            }
            for r in results
        ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    """Main audit function."""
    print("=" * 70)
    print("Odoo 18 CE + OCA Module Auditor")
    print("=" * 70)

    # Environment detection
    print(f"\n[1/4] Environment Detection")
    print(f"  Odoo Version: {ODOO_VERSION}")
    print(f"  Addons Root: {ADDONS_ROOT}")
    print(f"  IPAI Nested: {IPAI_NESTED}")
    print(f"  External-src: {EXTERNAL_SRC}")

    # Discover all ipai modules
    ipai_modules = discover_ipai_modules()
    print(f"\n  Found {len(ipai_modules)} ipai_* modules locally")

    # Build set of all available modules
    all_local_modules = set(ipai_modules) | CE_CORE_MODULES

    # CE/OCA Equivalents Audit
    print(f"\n[2/4] CE/OCA Equivalents Audit")
    print(f"  Analyzing {len(APPS_LIST)} modules from apps list...")

    modules = []
    for module_name in APPS_LIST:
        info = classify_module(module_name)
        modules.append(info)
        status_icon = (
            "✓"
            if info.classification in ["CE", "custom"]
            else "⚠" if info.classification == "OCA" else "✗"
        )
        print(f"    {status_icon} {module_name}: {info.classification}")

    # Quality Gate Audit for ipai_* modules
    print(f"\n[3/4] Quality Gate Audit for ipai_* modules")
    quality_results: Dict[str, List[QualityCheckResult]] = {}

    for module_name in ipai_modules:
        # Find module path
        module_path = ADDONS_ROOT / module_name
        if not module_path.exists():
            module_path = IPAI_NESTED / module_name

        if module_path.exists():
            results = quality_gate_audit(module_name, module_path, all_local_modules)
            quality_results[module_name] = results

            # Print summary
            has_fail = any(r.status == "FAIL" for r in results)
            has_warn = any(r.status == "WARNING" for r in results)
            if has_fail:
                status = "FAIL"
                icon = "✗"
            elif has_warn:
                status = "WARNING"
                icon = "⚠"
            else:
                status = "PASS"
                icon = "✓"
            print(f"    {icon} {module_name}: {status}")

    # Generate outputs
    print(f"\n[4/4] Generating Output Deliverables")

    # Create output directories
    docs_dir = REPO_ROOT / "docs"
    artifacts_dir = REPO_ROOT / "artifacts"
    docs_dir.mkdir(exist_ok=True)
    artifacts_dir.mkdir(exist_ok=True)

    # Generate reports
    md_path = docs_dir / "CE_OCA_EQUIVALENTS_AUDIT.md"
    csv_path = artifacts_dir / "ce_oca_equivalents_audit.csv"
    json_path = artifacts_dir / "ce_oca_equivalents_audit.json"
    quality_csv_path = artifacts_dir / "ipai_quality_gate.csv"
    quality_json_path = artifacts_dir / "ipai_quality_gate.json"

    generate_markdown_report(modules, quality_results, md_path)
    print(f"  ✓ Markdown report: {md_path}")

    generate_csv(modules, csv_path)
    print(f"  ✓ CSV report: {csv_path}")

    generate_json(modules, quality_results, json_path)
    print(f"  ✓ JSON report: {json_path}")

    # Generate separate quality gate outputs
    with open(quality_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "module",
                "status",
                "stage",
                "error_summary",
                "file_line",
                "fix_recommendation",
            ]
        )
        for module_name, results in sorted(quality_results.items()):
            for r in results:
                writer.writerow(
                    [
                        r.module,
                        r.status,
                        r.stage,
                        r.error_summary,
                        r.file_line,
                        r.fix_recommendation,
                    ]
                )
    print(f"  ✓ Quality gate CSV: {quality_csv_path}")

    with open(quality_json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "environment": {
                    "odoo_version": ODOO_VERSION,
                    "custom_addons_root": str(ADDONS_ROOT),
                },
                "results": {
                    mod: [asdict(r) for r in results]
                    for mod, results in quality_results.items()
                },
            },
            f,
            indent=2,
        )
    print(f"  ✓ Quality gate JSON: {quality_json_path}")

    # Summary
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

    ce_count = sum(1 for m in modules if m.classification == "CE")
    custom_count = sum(1 for m in modules if m.classification == "custom")
    enterprise_count = sum(1 for m in modules if m.classification == "enterprise-only")

    passed_count = sum(
        1
        for results in quality_results.values()
        if all(r.status == "PASS" for r in results)
    )
    failed_count = sum(
        1
        for results in quality_results.values()
        if any(r.status == "FAIL" for r in results)
    )

    print(f"\nApps List Analysis ({len(modules)} modules):")
    print(f"  - CE Core: {ce_count}")
    print(f"  - Custom (ipai_*): {custom_count}")
    print(f"  - Enterprise-only: {enterprise_count}")

    print(f"\nIPAI Quality Gate ({len(quality_results)} modules):")
    print(f"  - PASS: {passed_count}")
    print(f"  - FAIL: {failed_count}")

    if failed_count > 0:
        print(f"\n⚠ WARNING: {failed_count} modules have blocking issues!")
        print("  Review docs/CE_OCA_EQUIVALENTS_AUDIT.md for details.")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
