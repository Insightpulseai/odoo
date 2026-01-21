#!/usr/bin/env python3
"""
IPAI Module Full Auditor
Comprehensive audit of all IPAI modules for Odoo 18 CE.

This script:
1. Parses all module manifests and builds a dependency graph
2. Runs static validation (manifest, python, xml, security)
3. Generates per-module documentation
4. Creates the IPAI_MODULES_INDEX.md
5. Prepares install/upgrade test matrix (actual execution requires odoo-bin)
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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import hashlib

# Configuration
REPO_ROOT = Path("/home/user/odoo-ce")
ADDONS_ROOT = REPO_ROOT / "addons"
IPAI_NESTED = ADDONS_ROOT / "ipai"
DOCS_DIR = REPO_ROOT / "docs"
MODULES_DOCS_DIR = DOCS_DIR / "modules"
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
LOGS_DIR = ARTIFACTS_DIR / "logs"

# Odoo version
ODOO_VERSION = "18.0"

# Modules in scope for this audit
SCOPE_MODULES = [
    "ipai_workos_affine",
    "ipai_workos_core",
    "ipai_bir_tax_compliance",
    "ipai_close_orchestration",
    "ipai_finance_ppm",
    "ipai_finance_ppm_golive",
    "ipai_month_end",
    "ipai_ppm_a1",
    "ipai_superset_connector",
    "ipai_tbwa_finance",
    "ipai",
    "ipai_ask_ai",
    "ipai_crm_pipeline",
    "ipai_finance_closing",
    "ipai_finance_monthly_closing",
    "ipai_finance_ppm_umbrella",
    "ipai_grid_view",
    "ipai_month_end_closing",
    "ipai_platform_approvals",
    "ipai_platform_audit",
    "ipai_platform_permissions",
    "ipai_platform_theme",
    "ipai_platform_workflow",
    "ipai_ppm_monthly_close",
    "ipai_theme_tbwa_backend",
    "ipai_workos_blocks",
    "ipai_workos_canvas",
    "ipai_workos_collab",
    "ipai_workos_db",
    "ipai_workos_search",
    "ipai_workos_templates",
    "ipai_workos_views",
]

# CE Core modules (for dependency checking)
CE_CORE_MODULES = {
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
    "calendar",
    "contacts",
    "sales_team",
    "crm",
    "sale",
    "sale_management",
    "sale_crm",
    "analytic",
    "account",
    "account_payment",
    "purchase",
    "purchase_requisition",
    "stock",
    "stock_account",
    "stock_landed_costs",
    "stock_picking_batch",
    "sale_stock",
    "sale_purchase",
    "purchase_stock",
    "mrp",
    "maintenance",
    "project",
    "project_todo",
    "hr_timesheet",
    "sale_timesheet",
    "hr",
    "hr_contract",
    "hr_holidays",
    "hr_attendance",
    "hr_expense",
    "hr_recruitment",
    "hr_skills",
    "website",
    "website_sale",
    "website_crm",
    "website_blog",
    "website_forum",
    "website_slides",
    "website_event",
    "website_hr_recruitment",
    "mass_mailing",
    "mass_mailing_sms",
    "point_of_sale",
    "pos_restaurant",
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

# Enterprise modules (blocklist)
ENTERPRISE_BLOCKLIST = {
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


@dataclass
class ModuleAuditInfo:
    """Complete audit information for a module."""

    name: str
    display_name: str = ""
    version: str = ""
    category: str = ""
    license: str = ""
    author: str = ""
    summary: str = ""
    description: str = ""
    is_application: bool = False
    installable: bool = True
    depends: List[str] = field(default_factory=list)
    data_files: List[str] = field(default_factory=list)
    demo_files: List[str] = field(default_factory=list)
    assets: Dict[str, Any] = field(default_factory=dict)

    # Path info
    path: str = ""
    location: str = ""  # "top-level" or "nested"

    # Extracted info
    models: List[Dict] = field(default_factory=list)
    views: List[Dict] = field(default_factory=list)
    menus: List[Dict] = field(default_factory=list)
    security_groups: List[Dict] = field(default_factory=list)
    access_rules: List[Dict] = field(default_factory=list)
    record_rules: List[Dict] = field(default_factory=list)
    system_params: List[Dict] = field(default_factory=list)
    cron_jobs: List[Dict] = field(default_factory=list)

    # Validation results
    static_checks: List[Dict] = field(default_factory=list)
    has_readme: bool = False
    docs_coverage: str = ""

    # Test status
    install_status: str = "pending"
    upgrade_status: str = "pending"
    install_error: str = ""
    upgrade_error: str = ""


def parse_manifest(manifest_path: Path) -> Optional[Dict]:
    """Parse __manifest__.py file and return its contents."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
        return ast.literal_eval(content)
    except Exception as e:
        return None


def find_module_path(module_name: str) -> Tuple[Optional[Path], str]:
    """Find module path, return (path, location) tuple."""
    # Check top-level addons directory
    module_path = ADDONS_ROOT / module_name
    if module_path.exists() and (module_path / "__manifest__.py").exists():
        return module_path, "top-level"

    # Check nested ipai directory
    module_path = IPAI_NESTED / module_name
    if module_path.exists() and (module_path / "__manifest__.py").exists():
        return module_path, "nested"

    return None, ""


def extract_models_from_file(py_file: Path) -> List[Dict]:
    """Extract model definitions from a Python file."""
    models = []
    try:
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check for Odoo model inheritance
                for base in node.bases:
                    base_str = ""
                    if isinstance(base, ast.Attribute):
                        if hasattr(base.value, "id") and base.value.id == "models":
                            base_str = f"models.{base.attr}"

                    if base_str in [
                        "models.Model",
                        "models.TransientModel",
                        "models.AbstractModel",
                    ]:
                        model_info = {
                            "class_name": node.name,
                            "model_type": base_str.split(".")[-1],
                            "_name": None,
                            "_inherit": None,
                            "_description": None,
                            "fields": [],
                        }

                        # Extract class body assignments
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        name = target.id
                                        if name == "_name" and isinstance(
                                            item.value, ast.Constant
                                        ):
                                            model_info["_name"] = item.value.value
                                        elif name == "_inherit":
                                            if isinstance(item.value, ast.Constant):
                                                model_info["_inherit"] = (
                                                    item.value.value
                                                )
                                            elif isinstance(item.value, ast.List):
                                                model_info["_inherit"] = [
                                                    e.value
                                                    for e in item.value.elts
                                                    if isinstance(e, ast.Constant)
                                                ]
                                        elif name == "_description" and isinstance(
                                            item.value, ast.Constant
                                        ):
                                            model_info["_description"] = (
                                                item.value.value
                                            )
                                        elif isinstance(item.value, ast.Call):
                                            # Field definition
                                            if hasattr(item.value.func, "attr"):
                                                field_type = item.value.func.attr
                                                if field_type in [
                                                    "Char",
                                                    "Text",
                                                    "Integer",
                                                    "Float",
                                                    "Boolean",
                                                    "Date",
                                                    "Datetime",
                                                    "Binary",
                                                    "Html",
                                                    "Selection",
                                                    "Many2one",
                                                    "One2many",
                                                    "Many2many",
                                                ]:
                                                    model_info["fields"].append(
                                                        {
                                                            "name": name,
                                                            "type": field_type,
                                                        }
                                                    )

                        if model_info["_name"] or model_info["_inherit"]:
                            models.append(model_info)
    except Exception as e:
        pass

    return models


def extract_views_from_xml(xml_file: Path) -> List[Dict]:
    """Extract view definitions from XML file."""
    views = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Handle both odoo and openerp tags
        for record in root.findall(".//record"):
            model = record.get("model", "")
            if model == "ir.ui.view":
                view_info = {
                    "id": record.get("id", ""),
                    "model": "",
                    "type": "",
                    "name": "",
                    "inherit_id": None,
                }

                for field in record.findall("field"):
                    fname = field.get("name", "")
                    if fname == "name":
                        view_info["name"] = field.text or ""
                    elif fname == "model":
                        view_info["model"] = field.text or ""
                    elif fname == "arch":
                        # Determine view type from arch content
                        arch_text = ET.tostring(field, encoding="unicode")
                        for vtype in [
                            "tree",
                            "form",
                            "kanban",
                            "calendar",
                            "graph",
                            "pivot",
                            "search",
                            "activity",
                        ]:
                            if f"<{vtype}" in arch_text:
                                view_info["type"] = vtype
                                break
                    elif fname == "inherit_id":
                        view_info["inherit_id"] = field.get("ref", "")

                if view_info["id"]:
                    views.append(view_info)
    except Exception:
        pass

    return views


def extract_menus_from_xml(xml_file: Path) -> List[Dict]:
    """Extract menu definitions from XML file."""
    menus = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Handle menuitem shortcut
        for menuitem in root.findall(".//menuitem"):
            menu_info = {
                "id": menuitem.get("id", ""),
                "name": menuitem.get("name", ""),
                "parent": menuitem.get("parent", ""),
                "action": menuitem.get("action", ""),
                "sequence": menuitem.get("sequence", "10"),
            }
            if menu_info["id"]:
                menus.append(menu_info)

        # Handle record-based menus
        for record in root.findall(".//record[@model='ir.ui.menu']"):
            menu_info = {
                "id": record.get("id", ""),
                "name": "",
                "parent": "",
                "action": "",
            }
            for field in record.findall("field"):
                fname = field.get("name", "")
                if fname == "name":
                    menu_info["name"] = field.text or ""
                elif fname == "parent_id":
                    menu_info["parent"] = field.get("ref", "")
                elif fname == "action":
                    menu_info["action"] = field.get("ref", "")
            if menu_info["id"]:
                menus.append(menu_info)
    except Exception:
        pass

    return menus


def extract_security_from_csv(csv_file: Path) -> List[Dict]:
    """Extract access rules from ir.model.access.csv."""
    rules = []
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rules.append(
                    {
                        "id": row.get("id", ""),
                        "model": row.get("model_id:id", row.get("model_id/id", "")),
                        "group": row.get("group_id:id", row.get("group_id/id", "")),
                        "perm_read": row.get("perm_read", "0"),
                        "perm_write": row.get("perm_write", "0"),
                        "perm_create": row.get("perm_create", "0"),
                        "perm_unlink": row.get("perm_unlink", "0"),
                    }
                )
    except Exception:
        pass

    return rules


def extract_security_groups_from_xml(xml_file: Path) -> List[Dict]:
    """Extract security groups from XML."""
    groups = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for record in root.findall(".//record[@model='res.groups']"):
            group_info = {
                "id": record.get("id", ""),
                "name": "",
                "category": "",
                "implied_ids": [],
            }
            for field in record.findall("field"):
                fname = field.get("name", "")
                if fname == "name":
                    group_info["name"] = field.text or ""
                elif fname == "category_id":
                    group_info["category"] = field.get("ref", "")
                elif fname == "implied_ids":
                    group_info["implied_ids"] = [
                        el.text for el in field.findall("field") if el.text
                    ]
            if group_info["id"]:
                groups.append(group_info)
    except Exception:
        pass

    return groups


def extract_record_rules_from_xml(xml_file: Path) -> List[Dict]:
    """Extract record rules from XML."""
    rules = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for record in root.findall(".//record[@model='ir.rule']"):
            rule_info = {
                "id": record.get("id", ""),
                "name": "",
                "model": "",
                "domain": "",
                "groups": [],
            }
            for field in record.findall("field"):
                fname = field.get("name", "")
                if fname == "name":
                    rule_info["name"] = field.text or ""
                elif fname == "model_id":
                    rule_info["model"] = field.get("ref", "")
                elif fname == "domain_force":
                    rule_info["domain"] = field.text or ""
                elif fname == "groups":
                    rule_info["groups"] = field.get("eval", "")
            if rule_info["id"]:
                rules.append(rule_info)
    except Exception:
        pass

    return rules


def extract_system_params_from_xml(xml_file: Path) -> List[Dict]:
    """Extract system parameters from XML data files."""
    params = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for record in root.findall(".//record[@model='ir.config_parameter']"):
            param_info = {"id": record.get("id", ""), "key": "", "value": ""}
            for field in record.findall("field"):
                fname = field.get("name", "")
                if fname == "key":
                    param_info["key"] = field.text or ""
                elif fname == "value":
                    param_info["value"] = field.text or ""
            if param_info["key"]:
                params.append(param_info)
    except Exception:
        pass

    return params


def extract_cron_jobs_from_xml(xml_file: Path) -> List[Dict]:
    """Extract cron jobs from XML."""
    crons = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for record in root.findall(".//record[@model='ir.cron']"):
            cron_info = {
                "id": record.get("id", ""),
                "name": "",
                "model": "",
                "code": "",
                "interval_number": "",
                "interval_type": "",
                "active": True,
            }
            for field in record.findall("field"):
                fname = field.get("name", "")
                if fname == "name":
                    cron_info["name"] = field.text or ""
                elif fname == "model_id":
                    cron_info["model"] = field.get("ref", "")
                elif fname == "code":
                    cron_info["code"] = field.text or ""
                elif fname == "interval_number":
                    cron_info["interval_number"] = field.text or ""
                elif fname == "interval_type":
                    cron_info["interval_type"] = field.text or ""
                elif fname == "active":
                    cron_info["active"] = field.text != "False"
            if cron_info["id"]:
                crons.append(cron_info)
    except Exception:
        pass

    return crons


def run_static_checks(
    module_path: Path, module_name: str, all_modules: Set[str]
) -> List[Dict]:
    """Run static validation checks on a module."""
    checks = []

    # 1. Manifest syntax check
    manifest_file = module_path / "__manifest__.py"
    if not manifest_file.exists():
        checks.append(
            {
                "check": "manifest_exists",
                "status": "FAIL",
                "message": "__manifest__.py missing",
            }
        )
        return checks

    try:
        with open(manifest_file, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        manifest = ast.literal_eval(content)
        checks.append(
            {
                "check": "manifest_syntax",
                "status": "PASS",
                "message": "Valid Python syntax",
            }
        )

        # Check required fields
        if "name" not in manifest:
            checks.append(
                {
                    "check": "manifest_name",
                    "status": "FAIL",
                    "message": "Missing 'name' in manifest",
                }
            )

        if "version" not in manifest:
            checks.append(
                {
                    "check": "manifest_version",
                    "status": "WARNING",
                    "message": "Missing 'version' in manifest",
                }
            )

        if "license" not in manifest:
            checks.append(
                {
                    "check": "manifest_license",
                    "status": "WARNING",
                    "message": "Missing 'license' in manifest",
                }
            )

        if "depends" not in manifest or not manifest["depends"]:
            checks.append(
                {
                    "check": "manifest_depends",
                    "status": "WARNING",
                    "message": "No dependencies defined",
                }
            )

    except SyntaxError as e:
        checks.append(
            {
                "check": "manifest_syntax",
                "status": "FAIL",
                "message": f"Syntax error: {e}",
            }
        )
        return checks
    except ValueError as e:
        checks.append(
            {
                "check": "manifest_syntax",
                "status": "FAIL",
                "message": f"Invalid literal: {e}",
            }
        )
        return checks

    # 2. Check __init__.py exists
    init_file = module_path / "__init__.py"
    if not init_file.exists():
        checks.append(
            {
                "check": "init_exists",
                "status": "FAIL",
                "message": "Missing root __init__.py",
            }
        )
    else:
        checks.append(
            {"check": "init_exists", "status": "PASS", "message": "__init__.py present"}
        )

    # 3. Check subdirectory __init__.py files
    for subdir in ["models", "wizards", "controllers", "reports"]:
        subdir_path = module_path / subdir
        if subdir_path.exists() and subdir_path.is_dir():
            subdir_init = subdir_path / "__init__.py"
            if not subdir_init.exists():
                checks.append(
                    {
                        "check": f"init_{subdir}",
                        "status": "FAIL",
                        "message": f"Missing {subdir}/__init__.py",
                    }
                )

    # 4. Python compilation check
    for py_file in module_path.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            compile(content, str(py_file), "exec")
        except SyntaxError as e:
            rel_path = py_file.relative_to(module_path)
            checks.append(
                {
                    "check": "python_syntax",
                    "status": "FAIL",
                    "message": f"Syntax error in {rel_path}:{e.lineno}: {e.msg}",
                }
            )

    if not any(c["check"] == "python_syntax" for c in checks):
        checks.append(
            {
                "check": "python_syntax",
                "status": "PASS",
                "message": "All Python files compile",
            }
        )

    # 5. XML well-formedness check
    xml_errors = []
    for xml_file in module_path.rglob("*.xml"):
        try:
            ET.parse(xml_file)
        except ET.ParseError as e:
            rel_path = xml_file.relative_to(module_path)
            xml_errors.append(f"{rel_path}: {e}")

    if xml_errors:
        for error in xml_errors:
            checks.append({"check": "xml_syntax", "status": "FAIL", "message": error})
    else:
        checks.append(
            {
                "check": "xml_syntax",
                "status": "PASS",
                "message": "All XML files are well-formed",
            }
        )

    # 6. Security CSV check
    models_dir = module_path / "models"
    has_models = False
    if models_dir.exists():
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
            checks.append(
                {
                    "check": "security_csv",
                    "status": "WARNING",
                    "message": "Module has models but missing security/ir.model.access.csv",
                }
            )
        else:
            # Validate CSV format
            try:
                with open(security_csv, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                if rows:
                    checks.append(
                        {
                            "check": "security_csv",
                            "status": "PASS",
                            "message": f"ir.model.access.csv has {len(rows)} rules",
                        }
                    )
                else:
                    checks.append(
                        {
                            "check": "security_csv",
                            "status": "WARNING",
                            "message": "ir.model.access.csv is empty",
                        }
                    )
            except Exception as e:
                checks.append(
                    {
                        "check": "security_csv",
                        "status": "FAIL",
                        "message": f"Invalid CSV: {e}",
                    }
                )

    # 7. Dependency check
    manifest = parse_manifest(module_path / "__manifest__.py")
    if manifest:
        depends = manifest.get("depends", [])
        missing_deps = []
        enterprise_deps = []
        for dep in depends:
            if dep in ENTERPRISE_BLOCKLIST:
                enterprise_deps.append(dep)
            elif dep not in CE_CORE_MODULES and dep not in all_modules:
                # Check if it's another ipai module
                if not dep.startswith("ipai_"):
                    missing_deps.append(dep)

        if enterprise_deps:
            checks.append(
                {
                    "check": "enterprise_deps",
                    "status": "FAIL",
                    "message": f"Enterprise dependencies found: {', '.join(enterprise_deps)}",
                }
            )

        if missing_deps:
            checks.append(
                {
                    "check": "missing_deps",
                    "status": "WARNING",
                    "message": f"Dependencies not in CE core or addons: {', '.join(missing_deps)}",
                }
            )

    return checks


def audit_module(module_name: str, all_modules: Set[str]) -> Optional[ModuleAuditInfo]:
    """Perform a complete audit of a single module."""
    module_path, location = find_module_path(module_name)
    if not module_path:
        return None

    info = ModuleAuditInfo(name=module_name, path=str(module_path), location=location)

    # Parse manifest
    manifest = parse_manifest(module_path / "__manifest__.py")
    if manifest:
        info.display_name = manifest.get("name", module_name)
        info.version = manifest.get("version", "")
        info.category = manifest.get("category", "")
        info.license = manifest.get("license", "")
        info.author = manifest.get("author", "")
        info.summary = manifest.get("summary", "")
        info.description = manifest.get("description", "")
        info.is_application = manifest.get("application", False)
        info.installable = manifest.get("installable", True)
        info.depends = manifest.get("depends", [])
        info.data_files = manifest.get("data", [])
        info.demo_files = manifest.get("demo", [])
        info.assets = manifest.get("assets", {})

    # Extract models
    models_dir = module_path / "models"
    if models_dir.exists():
        for py_file in models_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                models = extract_models_from_file(py_file)
                info.models.extend(models)

    # Extract wizards (transient models)
    wizards_dir = module_path / "wizards"
    if wizards_dir.exists():
        for py_file in wizards_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                models = extract_models_from_file(py_file)
                info.models.extend(models)

    # Extract views, menus, security from XML files
    for xml_file in module_path.rglob("*.xml"):
        views = extract_views_from_xml(xml_file)
        info.views.extend(views)

        menus = extract_menus_from_xml(xml_file)
        info.menus.extend(menus)

        groups = extract_security_groups_from_xml(xml_file)
        info.security_groups.extend(groups)

        rules = extract_record_rules_from_xml(xml_file)
        info.record_rules.extend(rules)

        params = extract_system_params_from_xml(xml_file)
        info.system_params.extend(params)

        crons = extract_cron_jobs_from_xml(xml_file)
        info.cron_jobs.extend(crons)

    # Extract access rules from CSV
    security_csv = module_path / "security" / "ir.model.access.csv"
    if security_csv.exists():
        info.access_rules = extract_security_from_csv(security_csv)

    # Check for README
    readme_path = module_path / "README.md"
    info.has_readme = readme_path.exists()

    # Run static checks
    info.static_checks = run_static_checks(module_path, module_name, all_modules)

    # Calculate docs coverage
    has_sections = 0
    if info.display_name:
        has_sections += 1
    if info.summary or info.description:
        has_sections += 1
    if info.depends:
        has_sections += 1
    if info.has_readme:
        has_sections += 2

    if has_sections >= 4:
        info.docs_coverage = "good"
    elif has_sections >= 2:
        info.docs_coverage = "partial"
    else:
        info.docs_coverage = "minimal"

    return info


def generate_module_readme(info: ModuleAuditInfo) -> str:
    """Generate README.md content for a module."""
    lines = []

    lines.append(f"# {info.display_name}")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    if info.summary:
        lines.append(info.summary)
        lines.append("")

    lines.append(f"- **Technical Name:** `{info.name}`")
    lines.append(f"- **Version:** {info.version}")
    lines.append(f"- **Category:** {info.category}")
    lines.append(f"- **License:** {info.license}")
    if info.author:
        lines.append(f"- **Author:** {info.author}")
    lines.append(f"- **Application:** {'Yes' if info.is_application else 'No'}")
    lines.append(f"- **Installable:** {'Yes' if info.installable else 'No'}")
    lines.append("")

    # Business Use Case
    lines.append("## Business Use Case")
    lines.append("")
    if info.description:
        # Clean up HTML tags if present
        desc = re.sub(r"<[^>]+>", "", info.description)
        desc = desc.strip()
        if desc:
            lines.append(desc[:500] + "..." if len(desc) > 500 else desc)
        else:
            lines.append("*No detailed description provided in manifest.*")
    else:
        lines.append("*No business use case documented.*")
    lines.append("")

    # Functional Scope
    lines.append("## Functional Scope")
    lines.append("")
    if info.models:
        lines.append("### Data Models")
        lines.append("")
        for model in info.models:
            model_name = (
                model.get("_name") or model.get("_inherit") or model.get("class_name")
            )
            model_desc = model.get("_description", "")
            model_type = model.get("model_type", "Model")
            lines.append(f"- **{model_name}** ({model_type})")
            if model_desc:
                lines.append(f"  - {model_desc}")
            if model.get("fields"):
                lines.append(f"  - Fields: {len(model['fields'])} defined")
        lines.append("")

    if info.views:
        lines.append("### Views")
        lines.append("")
        view_summary = {}
        for view in info.views:
            vtype = view.get("type", "other")
            view_summary[vtype] = view_summary.get(vtype, 0) + 1
        for vtype, count in view_summary.items():
            lines.append(f"- {vtype.capitalize()}: {count}")
        lines.append("")

    if info.menus:
        lines.append("### Menus")
        lines.append("")
        for menu in info.menus[:5]:  # Limit to top 5
            lines.append(f"- `{menu['id']}`: {menu.get('name', 'Unnamed')}")
        if len(info.menus) > 5:
            lines.append(f"- ... and {len(info.menus) - 5} more")
        lines.append("")

    # Installation & Dependencies
    lines.append("## Installation & Dependencies")
    lines.append("")
    lines.append("### Dependencies")
    lines.append("")
    if info.depends:
        for dep in info.depends:
            dep_type = (
                "CE Core"
                if dep in CE_CORE_MODULES
                else "IPAI" if dep.startswith("ipai") else "Other"
            )
            lines.append(f"- `{dep}` ({dep_type})")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("### Installation")
    lines.append("")
    lines.append("```bash")
    lines.append(f"# Install module")
    lines.append(f"odoo-bin -d <database> -i {info.name} --stop-after-init")
    lines.append("")
    lines.append(f"# Upgrade module")
    lines.append(f"odoo-bin -d <database> -u {info.name} --stop-after-init")
    lines.append("```")
    lines.append("")

    # Configuration
    lines.append("## Configuration")
    lines.append("")
    if info.system_params:
        lines.append("### System Parameters")
        lines.append("")
        for param in info.system_params:
            lines.append(f"- `{param['key']}`: {param['value']}")
        lines.append("")
    else:
        lines.append("*No specific configuration required.*")
        lines.append("")

    if info.cron_jobs:
        lines.append("### Scheduled Actions")
        lines.append("")
        for cron in info.cron_jobs:
            status = "Active" if cron.get("active", True) else "Inactive"
            lines.append(f"- **{cron['name']}** ({status})")
        lines.append("")

    # Security
    lines.append("## Security")
    lines.append("")
    if info.security_groups:
        lines.append("### Security Groups")
        lines.append("")
        for group in info.security_groups:
            lines.append(f"- `{group['id']}`: {group.get('name', 'Unnamed')}")
        lines.append("")

    if info.access_rules:
        lines.append("### Access Rules")
        lines.append("")
        lines.append(
            f"*{len(info.access_rules)} access rules defined in ir.model.access.csv*"
        )
        lines.append("")

    if info.record_rules:
        lines.append("### Record Rules")
        lines.append("")
        for rule in info.record_rules:
            lines.append(f"- `{rule['id']}`: {rule.get('name', 'Unnamed')}")
        lines.append("")

    if not info.security_groups and not info.access_rules and not info.record_rules:
        lines.append("*No specific security configuration.*")
        lines.append("")

    # Integrations
    lines.append("## Integrations")
    lines.append("")
    # Check for external service hints in depends or code
    integrations = []
    if (
        "ipai_superset_connector" in info.depends
        or info.name == "ipai_superset_connector"
    ):
        integrations.append("Apache Superset (BI/Analytics)")
    if info.name == "ipai_ask_ai":
        integrations.append("OpenAI API / Claude API (AI Assistant)")
    if "mail" in info.depends:
        integrations.append("Odoo Mail (Email notifications)")

    if integrations:
        for integration in integrations:
            lines.append(f"- {integration}")
    else:
        lines.append("*No external integrations.*")
    lines.append("")

    # Upgrade Notes
    lines.append("## Upgrade Notes")
    lines.append("")
    lines.append(f"- Current Version: {info.version}")
    lines.append("- No breaking changes documented")
    lines.append("")

    # Verification Steps
    lines.append("## Verification Steps")
    lines.append("")
    lines.append("```bash")
    lines.append(f"# 1. Verify module is installed")
    lines.append(
        f"psql -d <database> -c \"SELECT name, state FROM ir_module_module WHERE name = '{info.name}'\""
    )
    lines.append("")
    lines.append(f"# 2. Check module info")
    lines.append(
        f'odoo-bin shell -d <database> -c \'print(env["ir.module.module"].search([("name", "=", "{info.name}")]).state)\''
    )
    lines.append("```")
    lines.append("")

    # Data Files
    if info.data_files:
        lines.append("## Data Files")
        lines.append("")
        for df in info.data_files:
            lines.append(f"- `{df}`")
        lines.append("")

    # Static Validation Status
    lines.append("## Static Validation Status")
    lines.append("")
    passed = sum(1 for c in info.static_checks if c["status"] == "PASS")
    warnings = sum(1 for c in info.static_checks if c["status"] == "WARNING")
    failed = sum(1 for c in info.static_checks if c["status"] == "FAIL")
    lines.append(f"- Passed: {passed}")
    lines.append(f"- Warnings: {warnings}")
    lines.append(f"- Failed: {failed}")
    lines.append("")

    return "\n".join(lines)


def generate_modules_index(modules: List[ModuleAuditInfo]) -> str:
    """Generate IPAI_MODULES_INDEX.md content."""
    lines = []

    lines.append("# IPAI Modules Index")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Odoo Version:** {ODOO_VERSION}")
    lines.append(f"**Total Modules:** {len(modules)}")
    lines.append("")

    # Summary by category
    lines.append("## Summary by Category")
    lines.append("")
    categories = {}
    for m in modules:
        cat = m.category or "Uncategorized"
        categories[cat] = categories.get(cat, 0) + 1

    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat in sorted(categories.keys()):
        lines.append(f"| {cat} | {categories[cat]} |")
    lines.append("")

    # Main index table
    lines.append("## Module Index")
    lines.append("")
    lines.append(
        "| Module | Purpose | Dependencies (CE/OCA) | Data Models | Views/Menus | Security/RLS | Config Settings | External Integrations | Seed Data | Known Limits | Docs Coverage | Test Status |"
    )
    lines.append(
        "|--------|---------|----------------------|-------------|-------------|--------------|-----------------|----------------------|-----------|--------------|---------------|-------------|"
    )

    for m in sorted(modules, key=lambda x: x.name):
        # Purpose
        purpose = (
            m.summary[:40] + "..."
            if m.summary and len(m.summary) > 40
            else (m.summary or "-")
        )

        # Dependencies
        ce_deps = [d for d in m.depends if d in CE_CORE_MODULES]
        ipai_deps = [d for d in m.depends if d.startswith("ipai")]
        deps_str = f"CE:{len(ce_deps)}, IPAI:{len(ipai_deps)}"

        # Data models
        models_count = len(m.models)
        models_str = f"{models_count} models" if models_count else "-"

        # Views/Menus
        views_menus = f"{len(m.views)}v/{len(m.menus)}m" if m.views or m.menus else "-"

        # Security
        security_str = []
        if m.security_groups:
            security_str.append(f"{len(m.security_groups)}g")
        if m.access_rules:
            security_str.append(f"{len(m.access_rules)}a")
        if m.record_rules:
            security_str.append(f"{len(m.record_rules)}r")
        security = ", ".join(security_str) if security_str else "-"

        # Config
        config = f"{len(m.system_params)} params" if m.system_params else "-"

        # Integrations
        integrations = "-"
        if "mail" in m.depends:
            integrations = "Mail"
        if m.name == "ipai_superset_connector":
            integrations = "Superset"
        if m.name == "ipai_ask_ai":
            integrations = "AI API"

        # Seed data
        seed = f"{len(m.data_files)} files" if m.data_files else "-"

        # Known limits
        limits = "-"

        # Docs coverage
        docs = m.docs_coverage

        # Test status
        test_status = m.install_status

        lines.append(
            f"| `{m.name}` | {purpose} | {deps_str} | {models_str} | {views_menus} | {security} | {config} | {integrations} | {seed} | {limits} | {docs} | {test_status} |"
        )

    lines.append("")

    # Dependency Graph
    lines.append("## Dependency Graph")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph TD")

    # Create simplified graph
    for m in modules:
        for dep in m.depends:
            if dep.startswith("ipai"):
                lines.append(f"    {m.name} --> {dep}")

    lines.append("```")
    lines.append("")

    # Modules by Application Status
    lines.append("## Application Modules")
    lines.append("")
    apps = [m for m in modules if m.is_application]
    if apps:
        for app in apps:
            lines.append(f"- **{app.display_name}** (`{app.name}`)")
    else:
        lines.append("*No application modules found.*")
    lines.append("")

    # Static Validation Summary
    lines.append("## Static Validation Summary")
    lines.append("")
    lines.append("| Module | Status | Issues |")
    lines.append("|--------|--------|--------|")

    for m in sorted(modules, key=lambda x: x.name):
        failed = [c for c in m.static_checks if c["status"] == "FAIL"]
        warnings = [c for c in m.static_checks if c["status"] == "WARNING"]

        if failed:
            status = "FAIL"
            issues = "; ".join([c["message"][:30] for c in failed[:2]])
        elif warnings:
            status = "WARNING"
            issues = "; ".join([c["message"][:30] for c in warnings[:2]])
        else:
            status = "PASS"
            issues = "-"

        lines.append(f"| `{m.name}` | {status} | {issues} |")

    lines.append("")

    # Per-module documentation links
    lines.append("## Documentation Links")
    lines.append("")
    for m in sorted(modules, key=lambda x: x.name):
        if m.location == "nested":
            doc_path = f"../addons/ipai/{m.name}/README.md"
        else:
            doc_path = f"../addons/{m.name}/README.md"
        lines.append(f"- [{m.display_name}]({doc_path})")
    lines.append("")

    return "\n".join(lines)


def generate_test_matrix(modules: List[ModuleAuditInfo]) -> Tuple[str, Dict]:
    """Generate test matrix CSV and JSON."""
    csv_lines = []
    csv_lines.append(
        "module,install_ok,upgrade_ok,errors,warnings,duration_s,db_name,log_excerpt_path,tested_commit"
    )

    json_data = {
        "generated": datetime.now().isoformat(),
        "odoo_version": ODOO_VERSION,
        "modules": [],
    }

    for m in modules:
        # Determine status from static checks
        has_fail = any(c["status"] == "FAIL" for c in m.static_checks)
        has_warn = any(c["status"] == "WARNING" for c in m.static_checks)

        if has_fail:
            install_ok = "blocked"
            upgrade_ok = "blocked"
            errors = ";".join(
                [c["message"] for c in m.static_checks if c["status"] == "FAIL"]
            )[:100]
        else:
            install_ok = "pending"
            upgrade_ok = "pending"
            errors = ""

        warnings = ";".join(
            [c["message"] for c in m.static_checks if c["status"] == "WARNING"]
        )[:100]

        csv_lines.append(
            f'{m.name},{install_ok},{upgrade_ok},"{errors}","{warnings}",0,test_db,artifacts/logs/{m.name}__install.log,HEAD'
        )

        json_data["modules"].append(
            {
                "name": m.name,
                "display_name": m.display_name,
                "version": m.version,
                "path": m.path,
                "location": m.location,
                "install_status": install_ok,
                "upgrade_status": upgrade_ok,
                "static_checks": m.static_checks,
                "errors": errors,
                "warnings": warnings,
                "models_count": len(m.models),
                "views_count": len(m.views),
                "menus_count": len(m.menus),
                "depends": m.depends,
                "data_files": m.data_files,
            }
        )

    return "\n".join(csv_lines), json_data


def main():
    """Main audit function."""
    print("=" * 70)
    print("IPAI Module Full Auditor")
    print("=" * 70)

    # Ensure directories exist
    MODULES_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Discover all ipai modules for dependency checking
    all_modules = set()
    for item in ADDONS_ROOT.iterdir():
        if item.is_dir() and (item / "__manifest__.py").exists():
            all_modules.add(item.name)
    if IPAI_NESTED.exists():
        for item in IPAI_NESTED.iterdir():
            if item.is_dir() and (item / "__manifest__.py").exists():
                all_modules.add(item.name)

    print(f"\n[1/5] Environment Detection")
    print(f"  Odoo Version: {ODOO_VERSION}")
    print(f"  Addons Root: {ADDONS_ROOT}")
    print(f"  Total modules found: {len(all_modules)}")
    print(f"  Modules in scope: {len(SCOPE_MODULES)}")

    # Audit each module
    print(f"\n[2/5] Auditing Modules")
    audited_modules: List[ModuleAuditInfo] = []

    for module_name in SCOPE_MODULES:
        info = audit_module(module_name, all_modules)
        if info:
            audited_modules.append(info)
            status = (
                "PASS"
                if not any(c["status"] == "FAIL" for c in info.static_checks)
                else "FAIL"
            )
            print(f"  {'✓' if status == 'PASS' else '✗'} {module_name}: {status}")
        else:
            print(f"  ? {module_name}: NOT FOUND")

    # Generate module documentation
    print(f"\n[3/5] Generating Module Documentation")
    for info in audited_modules:
        readme_content = generate_module_readme(info)

        # Write to module directory
        module_path = Path(info.path)
        readme_path = module_path / "README.md"

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        print(f"  ✓ {info.name}/README.md")

    # Generate index
    print(f"\n[4/5] Generating Module Index")
    index_content = generate_modules_index(audited_modules)
    index_path = DOCS_DIR / "IPAI_MODULES_INDEX.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"  ✓ {index_path}")

    # Generate test matrix
    print(f"\n[5/5] Generating Test Matrix")
    csv_content, json_data = generate_test_matrix(audited_modules)

    csv_path = ARTIFACTS_DIR / "ipai_install_upgrade_matrix.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    print(f"  ✓ {csv_path}")

    json_path = ARTIFACTS_DIR / "ipai_install_upgrade_matrix.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    print(f"  ✓ {json_path}")

    # Create placeholder log files
    for info in audited_modules:
        for suffix in ["install", "upgrade"]:
            log_path = LOGS_DIR / f"{info.name}__{suffix}.log"
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"# {info.name} {suffix} log\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Status: pending (static validation only)\n\n")
                for check in info.static_checks:
                    f.write(
                        f"[{check['status']}] {check['check']}: {check['message']}\n"
                    )
    print(f"  ✓ Log placeholders created in {LOGS_DIR}")

    # Summary
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

    passed = sum(
        1
        for m in audited_modules
        if not any(c["status"] == "FAIL" for c in m.static_checks)
    )
    failed = len(audited_modules) - passed

    print(f"\nSummary:")
    print(f"  - Modules audited: {len(audited_modules)}/{len(SCOPE_MODULES)}")
    print(f"  - Static validation passed: {passed}")
    print(f"  - Static validation failed: {failed}")
    print(f"\nDeliverables:")
    print(f"  - docs/IPAI_MODULES_INDEX.md")
    print(f"  - Per-module README.md files")
    print(f"  - artifacts/ipai_install_upgrade_matrix.csv")
    print(f"  - artifacts/ipai_install_upgrade_matrix.json")
    print(f"  - artifacts/logs/*.log")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
