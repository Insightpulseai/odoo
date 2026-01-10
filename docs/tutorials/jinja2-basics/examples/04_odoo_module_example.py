#!/usr/bin/env python3
"""
Practical example: Generate Odoo module files.

Demonstrates how the ipai_module_gen tool uses Jinja2 to scaffold
Odoo modules from capability specifications.
"""
from jinja2 import Environment, BaseLoader

# Manifest template (simplified from ipai_module_gen)
MANIFEST_TEMPLATE = """\
# -*- coding: utf-8 -*-
{
    "name": "{{ summary }}",
    "version": "{{ odoo_series }}.1.0.0",
    "category": "IPAI",
    "summary": "{{ summary }}",
    "author": "IPAI",
    "license": "LGPL-3",
    "depends": [
        {% for dep in depends -%}
        "{{ dep }}",
        {% endfor -%}
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
    ],
    "installable": True,
    "application": False,
}
"""

# Model template (simplified)
MODEL_TEMPLATE = """\
# -*- coding: utf-8 -*-
\"\"\"{{ model.description | default(model.name) }}\"\"\"
from odoo import api, fields, models


class {{ class_name }}(models.Model):
    _name = "{{ model.name }}"
    _description = "{{ model.description | default(model.name) }}"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True)
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("done", "Done"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
"""


def to_class_name(model_name: str) -> str:
    """Convert ipai.finance.close_cycle to CloseCycle"""
    # Get last part: close_cycle
    last_part = model_name.split(".")[-1]
    # Convert to TitleCase: CloseCycle
    return "".join(word.title() for word in last_part.split("_"))


# Create environment
env = Environment(
    loader=BaseLoader(),
    trim_blocks=True,
    lstrip_blocks=True
)

# Sample capability data (like capability_map.yaml)
capability = {
    "sap_id": "FI-CLOSE-AFC",
    "slug": "fi-close-afc",
    "title": "Advanced Financial Closing",
    "odoo": {
        "module": "ipai_finance_close_manager",
        "summary": "Advanced Financial Closing - close calendar, tasks, lock, audit",
        "depends": ["account", "mail", "project"],
        "models": [
            {
                "name": "ipai.finance.close_cycle",
                "description": "Close cycle (month-end) header"
            },
            {
                "name": "ipai.finance.close_task",
                "description": "Close tasks linked to cycle"
            }
        ]
    }
}

# Generate manifest
print("=== Generated __manifest__.py ===")
manifest_tpl = env.from_string(MANIFEST_TEMPLATE)
manifest = manifest_tpl.render(
    summary=capability["odoo"]["summary"],
    odoo_series="18.0",
    depends=capability["odoo"]["depends"]
)
print(manifest)
print()

# Generate model files
model_tpl = env.from_string(MODEL_TEMPLATE)
for model in capability["odoo"]["models"]:
    print(f"=== Generated models/{model['name'].split('.')[-1]}.py ===")
    model_code = model_tpl.render(
        model=model,
        class_name=to_class_name(model["name"])
    )
    print(model_code)
    print()
