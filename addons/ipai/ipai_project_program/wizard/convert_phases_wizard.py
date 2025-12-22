# -*- coding: utf-8 -*-
"""Wizard to convert legacy phases into IM child projects."""
from odoo import _, fields, models
from odoo.exceptions import UserError


class IPAIConvertPhasesWizard(models.TransientModel):
    _name = "ipai.convert.phases.wizard"
    _description = "Convert legacy phases into IM child projects"

    parent_project_id = fields.Many2one(
        "project.project",
        string="Parent Program",
        required=True,
        domain=[("is_program", "=", True)],
        help="Select the parent Program project",
    )
    im1_name = fields.Char(
        string="IM1 Name",
        default="IM1 - Month-End Closing Planning",
        required=True,
    )
    im2_name = fields.Char(
        string="IM2 Name",
        default="IM2 - Tax Filing & Compliance",
        required=True,
    )
    move_tasks_by_keyword = fields.Boolean(
        string="Move Tasks by Keyword",
        default=True,
        help="Automatically move tasks from parent to IM projects based on keywords",
    )
    im1_keywords = fields.Char(
        string="IM1 Keywords",
        default="Month-End,Closing,Accrual,Amortization,WIP,Trial Balance,Payroll",
        help="Comma-separated keywords for IM1 tasks",
    )
    im2_keywords = fields.Char(
        string="IM2 Keywords",
        default="Tax,BIR,VAT,Withholding,1601,1702,2550,0619",
        help="Comma-separated keywords for IM2 tasks",
    )

    def action_convert(self):
        """Create IM projects and optionally move tasks."""
        self.ensure_one()
        parent = self.parent_project_id.sudo()
        if not parent:
            raise UserError(_("Parent program not found."))

        def _get_or_create_child(im_code, name):
            child = (
                self.env["project.project"]
                .sudo()
                .search(
                    [("parent_id", "=", parent.id), ("im_code", "=", im_code)], limit=1
                )
            )
            if child:
                child.write({"name": name})
                return child
            return (
                self.env["project.project"]
                .sudo()
                .create(
                    {
                        "name": name,
                        "parent_id": parent.id,
                        "im_code": im_code,
                        "program_code": parent.program_code,
                        "program_type": parent.program_type,
                        "is_program": False,
                    }
                )
            )

        im1 = _get_or_create_child("IM1", self.im1_name)
        im2 = _get_or_create_child("IM2", self.im2_name)

        moved_count = 0
        if self.move_tasks_by_keyword:
            Task = self.env["project.task"].sudo()
            tasks = Task.search([("project_id", "=", parent.id)])
            im1_kw = [
                k.strip().lower()
                for k in (self.im1_keywords or "").split(",")
                if k.strip()
            ]
            im2_kw = [
                k.strip().lower()
                for k in (self.im2_keywords or "").split(",")
                if k.strip()
            ]

            for t in tasks:
                name = (t.name or "").lower()
                if any(k in name for k in im2_kw):
                    t.write({"project_id": im2.id})
                    moved_count += 1
                elif any(k in name for k in im1_kw):
                    t.write({"project_id": im1.id})
                    moved_count += 1
                # else leave in parent for manual handling

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Conversion Complete"),
                "message": _("Created/Updated IM1 and IM2 projects. Moved %s tasks.")
                % moved_count,
                "sticky": False,
                "type": "success",
            },
        }
