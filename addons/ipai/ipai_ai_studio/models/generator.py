# -*- coding: utf-8 -*-
"""
Deterministic addon scaffold generator.

Converts a spec JSON into a fully-functional Odoo addon file structure.
Includes dependency guardrails to block enterprise-only and missing modules.
"""
import json
from datetime import datetime

# Enterprise-only modules that should be blocked
ENTERPRISE_DENYLIST = {
    # From CE audit - no OCA equivalent / enterprise-only
    "voip",
    "sale_amazon",
    "marketing_card",
    "web_studio",
    # Commonly enterprise-only in many CE setups
    "documents",
    "documents_spreadsheet",
    "sign",
    "planning",
    "helpdesk",
    "quality_control",
    "website_sale_subscription",
    "sale_subscription",
    "mrp_plm",
    "industry_fsm",
    "appointment",
    "knowledge",
    "social",
    "social_sale",
    "marketing_automation",
    "website_helpdesk",
    "website_appointment",
    "studio",
    "web_studio",
}


def _assert_depends_ok(env, depends):
    """
    Validate dependencies against:
    1. Enterprise denylist
    2. Module registry (must exist in ir.module.module)
    """
    # Denylist check
    bad = [d for d in depends if d in ENTERPRISE_DENYLIST]
    if bad:
        raise ValueError(f"Enterprise-only dependencies blocked: {', '.join(bad)}")

    # Exists in module registry?
    missing = []
    for d in depends:
        m = env["ir.module.module"].sudo().search([("name", "=", d)], limit=1)
        if not m:
            missing.append(d)
    if missing:
        raise ValueError(
            f"Missing dependencies (not found in Apps registry): {', '.join(missing)}"
        )


def _py(s: str) -> str:
    """Escape string for Python."""
    return s.replace("\\", "\\\\").replace("'", "\\'")


def render_addon_from_spec(env, spec: dict) -> dict:
    """
    Deterministic scaffold generator.
    Returns dict: { "relative/path": "file content" }

    Args:
        env: Odoo environment for dependency validation
        spec: Module specification dictionary
    """
    module = spec["module_name"]
    app_name = spec.get("app_name", module)
    depends = spec.get("depends", ["base"])
    models = spec.get("models", [])
    menus = spec.get("menus", [])
    views = spec.get("views", {})
    security = spec.get("security", {})

    # Validate dependencies before generating
    _assert_depends_ok(env, depends)

    # --- manifest ---
    manifest = {
        "name": app_name,
        "version": "18.0.1.0.0",
        "depends": depends,
        "data": [
            "security/security.xml",
            "security/ir.model.access.csv",
            "views/menu.xml",
            "views/views.xml",
        ],
        "installable": True,
        "application": True,
        "license": "LGPL-3",
    }

    files = {}
    files["__init__.py"] = "from . import models\n"
    files["__manifest__.py"] = (
        "{"
        + "\n"
        + "\n".join([f"    '{k}': {repr(v)}," for k, v in manifest.items()])
        + "\n}\n"
    )

    # --- models ---
    files["models/__init__.py"] = "from . import models\n"

    # Single file containing all models to keep it simple
    model_py = ["# -*- coding: utf-8 -*-", "from odoo import api, fields, models", ""]
    for m in models:
        model_name = m["name"]
        class_name = "".join(
            [p.capitalize() for p in model_name.replace(".", "_").split("_")]
        )
        mail_thread = bool(m.get("mail_thread"))
        inherits = "models.Model"
        model_py.append(f"class {class_name}({inherits}):")
        model_py.append(f"    _name = '{model_name}'")
        if mail_thread:
            model_py.append("    _inherit = ['mail.thread', 'mail.activity.mixin']")
        model_py.append(f"    _description = '{_py(m.get('description', model_name))}'")
        model_py.append("")
        for f in m.get("fields", []):
            fname = f["name"]
            ftype = f["type"]
            kwargs = []
            if f.get("required"):
                kwargs.append("required=True")
            if f.get("readonly"):
                kwargs.append("readonly=True")
            if f.get("tracking") and mail_thread:
                kwargs.append("tracking=True")
            if ftype == "char":
                line = f"    {fname} = fields.Char({', '.join(kwargs)})"
            elif ftype == "text":
                line = f"    {fname} = fields.Text({', '.join(kwargs)})"
            elif ftype == "integer":
                line = f"    {fname} = fields.Integer({', '.join(kwargs)})"
            elif ftype == "float":
                line = f"    {fname} = fields.Float({', '.join(kwargs)})"
            elif ftype == "boolean":
                line = f"    {fname} = fields.Boolean({', '.join(kwargs)})"
            elif ftype == "date":
                line = f"    {fname} = fields.Date({', '.join(kwargs)})"
            elif ftype == "datetime":
                line = f"    {fname} = fields.Datetime({', '.join(kwargs)})"
            elif ftype == "many2one":
                comodel = f["comodel"]
                line = (
                    f"    {fname} = fields.Many2one('{comodel}', {', '.join(kwargs)})"
                )
            elif ftype == "one2many":
                comodel = f["comodel"]
                inverse = f["inverse"]
                line = f"    {fname} = fields.One2many('{comodel}', '{inverse}', {', '.join(kwargs)})"
            elif ftype == "many2many":
                comodel = f["comodel"]
                line = (
                    f"    {fname} = fields.Many2many('{comodel}', {', '.join(kwargs)})"
                )
            elif ftype == "selection":
                selection = f.get("selection", [])
                line = f"    {fname} = fields.Selection({repr(selection)}, {', '.join(kwargs)})"
            else:
                # fallback as Char to avoid crash
                line = f"    {fname} = fields.Char({', '.join(kwargs)})"
            model_py.append(line)
        model_py.append("")

    files["models/models.py"] = "\n".join(model_py) + "\n"

    # --- security ---
    groups = security.get("groups", [])
    access = security.get("access", [])

    # security.xml (groups)
    sec_lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<odoo>",
    ]
    for g in groups:
        xml_id = g["xml_id"]
        name = g["name"]
        sec_lines += [
            f'  <record id="{xml_id}" model="res.groups">',
            f'    <field name="name">{name}</field>',
            "  </record>",
        ]
    sec_lines.append("</odoo>")
    files["security/security.xml"] = "\n".join(sec_lines) + "\n"

    # ir.model.access.csv
    csv_lines = [
        "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
    ]
    for a in access:
        model_underscore = a["model"].replace(".", "_")
        gid = a.get("group")  # xml id
        perms = (a.get("perm") or "read").split(",")
        perms = set([p.strip() for p in perms if p.strip()])
        row = [
            f"access_{model_underscore}",
            f"access_{model_underscore}",
            f"model_{model_underscore}",
            f"{module}.{gid}" if gid else "",
            "1" if "read" in perms else "0",
            "1" if "write" in perms else "0",
            "1" if "create" in perms else "0",
            "1" if "unlink" in perms else "0",
        ]
        csv_lines.append(",".join(row))
    files["security/ir.model.access.csv"] = "\n".join(csv_lines) + "\n"

    # --- views/menu.xml + views/views.xml ---
    # Choose first model as primary for menu/action defaults
    primary_model = models[0]["name"] if models else None
    action_xml_id = "action_main"
    menu_xml_id = "menu_root"

    menu_lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<odoo>",
    ]
    if primary_model:
        menu_lines += [
            f'  <record id="{action_xml_id}" model="ir.actions.act_window">',
            f'    <field name="name">{app_name}</field>',
            f'    <field name="res_model">{primary_model}</field>',
            '    <field name="view_mode">tree,form</field>',
            "  </record>",
            f'  <menuitem id="{menu_xml_id}" name="{app_name}" action="{action_xml_id}" sequence="10"/>',
        ]
    # extra menus (optional)
    for m in menus:
        name = m.get("name")
        seq = m.get("sequence", 20)
        menu_lines += [
            f'  <menuitem id="menu_{name.lower().replace(" ", "_")}" name="{name}" sequence="{seq}"/>'
        ]
    menu_lines.append("</odoo>")
    files["views/menu.xml"] = "\n".join(menu_lines) + "\n"

    # Basic form/tree/search views for primary model
    view_lines = ['<?xml version="1.0" encoding="utf-8"?>', "<odoo>"]
    if primary_model:
        primary_fields_form = views.get("form", [])
        primary_fields_tree = views.get("tree", [])
        primary_fields_search = views.get("search", [])

        view_lines += [
            '  <record id="view_form_main" model="ir.ui.view">',
            f'    <field name="name">{primary_model}.form</field>',
            f'    <field name="model">{primary_model}</field>',
            '    <field name="arch" type="xml">',
            "      <form>",
            "        <sheet>",
            "          <group>",
        ]
        for f in primary_fields_form:
            view_lines.append(f'            <field name="{f}"/>')
        view_lines += [
            "          </group>",
            "        </sheet>",
            "      </form>",
            "    </field>",
            "  </record>",
            "",
            '  <record id="view_tree_main" model="ir.ui.view">',
            f'    <field name="name">{primary_model}.tree</field>',
            f'    <field name="model">{primary_model}</field>',
            '    <field name="arch" type="xml">',
            "      <tree>",
        ]
        for f in primary_fields_tree:
            view_lines.append(f'        <field name="{f}"/>')
        view_lines += [
            "      </tree>",
            "    </field>",
            "  </record>",
            "",
            '  <record id="view_search_main" model="ir.ui.view">',
            f'    <field name="name">{primary_model}.search</field>',
            f'    <field name="model">{primary_model}</field>',
            '    <field name="arch" type="xml">',
            "      <search>",
        ]
        for f in primary_fields_search:
            view_lines.append(f'        <field name="{f}"/>')
        view_lines += [
            "      </search>",
            "    </field>",
            "  </record>",
        ]
    view_lines.append("</odoo>")
    files["views/views.xml"] = "\n".join(view_lines) + "\n"

    # --- add mail dependency automatically if mail_thread used ---
    any_mail = any(bool(m.get("mail_thread")) for m in models)
    if any_mail and "mail" not in depends:
        # patch manifest in-memory (keep deterministic)
        manifest["depends"] = depends + ["mail"]
        files["__manifest__.py"] = (
            "{"
            + "\n"
            + "\n".join([f"    '{k}': {repr(v)}," for k, v in manifest.items()])
            + "\n}\n"
        )

    # Stamp spec for traceability
    files[".ipai_spec.json"] = (
        json.dumps(
            {"generated_at": datetime.utcnow().isoformat() + "Z", "spec": spec},
            indent=2,
        )
        + "\n"
    )

    return files
