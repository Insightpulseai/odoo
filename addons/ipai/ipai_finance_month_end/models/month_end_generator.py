# -*- coding: utf-8 -*-
"""Month-End Task Generator."""
import logging
from datetime import date

from odoo.exceptions import UserError

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class MonthEndGenerator(models.AbstractModel):
    _name = "ipai.month.end.generator"
    _description = "Month-End Task Generator"

    @api.model
    def _find_stage(self, label: str):
        """Find task stage by name."""
        return (
            self.env["project.task.type"].sudo().search([("name", "=", label)], limit=1)
        )

    @api.model
    def _find_user_by_role_code(self, role_code: str):
        """
        Map role_code -> directory email -> res.users by login/email.
        If none found, return empty recordset.
        """
        if not role_code:
            return self.env["res.users"]
        person = (
            self.env["ipai.directory.person"]
            .sudo()
            .search([("code", "=", role_code)], limit=1)
        )
        if not person or not person.email:
            return self.env["res.users"]
        user = (
            self.env["res.users"].sudo().search([("login", "=", person.email)], limit=1)
        )
        if not user:
            user = (
                self.env["res.users"]
                .sudo()
                .search([("email", "=", person.email)], limit=1)
            )
        return user

    @api.model
    def generate(
        self, program_project, anchor_date: date, templates=None, dry_run=False
    ):
        """
        Generate tasks into IM projects based on templates.

        Idempotent per (project, name, target_date).

        Args:
            program_project: The parent Program project
            anchor_date: Anchor date for offset calculations
            templates: Optional specific templates (None = all active)
            dry_run: If True, count but don't create tasks

        Returns:
            Number of tasks created (or would be created in dry_run)
        """
        if not program_project or not program_project.is_program:
            raise UserError(_("Please select a Program project (is_program=True)."))

        Template = self.env["ipai.month.end.template"].sudo()
        Task = self.env["project.task"].sudo()

        templates = templates or Template.search([("active", "=", True)])
        created = 0

        for tmpl in templates:
            # Resolve target IM project
            im = None
            if tmpl.default_im_xml_id:
                im = self.env.ref(tmpl.default_im_xml_id, raise_if_not_found=False)
            if not im:
                # Fallback: use program's IM1
                im = (
                    self.env["project.project"]
                    .sudo()
                    .search(
                        [
                            ("parent_id", "=", program_project.id),
                            ("im_code", "=", "IM1"),
                        ],
                        limit=1,
                    )
                )
            if not im:
                _logger.warning(
                    "No IM project found for template: %s", tmpl.task_base_name
                )
                continue

            for step in tmpl.step_ids:
                target = step.compute_target_date(anchor_date)
                activity_label = dict(step._fields["activity_type"].selection).get(
                    step.activity_type
                )
                task_name = f"{tmpl.task_base_name} - {activity_label}"
                stage = self._find_stage(activity_label) or False

                # Idempotency key: (project_id, name, date_deadline)
                existing = Task.search(
                    [
                        ("project_id", "=", im.id),
                        ("name", "=", task_name),
                        ("date_deadline", "=", target),
                    ],
                    limit=1,
                )
                if existing:
                    continue

                if dry_run:
                    created += 1
                    continue

                user = self._find_user_by_role_code(step.role_code)
                vals = {
                    "project_id": im.id,
                    "name": task_name,
                    "date_deadline": target,
                    "stage_id": stage.id if stage else False,
                    "activity_type": step.activity_type,
                    "role_code": step.role_code,
                }
                if user:
                    vals["user_ids"] = [(6, 0, [user.id])]

                Task.create(vals)
                created += 1

        _logger.info(
            "Month-end generation complete: %d tasks %s",
            created,
            "would be created (dry run)" if dry_run else "created",
        )
        return created
