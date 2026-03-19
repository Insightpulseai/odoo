#!/usr/bin/env python3
"""
Generate comprehensive technical documentation for IPAI Odoo modules.

Rules:
- Do NOT guess. Only document what can be proven from source code.
- Extract and cite file paths, XML IDs, model names, fields, constraints.
- Flag Odoo 18 compatibility issues (deprecated constructs).
- Output must be deterministic and repeatable.
"""

import os
import ast
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any
import json

# Target modules (21 total as specified)
TARGET_MODULES = [
    # WorkOS (9 modules)
    "ipai_workos_affine",
    "ipai_workos_core",
    "ipai_workos_blocks",
    "ipai_workos_canvas",
    "ipai_workos_collab",
    "ipai_workos_db",
    "ipai_workos_search",
    "ipai_workos_templates",
    "ipai_workos_views",
    # Platform (5 modules)
    "ipai_platform_approvals",
    "ipai_platform_audit",
    "ipai_platform_permissions",
    "ipai_platform_theme",
    "ipai_platform_workflow",
    # Finance (6 modules)
    "ipai_bir_tax_compliance",
    "ipai_close_orchestration",
    "ipai_finance_ppm_golive",
    "ipai_month_end",
    "ipai_ppm_a1",
    "ipai_tbwa_finance",
    # CRM (1 module)
    "ipai_crm_pipeline",
]

ADDONS_PATH = Path("addons/ipai")


def parse_manifest(module_path: Path) -> Dict[str, Any]:
    """Parse __manifest__.py and extract metadata."""
    manifest_file = module_path / "__manifest__.py"
    if not manifest_file.exists():
        return {}

    with open(manifest_file, "r") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__manifest__":
                        return ast.literal_eval(node.value)
    except:
        return {}

    return {}


def extract_models(module_path: Path) -> List[Dict[str, Any]]:
    """Extract Python models from models/ directory."""
    models = []
    models_dir = module_path / "models"

    if not models_dir.exists():
        return models

    for model_file in models_dir.glob("*.py"):
        if model_file.name == "__init__.py":
            continue

        with open(model_file, "r") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's an Odoo model
                    for base in node.bases:
                        if isinstance(base, ast.Attribute):
                            if base.attr == "Model":
                                model_info = extract_model_details(
                                    node, model_file, content
                                )
                                if model_info:
                                    models.append(model_info)
        except:
            pass

    return models


def extract_model_details(class_node, file_path, content) -> Dict[str, Any]:
    """Extract detailed model information from AST node."""
    model_name = None
    description = None
    fields = []

    for item in class_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    # Extract _name
                    if target.id == "_name" and isinstance(item.value, ast.Constant):
                        model_name = item.value.value

                    # Extract _description
                    if target.id == "_description" and isinstance(
                        item.value, ast.Constant
                    ):
                        description = item.value.value

                    # Extract fields (simplified detection)
                    if hasattr(item.value, "func"):
                        if hasattr(item.value.func, "attr"):
                            if item.value.func.attr in [
                                "Many2one",
                                "One2many",
                                "Many2many",
                                "Char",
                                "Text",
                                "Integer",
                                "Float",
                                "Boolean",
                                "Date",
                                "Datetime",
                                "Selection",
                            ]:
                                field_name = target.id
                                field_type = item.value.func.attr
                                fields.append(
                                    {
                                        "name": field_name,
                                        "type": field_type,
                                        "file": str(file_path),
                                    }
                                )

    if model_name:
        return {
            "name": model_name,
            "description": description or "",
            "file": str(file_path),
            "class_name": class_node.name,
            "fields": fields,
        }

    return None


def extract_security_groups(module_path: Path) -> List[Dict[str, Any]]:
    """Extract security groups from security XML files."""
    groups = []
    security_dir = module_path / "security"

    if not security_dir.exists():
        return groups

    for xml_file in security_dir.glob("*_security.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for record in root.findall('.//record[@model="res.groups"]'):
                group_id = record.get("id", "")
                name = record.find('.//field[@name="name"]')
                category = record.find('.//field[@name="category_id"]')

                groups.append(
                    {
                        "xml_id": group_id,
                        "name": name.text if name is not None else "",
                        "category": (
                            category.get("ref", "") if category is not None else ""
                        ),
                        "file": str(xml_file),
                    }
                )
        except:
            pass

    return groups


def extract_access_rules(module_path: Path) -> List[Dict[str, Any]]:
    """Extract access rules from ir.model.access.csv."""
    rules = []
    access_file = module_path / "security" / "ir.model.access.csv"

    if not access_file.exists():
        return rules

    with open(access_file, "r") as f:
        lines = f.readlines()

    if len(lines) > 1:  # Skip header
        for line in lines[1:]:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 8:
                rules.append(
                    {
                        "id": parts[0],
                        "name": parts[1],
                        "model_id": parts[2],
                        "group_id": parts[3],
                        "perm_read": parts[4] == "1",
                        "perm_write": parts[5] == "1",
                        "perm_create": parts[6] == "1",
                        "perm_unlink": parts[7] == "1",
                    }
                )

    return rules


def extract_record_rules(module_path: Path) -> List[Dict[str, Any]]:
    """Extract record rules from security XML files."""
    rules = []
    security_dir = module_path / "security"

    if not security_dir.exists():
        return rules

    for xml_file in security_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for record in root.findall('.//record[@model="ir.rule"]'):
                rule_id = record.get("id", "")
                name = record.find('.//field[@name="name"]')
                model = record.find('.//field[@name="model_id"]')
                domain = record.find('.//field[@name="domain_force"]')
                groups = record.find('.//field[@name="groups"]')

                rules.append(
                    {
                        "xml_id": rule_id,
                        "name": name.text if name is not None else "",
                        "model_ref": model.get("ref", "") if model is not None else "",
                        "domain": domain.text if domain is not None else "",
                        "groups": groups.get("eval", "") if groups is not None else "",
                        "file": str(xml_file),
                    }
                )
        except:
            pass

    return rules


def extract_menus(module_path: Path) -> List[Dict[str, Any]]:
    """Extract menu definitions from views XML files."""
    menus = []
    views_dir = module_path / "views"

    if not views_dir.exists():
        return menus

    for xml_file in views_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for menuitem in root.findall(".//menuitem"):
                menu_id = menuitem.get("id", "")
                name = menuitem.get("name", "")
                parent = menuitem.get("parent", "")
                action = menuitem.get("action", "")
                sequence = menuitem.get("sequence", "")

                menus.append(
                    {
                        "xml_id": menu_id,
                        "name": name,
                        "parent": parent,
                        "action": action,
                        "sequence": sequence,
                        "file": str(xml_file),
                    }
                )
        except:
            pass

    return menus


def extract_views(module_path: Path) -> List[Dict[str, Any]]:
    """Extract view definitions from views XML files."""
    views = []
    views_dir = module_path / "views"

    if not views_dir.exists():
        return views

    for xml_file in views_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for record in root.findall('.//record[@model="ir.ui.view"]'):
                view_id = record.get("id", "")
                name = record.find('.//field[@name="name"]')
                model = record.find('.//field[@name="model"]')
                arch = record.find('.//field[@name="arch"]')

                # Check for deprecated type="xml" attribute (Odoo 18 issue)
                deprecated_type_xml = (
                    arch.get("type") == "xml" if arch is not None else False
                )

                # Detect view type from arch content
                view_type = ""
                if arch is not None:
                    for child in arch:
                        if child.tag in [
                            "tree",
                            "form",
                            "kanban",
                            "search",
                            "graph",
                            "pivot",
                            "calendar",
                        ]:
                            view_type = child.tag
                            break

                views.append(
                    {
                        "xml_id": view_id,
                        "name": name.text if name is not None else "",
                        "model": model.text if model is not None else "",
                        "type": view_type,
                        "file": str(xml_file),
                        "deprecated_type_xml": deprecated_type_xml,
                    }
                )
        except:
            pass

    return views


def extract_actions(module_path: Path) -> List[Dict[str, Any]]:
    """Extract action definitions from views XML files."""
    actions = []
    views_dir = module_path / "views"

    if not views_dir.exists():
        return actions

    for xml_file in views_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for record in root.findall('.//record[@model="ir.actions.act_window"]'):
                action_id = record.get("id", "")
                name = record.find('.//field[@name="name"]')
                res_model = record.find('.//field[@name="res_model"]')
                view_mode = record.find('.//field[@name="view_mode"]')

                actions.append(
                    {
                        "xml_id": action_id,
                        "name": name.text if name is not None else "",
                        "res_model": res_model.text if res_model is not None else "",
                        "view_mode": view_mode.text if view_mode is not None else "",
                        "file": str(xml_file),
                    }
                )
        except:
            pass

    return actions


def extract_cron_jobs(module_path: Path) -> List[Dict[str, Any]]:
    """Extract cron jobs from data XML files."""
    crons = []
    data_dir = module_path / "data"

    if not data_dir.exists():
        return crons

    for xml_file in data_dir.glob("*.xml"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for record in root.findall('.//record[@model="ir.cron"]'):
                cron_id = record.get("id", "")
                name = record.find('.//field[@name="name"]')
                model = record.find('.//field[@name="model_id"]')
                function = record.find('.//field[@name="code"]')
                interval_number = record.find('.//field[@name="interval_number"]')
                interval_type = record.find('.//field[@name="interval_type"]')
                numbercall = record.find(
                    './/field[@name="numbercall"]'
                )  # Deprecated in Odoo 18

                crons.append(
                    {
                        "xml_id": cron_id,
                        "name": name.text if name is not None else "",
                        "model_ref": model.get("ref", "") if model is not None else "",
                        "function": function.text if function is not None else "",
                        "interval": f"{interval_number.text if interval_number is not None else ''} {interval_type.text if interval_type is not None else ''}",
                        "file": str(xml_file),
                        "deprecated_numbercall": numbercall
                        is not None,  # Flag Odoo 18 issue
                    }
                )
        except:
            pass

    return crons


def extract_controllers(module_path: Path) -> List[Dict[str, Any]]:
    """Extract HTTP controllers from controllers/ directory."""
    controllers = []
    controllers_dir = module_path / "controllers"

    if not controllers_dir.exists():
        return controllers

    for py_file in controllers_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        with open(py_file, "r") as f:
            content = f.read()

        # Extract route decorators
        route_pattern = r'@http\.route\([\'"]([^\'"]+)[\'"]'
        routes = re.findall(route_pattern, content)

        if routes:
            controllers.append({"file": str(py_file), "routes": routes})

    return controllers


def generate_module_doc(module_name: str) -> str:
    """Generate comprehensive documentation for a single module."""
    module_path = ADDONS_PATH / module_name

    if not module_path.exists():
        return f"# {module_name}\n\n**ERROR**: Module directory not found at `{module_path}`\n"

    # Extract all metadata
    manifest = parse_manifest(module_path)
    models = extract_models(module_path)
    security_groups = extract_security_groups(module_path)
    access_rules = extract_access_rules(module_path)
    record_rules = extract_record_rules(module_path)
    menus = extract_menus(module_path)
    views = extract_views(module_path)
    actions = extract_actions(module_path)
    cron_jobs = extract_cron_jobs(module_path)
    controllers = extract_controllers(module_path)

    # Check for Odoo 18 compatibility issues
    odoo18_issues = []

    # Check for deprecated numbercall in cron jobs
    for cron in cron_jobs:
        if cron.get("deprecated_numbercall"):
            odoo18_issues.append(
                f"⚠️ Deprecated `numbercall` field in cron job: `{cron['xml_id']}` ({cron['file']})"
            )

    # Check for deprecated type="xml" in views
    for view in views:
        if view.get("deprecated_type_xml"):
            odoo18_issues.append(
                f"⚠️ Deprecated `type=\"xml\"` attribute in view: `{view['xml_id']}` ({view['file']})"
            )

    # Build documentation
    doc = f"""# {module_name}

**Module**: `{module_name}`
**Version**: `{manifest.get('version', 'unknown')}`
**Category**: `{manifest.get('category', 'uncategorized')}`
**License**: `{manifest.get('license', 'LGPL-3')}`
**Author**: `{manifest.get('author', 'Unknown')}`
**Website**: `{manifest.get('website', '')}`

---

## Overview

**Summary**: {manifest.get('summary', 'No summary provided')}

**Description**: {manifest.get('description', 'No description provided')}

**Installable**: {'✅ Yes' if manifest.get('installable', False) else '❌ No'}
**Application**: {'✅ Yes (standalone app)' if manifest.get('application', False) else '❌ No (library/integration module)'}
**Auto-Install**: {'✅ Yes (auto-installed with dependencies)' if manifest.get('auto_install', False) else '❌ No (manual install required)'}

---

## Dependencies

**Odoo Core Modules**:
"""

    # Dependencies
    core_deps = [
        dep for dep in manifest.get("depends", []) if not dep.startswith("ipai_")
    ]
    ipai_deps = [dep for dep in manifest.get("depends", []) if dep.startswith("ipai_")]

    if core_deps:
        for dep in core_deps:
            doc += f"- `{dep}`\n"
    else:
        doc += "- None (base module only)\n"

    doc += "\n**IPAI Module Dependencies**:\n"
    if ipai_deps:
        for dep in ipai_deps:
            doc += f"- `{dep}`\n"
    else:
        doc += "- None (no IPAI dependencies)\n"

    # Data Model
    doc += "\n---\n\n## Data Model\n\n"

    if models:
        doc += f"**Total Models**: {len(models)}\n\n"
        for model in models:
            doc += f"### Model: `{model['name']}`\n\n"
            doc += f"**Description**: {model['description']}\n\n"
            doc += f"**Python Class**: `{model['class_name']}`  \n"
            doc += f"**File**: `{model['file']}`\n\n"

            if model["fields"]:
                doc += "**Fields**:\n\n"
                doc += "| Field Name | Type | File |\n"
                doc += "|------------|------|------|\n"
                for field in model["fields"]:
                    doc += f"| `{field['name']}` | {field['type']} | {Path(field['file']).name} |\n"
                doc += "\n"
            else:
                doc += (
                    "**Fields**: No fields extracted (check source code manually)\n\n"
                )
    else:
        doc += "**No Python models found** (This module may only provide views, data, or configuration)\n\n"

    # Security
    doc += "---\n\n## Security\n\n"

    if security_groups:
        doc += f"**Security Groups**: {len(security_groups)}\n\n"
        for group in security_groups:
            doc += f"### Group: `{group['xml_id']}`\n\n"
            doc += f"**Name**: {group['name']}  \n"
            doc += f"**Category**: `{group['category']}`  \n"
            doc += f"**File**: `{group['file']}`\n\n"
    else:
        doc += "**No security groups defined**\n\n"

    if access_rules:
        doc += f"**Access Rules (ir.model.access.csv)**: {len(access_rules)}\n\n"
        doc += "| Access ID | Model | Group | Read | Write | Create | Delete |\n"
        doc += "|-----------|-------|-------|------|-------|--------|--------|\n"
        for rule in access_rules:
            doc += f"| `{rule['id']}` | `{rule['model_id']}` | `{rule['group_id']}` | {'✅' if rule['perm_read'] else '❌'} | {'✅' if rule['perm_write'] else '❌'} | {'✅' if rule['perm_create'] else '❌'} | {'✅' if rule['perm_unlink'] else '❌'} |\n"
        doc += "\n"
    else:
        doc += "**No access rules (ir.model.access.csv) found**\n\n"

    if record_rules:
        doc += f"**Record Rules (ir.rule)**: {len(record_rules)}\n\n"
        for rule in record_rules:
            doc += f"### Rule: `{rule['xml_id']}`\n\n"
            doc += f"**Name**: {rule['name']}  \n"
            doc += f"**Model**: `{rule['model_ref']}`  \n"
            doc += f"**Domain**: `{rule['domain']}`  \n"
            doc += f"**Groups**: `{rule['groups']}`  \n"
            doc += f"**File**: `{rule['file']}`\n\n"
    else:
        doc += "**No record rules (ir.rule) found**\n\n"

    # UI
    doc += "---\n\n## UI (Menus, Actions, Views)\n\n"

    if menus:
        doc += f"**Menus**: {len(menus)}\n\n"
        doc += "| Menu ID | Name | Parent | Action | Sequence | File |\n"
        doc += "|---------|------|--------|--------|----------|------|\n"
        for menu in menus:
            doc += f"| `{menu['xml_id']}` | {menu['name']} | `{menu['parent']}` | `{menu['action']}` | {menu['sequence']} | {Path(menu['file']).name} |\n"
        doc += "\n"
    else:
        doc += "**No menus found**\n\n"

    if actions:
        doc += f"**Actions**: {len(actions)}\n\n"
        doc += "| Action ID | Name | Model | View Mode | File |\n"
        doc += "|-----------|------|-------|-----------|------|\n"
        for action in actions:
            doc += f"| `{action['xml_id']}` | {action['name']} | `{action['res_model']}` | {action['view_mode']} | {Path(action['file']).name} |\n"
        doc += "\n"
    else:
        doc += "**No actions found**\n\n"

    if views:
        doc += f"**Views**: {len(views)}\n\n"
        doc += "| View ID | Name | Model | Type | File |\n"
        doc += "|---------|------|-------|------|------|\n"
        for view in views:
            deprecated_marker = (
                " ⚠️ (deprecated type='xml')" if view.get("deprecated_type_xml") else ""
            )
            doc += f"| `{view['xml_id']}` | {view['name']} | `{view['model']}` | {view['type']}{deprecated_marker} | {Path(view['file']).name} |\n"
        doc += "\n"
    else:
        doc += "**No views found**\n\n"

    # Automation
    doc += "---\n\n## Automation\n\n"

    if cron_jobs:
        doc += f"**Scheduled Actions (ir.cron)**: {len(cron_jobs)}\n\n"
        for cron in cron_jobs:
            doc += f"### Cron: `{cron['xml_id']}`\n\n"
            doc += f"**Name**: {cron['name']}  \n"
            doc += f"**Model**: `{cron['model_ref']}`  \n"
            doc += f"**Function**: `{cron['function']}`  \n"
            doc += f"**Interval**: {cron['interval']}  \n"
            doc += f"**File**: `{cron['file']}`\n\n"
            if cron.get("deprecated_numbercall"):
                doc += "⚠️ **Odoo 18 Issue**: This cron job uses deprecated `numbercall` field. Remove before installation.\n\n"
    else:
        doc += "**No scheduled actions found**\n\n"

    # Integrations
    doc += "---\n\n## Integrations\n\n"

    if controllers:
        doc += f"**HTTP Controllers**: {len(controllers)}\n\n"
        for ctrl in controllers:
            doc += f"### Controller: `{Path(ctrl['file']).name}`\n\n"
            doc += "**Routes**:\n"
            for route in ctrl["routes"]:
                doc += f"- `{route}`\n"
            doc += f"\n**File**: `{ctrl['file']}`\n\n"
    else:
        doc += "**No HTTP controllers found**\n\n"

    # Configuration
    doc += "---\n\n## Configuration\n\n"

    data_files = manifest.get("data", [])
    demo_files = manifest.get("demo", [])

    if data_files:
        doc += "**Data Files**:\n"
        for data_file in data_files:
            doc += f"- `{data_file}`\n"
        doc += "\n"

    if demo_files:
        doc += "**Demo Data Files**:\n"
        for demo_file in demo_files:
            doc += f"- `{demo_file}`\n"
        doc += "\n"

    if not data_files and not demo_files:
        doc += "**No data or demo files declared**\n\n"

    # Operational
    doc += "---\n\n## Operational\n\n"

    doc += "### Installation\n\n"
    doc += "```bash\n"
    doc += f"# Install module\n"
    doc += f"odoo -d <database> -i {module_name} --stop-after-init\n"
    doc += "```\n\n"

    doc += "### Upgrade\n\n"
    doc += "```bash\n"
    doc += f"# Upgrade module\n"
    doc += f"odoo -d <database> -u {module_name} --stop-after-init\n"
    doc += "```\n\n"

    if odoo18_issues:
        doc += "### ⚠️ Odoo 18 Compatibility Issues\n\n"
        doc += "**CRITICAL**: The following issues must be fixed before installation on Odoo 18:\n\n"
        for issue in odoo18_issues:
            doc += f"{issue}\n\n"
        doc += "**Fix Procedure**:\n"
        doc += "1. Edit the affected files\n"
        doc += "2. Remove deprecated fields/attributes\n"
        doc += "3. Test installation in staging environment\n"
        doc += "4. Commit fixes with descriptive message\n\n"

    # Verification
    doc += "---\n\n## Verification\n\n"

    doc += "### Module Installation Check\n\n"
    doc += "```sql\n"
    doc += f"-- Verify module installed\n"
    doc += f"SELECT name, state, latest_version\n"
    doc += f"FROM ir_module_module\n"
    doc += f"WHERE name = '{module_name}';\n"
    doc += f"-- Expected: state='installed', latest_version='{manifest.get('version', 'unknown')}'\n"
    doc += "```\n\n"

    if models:
        doc += "### Data Model Verification\n\n"
        doc += "```sql\n"
        doc += "-- Verify tables created\n"
        for model in models:
            table_name = model["name"].replace(".", "_")
            doc += f"SELECT COUNT(*) FROM {table_name};  -- {model['name']}\n"
        doc += "```\n\n"

    if menus:
        doc += "### Menu Verification\n\n"
        doc += "```sql\n"
        doc += "-- Verify menus created\n"
        doc += f"SELECT id, name FROM ir_ui_menu\n"
        doc += f"WHERE id IN (\n"
        for i, menu in enumerate(menus):
            doc += f"  (SELECT id FROM ir_model_data WHERE module='{module_name}' AND name='{menu['xml_id']}')"
            if i < len(menus) - 1:
                doc += ",\n"
        doc += "\n);\n"
        doc += "```\n\n"

    if cron_jobs:
        doc += "### Scheduled Actions Verification\n\n"
        doc += "```sql\n"
        doc += "-- Verify cron jobs active\n"
        doc += f"SELECT id, name, active, nextcall\n"
        doc += f"FROM ir_cron\n"
        doc += f"WHERE id IN (\n"
        for i, cron in enumerate(cron_jobs):
            doc += f"  (SELECT id FROM ir_model_data WHERE module='{module_name}' AND name='{cron['xml_id']}')"
            if i < len(cron_jobs) - 1:
                doc += ",\n"
        doc += "\n);\n"
        doc += f"-- Expected: active=true for all jobs\n"
        doc += "```\n\n"

    doc += "---\n\n"
    doc += f"**Documentation Generated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
    doc += f"**Source**: Extracted from `{module_path}` via automated analysis  \n"
    doc += "**Note**: This documentation is generated from source code analysis. Manual verification recommended.\n"

    return doc


def main():
    """Generate documentation for all target modules."""
    print("Generating per-module documentation for 21 IPAI modules...")
    print(f"Output directory: docs/modules/\n")

    output_dir = Path("docs/modules")
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_count = 0
    failed_modules = []

    for module_name in TARGET_MODULES:
        print(f"Generating: {module_name}...")
        try:
            doc_content = generate_module_doc(module_name)

            output_file = output_dir / f"{module_name}.md"
            with open(output_file, "w") as f:
                f.write(doc_content)

            generated_count += 1
            print(f"  ✅ Generated: {output_file}")
        except Exception as e:
            failed_modules.append((module_name, str(e)))
            print(f"  ❌ Failed: {e}")

    print(f"\nGeneration complete:")
    print(f"  ✅ Success: {generated_count}/{len(TARGET_MODULES)}")
    if failed_modules:
        print(f"  ❌ Failed: {len(failed_modules)}")
        for module, error in failed_modules:
            print(f"    - {module}: {error}")

    # Save summary
    summary = {
        "total_modules": len(TARGET_MODULES),
        "generated": generated_count,
        "failed": len(failed_modules),
        "failed_modules": failed_modules,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }

    with open(output_dir / "generation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved to: docs/modules/generation_summary.json")


if __name__ == "__main__":
    main()
