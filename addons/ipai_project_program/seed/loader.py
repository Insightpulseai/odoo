# -*- coding: utf-8 -*-
"""Idempotent JSON seed loader for program and IM project data."""
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


def _ensure_xmlid(env, full_xmlid: str, model: str, res_id: int):
    """Ensure an external id exists and points to (model, res_id)."""
    if "." not in full_xmlid:
        return
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


def load_seed_bundle(env, module_name: str):
    """
    Load all seed data from JSON files.

    This function is idempotent - safe to run multiple times.
    """
    _logger.info("Loading seed bundle for %s", module_name)

    # 1) Task stages
    stages = _read_json(module_name, "data/seed/stages.json").get("task_stages", [])
    for s in stages:
        name = s["name"]
        seq = s.get("sequence", 10)
        rec = env["project.task.type"].sudo().search([("name", "=", name)], limit=1)
        if rec:
            rec.write({"sequence": seq})
        else:
            rec = env["project.task.type"].sudo().create({"name": name, "sequence": seq})
        # Store xmlid if provided
        xml_id = s.get("xml_id")
        if xml_id:
            _ensure_xmlid(env, f"{module_name}.{xml_id}", "project.task.type", rec.id)

    # 2) Directory people
    directory = _read_json(module_name, "data/seed/directory.json").get("people", [])
    for p in directory:
        code = p["code"]
        rec = env["ipai.directory.person"].sudo().search([("code", "=", code)], limit=1)
        vals = {
            "code": code,
            "name": p.get("name"),
            "email": p.get("email"),
            "role": p.get("role"),
        }
        if rec:
            rec.write(vals)
        else:
            env["ipai.directory.person"].sudo().create(vals)

    # 3) Programs (parent projects)
    programs = _read_json(module_name, "data/seed/programs.json").get("programs", [])
    for p in programs:
        program_code = p["program_code"]
        rec = env["project.project"].sudo().search(
            [("program_code", "=", program_code), ("parent_id", "=", False)], limit=1
        )
        vals = {
            "name": p["name"],
            "program_code": program_code,
            "program_type": p.get("program_type", "hybrid"),
            "date_start": p.get("date_start"),
            "date": p.get("date_end"),
            "is_program": True,
        }
        if rec:
            rec.write(vals)
        else:
            rec = env["project.project"].sudo().create(vals)

        xml_id = p.get("xml_id")
        if xml_id:
            _ensure_xmlid(env, f"{module_name}.{xml_id}", "project.project", rec.id)

    # 4) IM projects (child projects)
    ims = _read_json(module_name, "data/seed/im_projects.json").get(
        "implementation_modules", []
    )
    for im in ims:
        parent = env.ref(im["parent_xml_id"], raise_if_not_found=False)
        if not parent:
            _logger.warning("Parent not found for IM: %s", im.get("xml_id"))
            continue
        im_code = im["im_code"]
        child = env["project.project"].sudo().search(
            [("parent_id", "=", parent.id), ("im_code", "=", im_code)], limit=1
        )
        vals = {
            "name": im["name"],
            "parent_id": parent.id,
            "im_code": im_code,
            "program_code": parent.program_code,
            "program_type": parent.program_type,
            "is_program": False,
        }
        if child:
            child.write(vals)
        else:
            child = env["project.project"].sudo().create(vals)

        xml_id = im.get("xml_id")
        if xml_id:
            _ensure_xmlid(env, f"{module_name}.{xml_id}", "project.project", child.id)

    _logger.info("Seed bundle loaded successfully for %s", module_name)
