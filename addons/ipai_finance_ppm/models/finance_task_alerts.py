# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models


class ProjectTaskAlerts(models.Model):
    _inherit = "project.task"

    def write(self, vals):
        tasks = self
        previous_assignees = {}
        if "user_ids" in vals:
            for task in tasks:
                previous_assignees[task.id] = set(task.user_ids.ids)

        res = super().write(vals)

        if "stage_id" in vals:
            new_stage = self.env["project.task.type"].browse(vals["stage_id"])
            if new_stage and "Approv" in (new_stage.name or ""):
                for task in tasks.filtered(lambda t: t.approver_id):
                    partner = task.approver_id.partner_id
                    if partner:
                        task.message_post(
                            body=(
                                f"⚠️ <b>Stage Change:</b> Task moved to {new_stage.name}. "
                                "Review required."
                            ),
                            partner_ids=[partner.id],
                            message_type="comment",
                            subtype_xmlid="mail.mt_comment",
                        )

        if "user_ids" in vals:
            for task in tasks:
                previous = previous_assignees.get(task.id, set())
                current = set(task.user_ids.ids)
                added_user_ids = current - previous
                if not added_user_ids:
                    continue
                partners = (
                    self.env["res.users"].browse(list(added_user_ids)).mapped("partner_id")
                )
                partners = partners.filtered(
                    lambda partner: partner and partner.id != self.env.user.partner_id.id
                )
                if partners:
                    task.message_post(
                        body="👋 <b>Handover Alert:</b> You have been assigned to this task.",
                        partner_ids=partners.ids,
                        message_type="comment",
                        subtype_xmlid="mail.mt_comment",
                    )

        return res

    @api.model
    def _cron_deadline_nudge(self):
        tomorrow = fields.Date.context_today(self) + timedelta(days=1)
        tasks_due = self.search(
            [
                ("date_deadline", "=", tomorrow),
                ("stage_id.fold", "=", False),
                ("user_ids", "!=", False),
            ]
        )

        for task in tasks_due:
            partners_to_ping = task.user_ids.mapped("partner_id").ids
            if partners_to_ping:
                task.message_post(
                    body=f"⏰ <b>Deadline Alert:</b> This task is due tomorrow ({tomorrow}).",
                    partner_ids=partners_to_ping,
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                )
