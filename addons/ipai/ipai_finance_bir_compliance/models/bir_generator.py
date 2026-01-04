# -*- coding: utf-8 -*-
"""BIR Task Generator."""
import logging
from datetime import date

from odoo.exceptions import UserError

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class BIRGenerator(models.AbstractModel):
    _name = "ipai.bir.generator"
    _description = "BIR Task Generator"

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
    def generate(self, program_project, date_from=None, date_to=None, dry_run=False):
        """
        Generate tasks into IM projects based on BIR schedule items.

        Idempotent per (project, name, target_date).

        Args:
            program_project: The parent Program project
            date_from: Optional start date filter for deadlines
            date_to: Optional end date filter for deadlines
            dry_run: If True, count but don't create tasks

        Returns:
            Number of tasks created (or would be created in dry_run)
        """
        if not program_project or not program_project.is_program:
            raise UserError(_("Please select a Program project (is_program=True)."))

        Item = self.env["ipai.bir.schedule.item"].sudo()
        Task = self.env["project.task"].sudo()

        # Build domain for schedule items
        domain = [("active", "=", True)]
        if date_from:
            domain.append(("deadline", ">=", date_from))
        if date_to:
            domain.append(("deadline", "<=", date_to))

        created = 0
        for item in Item.search(domain, order="deadline asc"):
            # Resolve target IM project
            im = self.env.ref(item.im_xml_id, raise_if_not_found=False)
            if not im:
                # Fallback: use program's IM2
                im = (
                    self.env["project.project"]
                    .sudo()
                    .search(
                        [
                            ("parent_id", "=", program_project.id),
                            ("im_code", "=", "IM2"),
                        ],
                        limit=1,
                    )
                )
            if not im:
                _logger.warning(
                    "No IM project found for BIR item: %s %s",
                    item.bir_form,
                    item.period_covered,
                )
                continue

            for step in item.step_ids:
                label = dict(step._fields["activity_type"].selection).get(
                    step.activity_type
                )
                target = step.compute_target_date(item.deadline)
                task_name = f"{item.bir_form} ({item.period_covered}) - {label}"
                stage = self._find_stage(label) or False

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
                    "bir_form": item.bir_form,
                    "period_covered": item.period_covered,
                    "target_date": target,
                }
                if user:
                    vals["user_ids"] = [(6, 0, [user.id])]

                Task.create(vals)
                created += 1

        _logger.info(
            "BIR generation complete: %d tasks %s",
            created,
            "would be created (dry run)" if dry_run else "created",
        )
        return created
