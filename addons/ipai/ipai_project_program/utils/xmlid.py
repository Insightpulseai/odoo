# -*- coding: utf-8 -*-
"""External ID (XMLID) utilities."""
from odoo.exceptions import ValidationError


def ensure_xmlid(env, full_xmlid: str, model: str, res_id: int):
    """
    Ensure an external id exists and points to (model, res_id).

    Args:
        env: Odoo environment
        full_xmlid: Full XML ID in form 'module.name'
        model: Model name (e.g., 'project.project')
        res_id: Record ID to link

    Raises:
        ValidationError: If xmlid format is invalid
    """
    if "." not in full_xmlid:
        raise ValidationError("XMLID must be in form 'module.name'")
    module, name = full_xmlid.split(".", 1)
    imd = env["ir.model.data"].sudo()
    existing = imd.search([("module", "=", module), ("name", "=", name)], limit=1)
    vals = {
        "module": module,
        "name": name,
        "model": model,
        "res_id": res_id,
        "noupdate": True,
    }
    if existing:
        existing.write(vals)
    else:
        imd.create(vals)
