# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ImplementationTemplate(models.Model):
    """Implementation project templates for service delivery."""
    _name = "ipai.implementation.template"
    _description = "IPAI Implementation Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(string="Template Name", required=True, tracking=True)
    code = fields.Char(string="Template Code", tracking=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(default=True)

    description = fields.Html(string="Description")

    phase_ids = fields.One2many(
        "ipai.implementation.phase",
        "template_id",
        string="Phases",
    )

    deliverable_ids = fields.One2many(
        "ipai.implementation.deliverable",
        "template_id",
        string="Deliverables",
    )

    # Statistics
    total_phases = fields.Integer(
        string="Total Phases",
        compute="_compute_totals",
        store=True,
    )
    total_deliverables = fields.Integer(
        string="Total Deliverables",
        compute="_compute_totals",
        store=True,
    )
    estimated_duration = fields.Float(
        string="Estimated Duration (Days)",
        compute="_compute_totals",
        store=True,
    )

    @api.depends("phase_ids", "deliverable_ids", "phase_ids.duration_days")
    def _compute_totals(self):
        for template in self:
            template.total_phases = len(template.phase_ids)
            template.total_deliverables = len(template.deliverable_ids)
            template.estimated_duration = sum(template.phase_ids.mapped("duration_days"))

    def action_create_project(self, partner_id=None, sale_order_id=None):
        """Create a project from this template."""
        self.ensure_one()
        project_vals = {
            "name": f"{self.name} - Implementation",
            "description": self.description,
            "partner_id": partner_id,
            "sale_order_id": sale_order_id,
        }

        project = self.env["project.project"].create(project_vals)

        # Create tasks from phases
        for phase in self.phase_ids.sorted("sequence"):
            task_vals = {
                "name": phase.name,
                "project_id": project.id,
                "description": phase.description,
            }
            self.env["project.task"].create(task_vals)

        return project

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Template code must be unique!"),
    ]


class ImplementationPhase(models.Model):
    """Implementation phases within a template."""
    _name = "ipai.implementation.phase"
    _description = "IPAI Implementation Phase"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "ipai.implementation.template",
        string="Template",
        required=True,
        ondelete="cascade",
    )

    name = fields.Char(string="Phase Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Html(string="Description")

    duration_days = fields.Float(string="Duration (Days)", default=5.0)

    milestone_type = fields.Selection([
        ("kickoff", "Kickoff"),
        ("discovery", "Discovery Complete"),
        ("config", "Configuration Complete"),
        ("migration", "Data Migration Complete"),
        ("uat", "UAT Signoff"),
        ("golive", "Go-Live"),
        ("hypercare", "Hypercare Complete"),
        ("closure", "Project Closure"),
    ], string="Milestone Type")

    gate_criteria = fields.Text(
        string="Gate Criteria",
        help="Criteria that must be met to complete this phase",
    )


class ImplementationDeliverable(models.Model):
    """Deliverables associated with implementation templates."""
    _name = "ipai.implementation.deliverable"
    _description = "IPAI Implementation Deliverable"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "ipai.implementation.template",
        string="Template",
        required=True,
        ondelete="cascade",
    )

    phase_id = fields.Many2one(
        "ipai.implementation.phase",
        string="Phase",
        domain="[('template_id', '=', template_id)]",
    )

    name = fields.Char(string="Deliverable Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(string="Description")

    deliverable_type = fields.Selection([
        ("document", "Document"),
        ("configuration", "Configuration"),
        ("training", "Training Material"),
        ("signoff", "Signoff/Approval"),
        ("artifact", "Technical Artifact"),
    ], string="Type", required=True, default="document")

    is_mandatory = fields.Boolean(string="Mandatory", default=True)

    owner_role = fields.Selection([
        ("pm", "Project Manager"),
        ("consultant", "Consultant"),
        ("developer", "Developer"),
        ("customer", "Customer"),
    ], string="Owner Role", default="consultant")


class RiskRegisterItem(models.Model):
    """Risk register for tracking implementation risks."""
    _name = "ipai.risk.register.item"
    _description = "IPAI Risk Register Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, create_date desc"

    name = fields.Char(string="Risk Title", required=True, tracking=True)

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        tracking=True,
    )

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
    )

    description = fields.Text(string="Risk Description", tracking=True)

    risk_category = fields.Selection([
        ("scope", "Scope"),
        ("schedule", "Schedule"),
        ("resource", "Resource"),
        ("technical", "Technical"),
        ("budget", "Budget"),
        ("change", "Change Management"),
        ("integration", "Integration"),
        ("data", "Data Quality"),
    ], string="Category", required=True, tracking=True)

    probability = fields.Selection([
        ("1", "Very Low (1)"),
        ("2", "Low (2)"),
        ("3", "Medium (3)"),
        ("4", "High (4)"),
        ("5", "Very High (5)"),
    ], string="Probability", required=True, default="3", tracking=True)

    impact = fields.Selection([
        ("1", "Very Low (1)"),
        ("2", "Low (2)"),
        ("3", "Medium (3)"),
        ("4", "High (4)"),
        ("5", "Very High (5)"),
    ], string="Impact", required=True, default="3", tracking=True)

    priority = fields.Integer(
        string="Risk Score",
        compute="_compute_priority",
        store=True,
    )

    state = fields.Selection([
        ("identified", "Identified"),
        ("analyzing", "Analyzing"),
        ("mitigating", "Mitigating"),
        ("monitoring", "Monitoring"),
        ("closed", "Closed"),
    ], string="Status", default="identified", tracking=True)

    mitigation_plan = fields.Text(string="Mitigation Plan")
    contingency_plan = fields.Text(string="Contingency Plan")

    owner_id = fields.Many2one(
        "res.users",
        string="Risk Owner",
        default=lambda self: self.env.user,
        tracking=True,
    )

    identified_date = fields.Date(
        string="Identified Date",
        default=fields.Date.today,
    )

    review_date = fields.Date(string="Next Review Date")

    @api.depends("probability", "impact")
    def _compute_priority(self):
        for risk in self:
            prob = int(risk.probability or "1")
            imp = int(risk.impact or "1")
            risk.priority = prob * imp

    def action_analyze(self):
        self.write({"state": "analyzing"})

    def action_mitigate(self):
        self.write({"state": "mitigating"})

    def action_monitor(self):
        self.write({"state": "monitoring"})

    def action_close(self):
        self.write({"state": "closed"})
