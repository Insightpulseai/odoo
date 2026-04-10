"""PPM Issue Register — project issue tracking.

Delta model: CE/OCA do not provide a structured issue register.
"""

from odoo import fields, models


class PPMIssue(models.Model):
    _name = "ppm.issue"
    _description = "PPM Issue"
    _order = "priority desc, create_date desc"

    name = fields.Char(string="Issue Title", required=True)
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="project_id.company_id",
        store=True,
    )
    description = fields.Text(string="Description")
    category = fields.Selection(
        [
            ("financial", "Financial"),
            ("schedule", "Schedule"),
            ("resource", "Resource"),
            ("technical", "Technical"),
            ("compliance", "Compliance"),
            ("stakeholder", "Stakeholder"),
        ],
        string="Category",
        default="financial",
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("investigating", "Investigating"),
            ("escalated", "Escalated"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="open",
    )
    priority = fields.Selection(
        [("0", "Low"), ("1", "Medium"), ("2", "High"), ("3", "Critical")],
        string="Priority",
        default="1",
    )
    owner_id = fields.Many2one("res.users", string="Issue Owner")
    resolution = fields.Text(string="Resolution")
    raised_date = fields.Date(string="Raised Date", default=fields.Date.today)
    target_date = fields.Date(string="Target Resolution Date")
    resolved_date = fields.Date(string="Resolved Date")
