# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    cr.execute("SELECT to_regclass('ipai_finance_task_template')")
    table_exists = cr.fetchone()[0]
    if not table_exists:
        return

    cr.execute(
        """
        SELECT id, name, category, employee_code_id, reviewed_by_id, approved_by_id,
               prep_duration, review_duration, approval_duration
        FROM ipai_finance_task_template
        """
    )
    templates = cr.dictfetchall()
    if not templates:
        return

    project = env.ref("ipai_finance_ppm.finance_month_end_project", raise_if_not_found=False)
    if not project:
        project = (
            env["project.project"].search([("name", "=", "Finance Month-End & Compliance")], limit=1)
            or env["project.project"].create({"name": "Finance Month-End & Compliance"})
        )

    finance_person_model = env["ipai.finance.person"]
    task_model = env["project.task"]

    for template in templates:
        owner = finance_person_model.browse(template["employee_code_id"]) if template["employee_code_id"] else finance_person_model.browse()
        reviewer_person = finance_person_model.browse(template["reviewed_by_id"]) if template["reviewed_by_id"] else finance_person_model.browse()
        approver_person = finance_person_model.browse(template["approved_by_id"]) if template["approved_by_id"] else finance_person_model.browse()

        description_parts = []
        if template["category"]:
            description_parts.append(f"Category: {template['category']}")

        durations = []
        if template["prep_duration"]:
            durations.append(f"Prep SLA: {template['prep_duration']} days")
        if template["review_duration"]:
            durations.append(f"Review SLA: {template['review_duration']} days")
        if template["approval_duration"]:
            durations.append(f"Approval SLA: {template['approval_duration']} days")
        if durations:
            description_parts.append("; ".join(durations))

        if reviewer_person:
            description_parts.append(f"Reviewer: {reviewer_person.display_name}")
        if approver_person:
            description_parts.append(f"Approver: {approver_person.display_name}")

        description = "\n".join(description_parts) if description_parts else False

        existing = task_model.search(
            [
                ("project_id", "=", project.id),
                ("name", "=", template["name"]),
            ],
            limit=1,
        )

        vals = {
            "name": template["name"],
            "project_id": project.id,
            "finance_code": owner.code if owner else False,
            "finance_deadline_type": "monthly",
            "reviewer_id": reviewer_person.user_id.id if reviewer_person.user_id else False,
            "approver_id": approver_person.user_id.id if approver_person.user_id else False,
            "description": description,
        }

        if owner.user_id:
            vals["user_ids"] = [(6, 0, [owner.user_id.id])]

        if existing:
            existing.write(vals)
        else:
            task_model.create(vals)
