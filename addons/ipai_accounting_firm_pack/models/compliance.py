# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ComplianceTask(models.Model):
    """Compliance task for tracking deadlines and requirements."""
    _name = "ipai.compliance.task"
    _description = "IPAI Compliance Task"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "due_date, priority desc"

    name = fields.Char(string="Task Name", required=True, tracking=True)

    engagement_id = fields.Many2one(
        "ipai.engagement",
        string="Engagement",
        required=True,
        tracking=True,
        ondelete="cascade",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client",
        related="engagement_id.partner_id",
        store=True,
    )

    task_type = fields.Selection([
        ("tax_filing", "Tax Filing"),
        ("annual_report", "Annual Report"),
        ("quarterly_report", "Quarterly Report"),
        ("monthly_close", "Monthly Close"),
        ("audit_procedure", "Audit Procedure"),
        ("client_request", "Client Request"),
        ("internal", "Internal Task"),
        ("regulatory", "Regulatory Requirement"),
        ("other", "Other"),
    ], string="Task Type", required=True, tracking=True)

    due_date = fields.Date(string="Due Date", required=True, tracking=True)
    completion_date = fields.Date(string="Completion Date")

    priority = fields.Selection([
        ("0", "Low"),
        ("1", "Normal"),
        ("2", "High"),
        ("3", "Urgent"),
    ], string="Priority", default="1", tracking=True)

    state = fields.Selection([
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("blocked", "Blocked"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="todo", tracking=True)

    assigned_id = fields.Many2one(
        "res.users",
        string="Assigned To",
        tracking=True,
    )

    reviewer_id = fields.Many2one(
        "res.users",
        string="Reviewer",
    )

    description = fields.Text(string="Description")
    notes = fields.Text(string="Notes")

    # Color for kanban
    color = fields.Integer(string="Color Index")

    # Days until due (for filtering)
    days_until_due = fields.Integer(
        string="Days Until Due",
        compute="_compute_days_until_due",
        store=True,
    )

    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_days_until_due",
        store=True,
    )

    @api.depends("due_date", "state")
    def _compute_days_until_due(self):
        today = fields.Date.today()
        for task in self:
            if task.due_date:
                delta = (task.due_date - today).days
                task.days_until_due = delta
                task.is_overdue = delta < 0 and task.state not in ("done", "cancelled")
            else:
                task.days_until_due = 0
                task.is_overdue = False

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_block(self):
        self.write({"state": "blocked"})

    def action_done(self):
        self.write({
            "state": "done",
            "completion_date": fields.Date.today(),
        })

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset(self):
        self.write({"state": "todo", "completion_date": False})


class DocumentRequest(models.Model):
    """Document request for client document collection."""
    _name = "ipai.document.request"
    _description = "IPAI Document Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "client_upload_deadline, create_date desc"

    name = fields.Char(
        string="Request Reference",
        default=lambda self: _("New"),
        readonly=True,
        copy=False,
    )

    engagement_id = fields.Many2one(
        "ipai.engagement",
        string="Engagement",
        required=True,
        tracking=True,
        ondelete="cascade",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client",
        related="engagement_id.partner_id",
        store=True,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("sent", "Sent to Client"),
        ("partial", "Partially Received"),
        ("received", "Fully Received"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="draft", tracking=True)

    request_list = fields.Text(
        string="Document Request List (JSON)",
        help="JSON array of requested documents with status",
        default='[]',
    )

    request_description = fields.Html(
        string="Request Description",
        help="Human-readable description of requested documents",
    )

    client_upload_deadline = fields.Date(
        string="Client Upload Deadline",
        required=True,
        tracking=True,
    )

    sent_date = fields.Date(string="Sent Date")
    received_date = fields.Date(string="Received Date")

    # Link to DMS if available (placeholder for OCA DMS integration)
    dms_directory_id = fields.Integer(
        string="DMS Directory ID",
        help="Reference to DMS directory for uploads",
    )

    notes = fields.Text(string="Notes")

    # Attachment count
    attachment_count = fields.Integer(
        string="Attachments",
        compute="_compute_attachment_count",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "ipai.document.request"
                ) or _("New")
        return super().create(vals_list)

    def _compute_attachment_count(self):
        Attachment = self.env["ir.attachment"]
        for request in self:
            request.attachment_count = Attachment.search_count([
                ("res_model", "=", self._name),
                ("res_id", "=", request.id),
            ])

    def action_send(self):
        self.write({
            "state": "sent",
            "sent_date": fields.Date.today(),
        })

    def action_mark_partial(self):
        self.write({"state": "partial"})

    def action_mark_received(self):
        self.write({
            "state": "received",
            "received_date": fields.Date.today(),
        })

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_view_attachments(self):
        """View attachments for this request."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Attachments"),
            "res_model": "ir.attachment",
            "view_mode": "kanban,list,form",
            "domain": [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ],
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }
