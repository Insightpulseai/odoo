# -*- coding: utf-8 -*-
"""Idempotent JSON seed loader for BIR schedule data."""
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
    Load BIR schedule items from JSON seed file.

    This function is idempotent - safe to run multiple times.
    """
    _logger.info("Loading BIR schedule items for %s", module_name)

    payload = _read_json(module_name, "data/seed/bir_schedule_2026.json")
    items = payload.get("items", [])

    Item = env["ipai.bir.schedule.item"].sudo()
    Step = env["ipai.bir.schedule.step"].sudo()

    for it in items:
        # Idempotency key: (bir_form, period_covered, deadline)
        key = (it.get("bir_form"), it.get("period_covered"), it.get("deadline"))
        rec = Item.search([
            ("bir_form", "=", key[0]),
            ("period_covered", "=", key[1]),
            ("deadline", "=", key[2]),
        ], limit=1)

        vals = {
            "bir_form": it.get("bir_form"),
            "period_covered": it.get("period_covered"),
            "deadline": it.get("deadline"),
            "im_xml_id": it.get("im_xml_id"),
        }

        if rec:
            rec.write(vals)
        else:
            rec = Item.create(vals)

        # Replace steps (simple deterministic idempotency)
        Step.search([("item_id", "=", rec.id)]).unlink()
        for idx, s in enumerate(it.get("steps", []), start=1):
            Step.create({
                "item_id": rec.id,
                "sequence": idx * 10,
                "activity_type": s.get("activity_type"),
                "role_code": s.get("role_code"),
                "business_days_before": s.get("business_days_before", 0),
                "on_or_before_deadline": bool(s.get("on_or_before_deadline", False)),
            })

    _logger.info("Loaded %d BIR schedule items", len(items))
