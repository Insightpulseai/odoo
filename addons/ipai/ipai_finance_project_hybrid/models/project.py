# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.exceptions import UserError

from odoo import _, api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    ipai_is_im_project = fields.Boolean(
        string="Is IM Project", default=False, index=True
    )
    ipai_im_code = fields.Selection([("IM1", "IM1"), ("IM2", "IM2")], index=True)
    ipai_root_project_id = fields.Many2one(
        "project.project", string="Root Project", index=True, ondelete="set null"
    )
    ipai_finance_enabled = fields.Boolean(
        string="Finance Analytics Enabled", default=False
    )

    def action_ipai_generate_im_projects(self):
        self.ensure_one()
        wiz = self.env["ipai.generate.im.projects.wizard"].create(
            {"project_id": self.id}
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Generate IM Projects"),
            "res_model": "ipai.generate.im.projects.wizard",
            "view_mode": "form",
            "target": "new",
            "res_id": wiz.id,
        }

    def _ipai_find_or_create_child(self, im_code: str, name_suffix: str):
        self.ensure_one()
        child = self.search(
            [
                ("ipai_is_im_project", "=", True),
                ("ipai_root_project_id", "=", self.id),
                ("ipai_im_code", "=", im_code),
            ],
            limit=1,
        )
        if child:
            return child
        vals = {
            "name": f"{self.name} - {name_suffix}",
            "ipai_is_im_project": True,
            "ipai_im_code": im_code,
            "ipai_root_project_id": self.id,
            "ipai_finance_enabled": True,
            "privacy_visibility": "followers",
        }
        # Copy key project defaults where possible
        for f in ["company_id", "partner_id", "user_id", "allow_timesheets"]:
            if f in self._fields:
                vals[f] = getattr(self, f).id if getattr(self, f) else False
        return self.create(vals)

    def ipai_generate_tasks_from_templates(self, month_end: date = None):
        self.ensure_one()
        if not month_end:
            # default: end of current month
            today = fields.Date.today()
            month_end = (today.replace(day=28) + timedelta(days=4)).replace(
                day=1
            ) - timedelta(days=1)

        Template = self.env["ipai.finance.task.template"].search(
            [("active", "=", True)]
        )
        if not Template:
            raise UserError(
                _("No finance task templates found. Run Finance Seed first.")
            )

        Task = self.env["project.task"]
        created = self.env["project.task"]

        for t in Template:
            if t.anchor == "manual":
                continue
            anchor_date = month_end
            due = anchor_date + timedelta(days=t.offset_days)
            # build task name with category prefix
            name = t.name
            vals = {
                "name": name,
                "project_id": self.id,
                "date_deadline": due,
                "ipai_task_category": t.task_category,
                "ipai_template_id": t.id,
            }
            # Assign by prep_by_code if resolvable
            if t.prep_by_code:
                user = self.env["ipai.finance.directory"].resolve_user(t.prep_by_code)
                if user:
                    vals["user_ids"] = [(6, 0, [user.id])]
                    vals["ipai_owner_code"] = t.prep_by_code
                    vals["ipai_owner_role"] = "prep"
            existing = Task.search(
                [
                    ("project_id", "=", self.id),
                    ("ipai_template_id", "=", t.id),
                    ("date_deadline", "=", due),
                ],
                limit=1,
            )
            if existing:
                continue
            created |= Task.create(vals)

        return created

    def ipai_generate_tasks_from_bir_schedule(self):
        self.ensure_one()
        Schedule = self.env["ipai.bir.schedule.line"].search([])
        if not Schedule:
            raise UserError(_("No BIR schedule found. Run Finance Seed first."))

        Task = self.env["project.task"]
        created = self.env["project.task"]

        def _mk(name, code, role, due, step):
            vals = {
                "name": name,
                "project_id": self.id,
                "date_deadline": due,
                "ipai_task_category": "tax",
                "ipai_owner_code": code,
                "ipai_owner_role": role,
                "ipai_compliance_step": step,
            }
            user = (
                self.env["ipai.finance.directory"].resolve_user(code) if code else False
            )
            if user:
                vals["user_ids"] = [(6, 0, [user.id])]
            return vals

        for line in Schedule:
            # create 3-step workflow tasks if dates exist; otherwise single task due on deadline
            base = f"{line.bir_form} - {line.period_label}"
            steps = []
            if line.prep_due_date:
                steps.append(
                    (
                        "Prepare",
                        line.prep_by_code,
                        "prep",
                        line.prep_due_date,
                        "prepare",
                    )
                )
            if line.review_due_date:
                steps.append(
                    (
                        "Review",
                        line.review_by_code,
                        "review",
                        line.review_due_date,
                        "review",
                    )
                )
            if line.approve_due_date:
                steps.append(
                    (
                        "Approve/Pay",
                        line.approve_by_code,
                        "approve",
                        line.approve_due_date,
                        "approve",
                    )
                )
            if not steps:
                steps = [
                    (
                        "File/Pay",
                        line.approve_by_code
                        or line.review_by_code
                        or line.prep_by_code,
                        "approve",
                        line.deadline_date,
                        "file",
                    )
                ]

            for label, code, role, due, step in steps:
                name = f"{base} — {label}"
                exists = Task.search(
                    [
                        ("project_id", "=", self.id),
                        ("name", "=", name),
                        ("date_deadline", "=", due),
                    ],
                    limit=1,
                )
                if exists:
                    continue
                created |= Task.create(_mk(name, code, role, due, step))

        return created
