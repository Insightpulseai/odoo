import json

from odoo import fields, models
from odoo.exceptions import UserError


class IpaiImportSeedWizard(models.TransientModel):
    _name = "ipai.import.seed.wizard"
    _description = "Import Seed Data (JSON)"

    seed_json = fields.Text(required=True, help="Paste exported JSON payload here.")
    mode = fields.Selection(
        [("upsert", "Upsert (idempotent)"), ("replace", "Replace all")],
        default="upsert",
        required=True,
    )

    def action_import(self):
        """Import seed data from JSON payload."""
        self.ensure_one()
        try:
            payload = json.loads(self.seed_json)
        except Exception as e:
            raise UserError(f"Invalid JSON: {e}") from e

        env = self.env

        if self.mode == "replace":
            env["ipai.localization.overlay"].sudo().search([]).unlink()
            env["ipai.stc.scenario"].sudo().search([]).unlink()
            env["ipai.stc.check"].sudo().search([]).unlink()
            env["ipai.stc.worklist_type"].sudo().search([]).unlink()
            env["ipai.ppm.task.checklist"].sudo().search([]).unlink()
            env["ipai.ppm.task"].sudo().search([]).unlink()
            env["ipai.ppm.template"].sudo().search([]).unlink()
            env["ipai.workstream"].sudo().search([]).unlink()

        # Workstreams
        Workstream = env["ipai.workstream"].sudo()
        ws_by_code = {w.code: w for w in Workstream.search([])}
        for row in payload.get("workstreams", []):
            code = row.get("code")
            if not code:
                continue
            ws = ws_by_code.get(code)
            vals = {
                "name": row.get("name") or code,
                "description": row.get("description"),
                "sap_anchor": row.get("sap_anchor"),
                "odoo_anchor": row.get("odoo_anchor"),
                "active": row.get("active", True),
            }
            if ws:
                ws.write(vals)
            else:
                ws = Workstream.create({"code": code, **vals})
                ws_by_code[code] = ws

        # Worklist types
        Worklist = env["ipai.stc.worklist_type"].sudo()
        wl_by_code = {w.code: w for w in Worklist.search([])}
        for row in payload.get("stc_worklist_types", []):
            code = row.get("code")
            if not code:
                continue
            wl = wl_by_code.get(code)
            vals = {
                "name": row.get("name") or code,
                "description": row.get("description"),
            }
            if wl:
                wl.write(vals)
            else:
                wl = Worklist.create({"code": code, **vals})
                wl_by_code[code] = wl

        # Templates
        Template = env["ipai.ppm.template"].sudo()
        tpl_by_code = {}
        for row in payload.get("templates", []):
            ws_id = row.get("workstream_id")
            ws = ws_by_code.get("AFC") if not ws_id else Workstream.browse(ws_id)
            if ws_id and isinstance(ws_id, int):
                ws = Workstream.browse(ws_id)
                if not ws.exists():
                    ws = ws_by_code.get("AFC")
            code = row.get("code")
            if not code:
                continue
            existing = Template.search(
                [("code", "=", code), ("workstream_id", "=", ws.id)], limit=1
            )
            vals = {
                "workstream_id": ws.id,
                "name": row.get("name") or code,
                "period_type": row.get("period_type") or "monthly",
                "version": row.get("version") or "v1",
                "is_active": row.get("is_active", True),
                "sequence": row.get("sequence", 10),
            }
            if existing:
                existing.write(vals)
                tpl_by_code[code] = existing
            else:
                tpl_by_code[code] = Template.create({"code": code, **vals})

        # Tasks + checklists
        Task = env["ipai.ppm.task"].sudo()
        Checklist = env["ipai.ppm.task.checklist"].sudo()
        task_by_code = {}
        for row in payload.get("tasks", []):
            code = row.get("code")
            if not code:
                continue
            template_id = row.get("template_id")
            template = None
            if template_id:
                template = Template.browse(template_id)
                if not template.exists():
                    template = None
            if not template:
                template = Template.search(
                    [("workstream_id.code", "=", "AFC")], limit=1
                )
            if not template:
                continue
            existing = Task.search(
                [("code", "=", code), ("template_id", "=", template.id)], limit=1
            )
            vals = {
                "template_id": template.id,
                "name": row.get("name") or code,
                "category": row.get("category"),
                "phase": row.get("phase"),
                "sequence": row.get("sequence", 10),
                "due_offset_days": row.get("due_offset_days", 0),
                "prep_offset": row.get("prep_offset", 0),
                "review_offset": row.get("review_offset", 0),
                "owner_role": row.get("owner_role"),
                "requires_approval": row.get("requires_approval", False),
                "evidence_required": row.get("evidence_required", True),
                "sap_reference": row.get("sap_reference"),
            }
            if existing:
                existing.write(vals)
                task = existing
            else:
                task = Task.create({"code": code, **vals})
            task_by_code[code] = task

        # Checklists
        for row in payload.get("checklists", []):
            task_id = row.get("task_id")
            task = Task.browse(task_id) if task_id else None
            if not task or not task.exists():
                continue
            existing = Checklist.search(
                [("task_id", "=", task.id), ("label", "=", row.get("label"))], limit=1
            )
            vals = {
                "task_id": task.id,
                "sequence": row.get("sequence", 10),
                "label": row.get("label"),
                "required": row.get("required", True),
                "evidence_type": row.get("evidence_type") or "file",
                "notes": row.get("notes"),
            }
            if existing:
                existing.write(vals)
            else:
                Checklist.create(vals)

        # STC checks
        Check = env["ipai.stc.check"].sudo()
        for row in payload.get("stc_checks", []):
            code = row.get("code")
            if not code:
                continue
            ws = ws_by_code.get("STC")
            wl = None
            if row.get("worklist_type_id"):
                wl = Worklist.browse(row.get("worklist_type_id"))
                if not wl.exists():
                    wl = None
            existing = Check.search([("code", "=", code)], limit=1)
            vals = {
                "workstream_id": ws.id if ws else False,
                "worklist_type_id": wl.id if wl else False,
                "name": row.get("name") or code,
                "description": row.get("description"),
                "category": row.get("category"),
                "sequence": row.get("sequence", 10),
                "severity": row.get("severity") or "med",
                "is_active": row.get("is_active", True),
                "sap_reference": row.get("sap_reference"),
            }
            if existing:
                existing.write(vals)
            else:
                Check.create({"code": code, **vals})

        # STC scenarios
        Scenario = env["ipai.stc.scenario"].sudo()
        for row in payload.get("stc_scenarios", []):
            code = row.get("code")
            if not code:
                continue
            ws = ws_by_code.get("STC")
            existing = Scenario.search([("code", "=", code)], limit=1)
            check_codes = row.get("check_codes") or []
            checks = Check.search([("code", "in", check_codes)])
            vals = {
                "workstream_id": ws.id if ws else False,
                "name": row.get("name") or code,
                "frequency": row.get("frequency") or "monthly",
                "sequence": row.get("sequence", 10),
                "notes": row.get("notes"),
                "bir_forms": row.get("bir_forms"),
                "sap_reference": row.get("sap_reference"),
                "check_ids": [(6, 0, checks.ids)],
            }
            if existing:
                existing.write(vals)
            else:
                Scenario.create({"code": code, **vals})

        # Overlays
        Overlay = env["ipai.localization.overlay"].sudo()
        for row in payload.get("localization_overlays", []):
            ws_id = row.get("workstream_id")
            ws = None
            if ws_id:
                ws = Workstream.browse(ws_id)
                if not ws.exists():
                    ws = None
            if not ws:
                ws = ws_by_code.get("STC")
            key = (
                row.get("country") or "PH",
                row.get("applies_to_code"),
                row.get("patch_type"),
            )
            existing = Overlay.search(
                [
                    ("country", "=", key[0]),
                    ("applies_to_code", "=", key[1]),
                    ("patch_type", "=", key[2]),
                ],
                limit=1,
            )
            vals = {
                "country": key[0],
                "workstream_id": ws.id if ws else False,
                "applies_to_code": key[1],
                "patch_type": key[2],
                "patch_payload": row.get("patch_payload") or "{}",
                "sequence": row.get("sequence", 10),
                "active": row.get("active", True),
            }
            if existing:
                existing.write(vals)
            else:
                Overlay.create(vals)

        return {"type": "ir.actions.act_window_close"}
