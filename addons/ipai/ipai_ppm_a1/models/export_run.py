# -*- coding: utf-8 -*-
"""
A1 Seed Export/Import

Handles exporting A1 configuration to seed YAML/JSON and importing from seeds.
"""
import hashlib
import json
import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class A1ExportRun(models.Model):
    """
    Audit log for seed export/import operations.
    """

    _name = "a1.export.run"
    _description = "A1 Seed Export/Import Run"
    _order = "create_date desc"

    # Run identification
    run_type = fields.Selection([
        ("export", "Export"),
        ("import", "Import"),
    ], string="Type", required=True)

    # Status
    status = fields.Selection([
        ("pending", "Pending"),
        ("running", "Running"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("error", "Error"),
    ], string="Status", default="pending", required=True)

    # Payload
    seed_json = fields.Text(string="Seed JSON")
    seed_hash = fields.Char(string="Seed Hash", index=True)

    # Stats
    created_count = fields.Integer(string="Created", default=0)
    updated_count = fields.Integer(string="Updated", default=0)
    unchanged_count = fields.Integer(string="Unchanged", default=0)
    error_count = fields.Integer(string="Errors", default=0)

    # Log
    log = fields.Text(string="Log")

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Webhook
    webhook_url = fields.Char(string="Webhook URL")

    @api.model
    def export_to_seed(self, company_id=None):
        """
        Export A1 configuration to seed JSON.

        Returns:
            dict: Seed payload
        """
        company_id = company_id or self.env.company.id

        # Create run record
        run = self.create({
            "run_type": "export",
            "status": "running",
            "company_id": company_id,
        })

        try:
            seed = self._build_seed_payload(company_id)
            seed_json = json.dumps(seed, indent=2, ensure_ascii=False, default=str)
            seed_hash = hashlib.sha256(seed_json.encode()).hexdigest()[:16]

            run.write({
                "status": "success",
                "seed_json": seed_json,
                "seed_hash": seed_hash,
            })

            return seed

        except Exception as e:
            run.write({
                "status": "error",
                "log": str(e),
            })
            raise

    def _build_seed_payload(self, company_id):
        """Build the seed payload from A1 configuration."""
        company = self.env["res.company"].browse(company_id)

        # Get workstreams grouped by phase
        workstreams = self.env["a1.workstream"].search([
            ("company_id", "=", company_id),
            ("active", "=", True),
        ])

        # Group by phase
        phases = {}
        for ws in workstreams:
            phase_code = ws.phase_code or "DEFAULT"
            if phase_code not in phases:
                phases[phase_code] = []
            phases[phase_code].append(ws)

        # Build cycles structure
        cycles = []
        for phase_code, phase_workstreams in phases.items():
            ws_list = []
            for ws in phase_workstreams:
                templates = []
                for tpl in ws.template_ids:
                    steps = []
                    for step in tpl.step_ids:
                        steps.append({
                            "step_code": step.code,
                            "name": step.name,
                            "default_assignee": step.assignee_role,
                            "effort_days": step.effort_days,
                            "deadline_offset_days": step.deadline_offset_days,
                        })

                    checklist = []
                    for item in tpl.checklist_ids:
                        checklist.append({
                            "code": item.code,
                            "name": item.name,
                            "type": item.item_type,
                            "required": item.is_required,
                        })

                    templates.append({
                        "task_template_code": tpl.code,
                        "name": tpl.name,
                        "owner_role": tpl.owner_role,
                        "reviewer_role": tpl.reviewer_role,
                        "approver_role": tpl.approver_role,
                        "steps": steps,
                        "checklist": checklist,
                    })

                ws_list.append({
                    "workstream_code": ws.code,
                    "name": ws.name,
                    "owner_role": ws.owner_role_id.code if ws.owner_role_id else None,
                    "task_templates": templates,
                })

            cycles.append({
                "cycle_code": "MONTH_END_CLOSE",
                "name": "Month-End Close",
                "phases": [{
                    "phase_code": phase_code,
                    "name": phase_code,
                    "workstreams": ws_list,
                }],
            })

        # Get roles
        roles = self.env["a1.role"].search([("company_id", "=", company_id)])
        directory = {
            "identifier": "role_code",
            "entries": [
                {
                    "role_code": r.code,
                    "name": r.name,
                    "default_user": r.default_user_id.login if r.default_user_id else None,
                }
                for r in roles
            ],
        }

        return {
            "schema_version": "1.1.0",
            "seed_id": f"a1_seed_{company.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timezone": "Asia/Manila",
            "company": {
                "id": company.id,
                "name": company.name,
            },
            "directory": directory,
            "cycles": cycles,
        }

    @api.model
    def import_from_seed(self, seed, company_id=None, dry_run=False):
        """
        Import A1 configuration from seed JSON.

        Args:
            seed: Seed dict or JSON string
            company_id: Target company
            dry_run: If True, validate only without persisting

        Returns:
            dict: Import report
        """
        if isinstance(seed, str):
            seed = json.loads(seed)

        company_id = company_id or self.env.company.id

        # Create run record
        run = self.create({
            "run_type": "import",
            "status": "running",
            "company_id": company_id,
            "seed_json": json.dumps(seed, indent=2),
        })

        report = {
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": [],
            "warnings": [],
        }

        try:
            # Import roles
            self._import_roles(seed, company_id, report, dry_run)

            # Import workstreams and templates
            for cycle in seed.get("cycles", []):
                for phase in cycle.get("phases", []):
                    for ws_data in phase.get("workstreams", []):
                        self._import_workstream(ws_data, phase, company_id, report, dry_run)

            status = "success" if not report["errors"] else "warning"
            run.write({
                "status": status,
                "created_count": report["created"],
                "updated_count": report["updated"],
                "unchanged_count": report["unchanged"],
                "error_count": len(report["errors"]),
                "log": json.dumps(report, indent=2),
            })

            return report

        except Exception as e:
            run.write({
                "status": "error",
                "log": str(e),
            })
            raise

    def _import_roles(self, seed, company_id, report, dry_run):
        """Import roles from seed."""
        Role = self.env["a1.role"]
        directory = seed.get("directory", {})

        for entry in directory.get("entries", []):
            role_code = entry.get("role_code")
            if not role_code:
                continue

            existing = Role.search([
                ("code", "=", role_code),
                ("company_id", "=", company_id),
            ], limit=1)

            vals = {
                "code": role_code,
                "name": entry.get("name", role_code),
                "company_id": company_id,
            }

            if existing:
                if not dry_run:
                    existing.write(vals)
                report["updated"] += 1
            else:
                if not dry_run:
                    Role.create(vals)
                report["created"] += 1

    def _import_workstream(self, ws_data, phase, company_id, report, dry_run):
        """Import a workstream and its templates."""
        Workstream = self.env["a1.workstream"]
        Template = self.env["a1.template"]

        ws_code = ws_data.get("workstream_code")
        if not ws_code:
            return

        # Find or create workstream
        existing_ws = Workstream.search([
            ("code", "=", ws_code),
            ("company_id", "=", company_id),
        ], limit=1)

        ws_vals = {
            "code": ws_code,
            "name": ws_data.get("name", ws_code),
            "phase_code": phase.get("phase_code"),
            "company_id": company_id,
        }

        if existing_ws:
            if not dry_run:
                existing_ws.write(ws_vals)
            workstream = existing_ws
            report["updated"] += 1
        else:
            if not dry_run:
                workstream = Workstream.create(ws_vals)
            else:
                workstream = None
            report["created"] += 1

        # Import templates
        for tpl_data in ws_data.get("task_templates", []):
            tpl_code = tpl_data.get("task_template_code")
            if not tpl_code:
                continue

            existing_tpl = Template.search([
                ("code", "=", tpl_code),
                ("company_id", "=", company_id),
            ], limit=1)

            tpl_vals = {
                "code": tpl_code,
                "name": tpl_data.get("name", tpl_code),
                "workstream_id": workstream.id if workstream else False,
                "owner_role": tpl_data.get("owner_role"),
                "reviewer_role": tpl_data.get("reviewer_role"),
                "approver_role": tpl_data.get("approver_role"),
                "company_id": company_id,
            }

            if existing_tpl:
                if not dry_run:
                    existing_tpl.write(tpl_vals)
                report["updated"] += 1
            else:
                if not dry_run:
                    Template.create(tpl_vals)
                report["created"] += 1
