from odoo import fields, models


class IpaiPpmTask(models.Model):
    _name = "ipai.ppm.task"
    _description = "PPM Task (Canonical)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "template_id, sequence, name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    template_id = fields.Many2one(
        "ipai.ppm.template", required=True, ondelete="cascade", index=True
    )
    category = fields.Char(
        help="SAP-style category e.g. Accruals, VAT, AR/AP, WIP, etc."
    )
    phase = fields.Selection(
        [
            ("I", "Phase I"),
            ("II", "Phase II"),
            ("III", "Phase III"),
            ("IV", "Phase IV"),
        ],
        help="AFC closing phase",
    )
    sequence = fields.Integer(default=10)
    due_offset_days = fields.Integer(
        default=0, help="Offset from period end (negative = before end)"
    )
    prep_offset = fields.Integer(default=0, help="Prep due offset from period end")
    review_offset = fields.Integer(default=0, help="Review due offset from period end")
    owner_role = fields.Char(help="RACI: e.g. RIM, BOM, CKVC, FD")
    requires_approval = fields.Boolean(default=False)
    evidence_required = fields.Boolean(default=True)
    sap_reference = fields.Char(help="SAP AFC task reference code")

    checklist_line_ids = fields.One2many("ipai.ppm.task.checklist", "task_id")

    _sql_constraints = [
        (
            "task_code_unique",
            "unique(code, template_id)",
            "Task code must be unique per template.",
        ),
    ]


class IpaiPpmTaskChecklist(models.Model):
    _name = "ipai.ppm.task.checklist"
    _description = "Task Checklist (Evidence)"
    _order = "sequence, id"

    task_id = fields.Many2one(
        "ipai.ppm.task", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    label = fields.Char(required=True)
    required = fields.Boolean(default=True)
    evidence_type = fields.Selection(
        [
            ("file", "File"),
            ("link", "Link"),
            ("note", "Note"),
            ("report", "Report Output"),
        ],
        default="file",
        required=True,
    )
    notes = fields.Char()
