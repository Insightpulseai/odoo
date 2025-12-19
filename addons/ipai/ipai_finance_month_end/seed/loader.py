# -*- coding: utf-8 -*-
"""Idempotent JSON seed loader for month-end templates."""
import json
import logging
from odoo.modules.module import get_module_resource
from odoo.tools import file_open

_logger = logging.getLogger(__name__)


def _read_json(module_name: str, rel_path: str) -> dict:
    """Read JSON file from module data directory."""
    abs_path = get_module_resource(module_name, rel_path)
    if not abs_path:
        _logger.warning("Seed file not found: %s/%s", module_name, rel_path)
        return {}
    try:
        with file_open(abs_path, "r") as f:
            return json.load(f)
    except Exception as e:
        _logger.error("Error reading seed file %s: %s", rel_path, e)
        return {}


def load_seed_bundle(env, module_name: str):
    """
    Load month-end templates from JSON seed file.

    This function is idempotent - safe to run multiple times.
    """
    _logger.info("Loading month-end templates for %s", module_name)

    payload = _read_json(module_name, "data/seed/month_end_templates.json")
    templates = payload.get("templates", [])

    Template = env["ipai.month.end.template"].sudo()
    Step = env["ipai.month.end.template.step"].sudo()

    for t in templates:
        base = t["task_base_name"]
        rec = Template.search([("task_base_name", "=", base)], limit=1)
        vals = {
            "category": t.get("category"),
            "task_base_name": base,
            "default_im_xml_id": t.get("default_im_xml_id"),
        }
        if rec:
            rec.write(vals)
        else:
            rec = Template.create(vals)

        # Replace steps (simple deterministic idempotency)
        Step.search([("template_id", "=", rec.id)]).unlink()
        for idx, s in enumerate(t.get("steps", []), start=1):
            Step.create({
                "template_id": rec.id,
                "sequence": idx * 10,
                "activity_type": s["activity_type"],
                "role_code": s.get("role_code"),
                "offset_days": s.get("offset_days", 0),
                "business_days_before": s.get("business_days_before", 0),
            })

    _logger.info("Loaded %d month-end templates", len(templates))
