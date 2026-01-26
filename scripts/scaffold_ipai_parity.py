#!/usr/bin/env python3
"""
Scaffold all missing ipai_* modules for EE parity.
Usage: python scripts/scaffold_ipai_parity.py
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
IPAI_DIR = REPO_ROOT / "addons" / "ipai"
ODOO_VERSION = os.environ.get("ODOO_VERSION", "19.0")

# ipai modules to scaffold: name -> (title, description, depends)
IPAI_MODULES = {
    "ipai_ai_agent_builder": (
        "AI Agent Builder",
        "AI agents with system prompts, topics, tools",
        ["mail"],
    ),
    "ipai_ai_rag": (
        "AI RAG Pipeline",
        "RAG for document-based context retrieval",
        ["ipai_ai_agent_builder"],
    ),
    "ipai_ai_tools": (
        "AI Tool Registry",
        "Audited tool execution for AI agents",
        ["ipai_ai_agent_builder"],
    ),
    "ipai_ai_fields": (
        "AI Fields",
        "AI-powered field population",
        ["ipai_ai_agent_builder"],
    ),
    "ipai_ai_automations": (
        "AI Automations",
        "AI in server actions",
        ["ipai_ai_agent_builder", "base_automation"],
    ),
    "ipai_ai_livechat": (
        "AI Livechat",
        "AI agent for live chat",
        ["ipai_ai_agent_builder", "im_livechat"],
    ),
    "ipai_finance_tax_return": (
        "Tax Return Workflow",
        "Tax return with validation",
        ["account"],
    ),
    "ipai_whatsapp_connector": (
        "WhatsApp Connector",
        "WhatsApp messaging integration",
        ["mail"],
    ),
    "ipai_project_templates": (
        "Project Templates",
        "Project and task templates",
        ["project"],
    ),
    "ipai_planning_attendance": (
        "Planning Attendance",
        "Compare planned vs attended",
        ["hr_attendance"],
    ),
    "ipai_esg": (
        "ESG Carbon Analytics",
        "Carbon footprint tracking",
        ["base"],
    ),
    "ipai_esg_social": (
        "ESG Social Metrics",
        "Gender parity and pay gap",
        ["hr"],
    ),
    "ipai_helpdesk_refund": (
        "Helpdesk Refunds",
        "Gift card reimbursements",
        ["ipai_helpdesk"],
    ),
    "ipai_documents_ai": (
        "Documents AI",
        "AI document classification",
        ["mail"],
    ),
    "ipai_sign": (
        "Electronic Sign",
        "Document envelopes for signing",
        ["mail"],
    ),
    "ipai_equity": (
        "Equity Management",
        "Share and shareholder tracking",
        ["base"],
    ),
}


def scaffold_module(module_name: str, title: str, desc: str, depends: list):
    """Scaffold a single module."""
    module_path = IPAI_DIR / module_name

    if module_path.exists():
        print(f"[SKIP] {module_name} already exists")
        return False

    print(f"[CREATE] {module_name}")

    # Create directories
    (module_path / "models").mkdir(parents=True)
    (module_path / "views").mkdir()
    (module_path / "security").mkdir()
    (module_path / "data").mkdir()
    (module_path / "static" / "description").mkdir(parents=True)

    # Model name from module name
    model_name = module_name.replace("ipai_", "").replace("_", ".")
    class_name = "".join(word.capitalize() for word in module_name.replace("ipai_", "").split("_"))
    file_name = module_name.replace("ipai_", "")

    # __manifest__.py
    depends_str = ", ".join(f'"{d}"' for d in depends)
    manifest = f'''# -*- coding: utf-8 -*-
{{
    "name": "{title}",
    "version": "{ODOO_VERSION}.1.0.0",
    "category": "InsightPulse AI",
    "summary": "{desc}",
    "description": """
{title}
{"=" * len(title)}

{desc}

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

**Features:**
- Core functionality for {title.lower()}
- Integration with Odoo workflows
- Audit logging and compliance

**Configuration:**
- Go to Settings > IPAI > {title}

**Credits:**
- InsightPulse AI Team
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [{depends_str}],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}}
'''
    (module_path / "__manifest__.py").write_text(manifest)

    # __init__.py
    (module_path / "__init__.py").write_text("# -*- coding: utf-8 -*-\nfrom . import models\n")

    # models/__init__.py
    (module_path / "models" / "__init__.py").write_text(f"# -*- coding: utf-8 -*-\nfrom . import {file_name}\n")

    # Main model file
    model_code = f'''# -*- coding: utf-8 -*-
from odoo import api, fields, models


class {class_name}(models.Model):
    _name = "ipai.{model_name}"
    _description = "{title}"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notes = fields.Text(string="Notes")

    # TODO: Add specific fields for {title}
'''
    (module_path / "models" / f"{file_name}.py").write_text(model_code)

    # Security file
    security = f"""id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{file_name}_user,{file_name}.user,model_ipai_{model_name.replace('.', '_')},base.group_user,1,0,0,0
access_{file_name}_manager,{file_name}.manager,model_ipai_{model_name.replace('.', '_')},base.group_system,1,1,1,1
"""
    (module_path / "security" / "ir.model.access.csv").write_text(security)

    # Menu view
    menu_xml = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Menu items will be added here -->
</odoo>
'''
    (module_path / "views" / "menu.xml").write_text(menu_xml)

    # README
    readme = f"""# {title}

## Description

{desc}

This module provides Odoo 19 Enterprise Edition parity for CE deployments.

## Dependencies

{chr(10).join(f"- {d}" for d in depends)}

## Configuration

1. Install the module
2. Go to Settings > IPAI > {title}
3. Configure as needed

## License

LGPL-3
"""
    (module_path / "README.md").write_text(readme)

    return True


def main():
    print("=" * 50)
    print("SCAFFOLDING IPAI MODULES FOR EE PARITY")
    print("=" * 50)

    IPAI_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for name, (title, desc, depends) in sorted(IPAI_MODULES.items()):
        if scaffold_module(name, title, desc, depends):
            created += 1
        else:
            skipped += 1

    print("")
    print("=" * 50)
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Total: {len(IPAI_MODULES)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
