from odoo import models, fields


class CrmStage(models.Model):
    """
    Enhanced CRM Stage with rule configuration.

    Adds the ability to define required fields per stage,
    enabling Salesforce-like validation on stage transitions.
    """

    _inherit = "crm.stage"

    ipai_required_field_ids = fields.Many2many(
        "ir.model.fields",
        "crm_stage_required_fields_rel",
        "stage_id",
        "field_id",
        string="Required Fields",
        domain="[('model', '=', 'crm.lead'), ('store', '=', True), ('ttype', 'not in', ['one2many', 'many2many', 'binary'])]",
        help="Fields that must be filled before a lead/opportunity can enter this stage.",
    )

    ipai_enforce_rules = fields.Boolean(
        string="Enforce Stage Rules",
        default=False,
        help="If checked, leads cannot be moved to this stage until all required fields are filled.",
    )

    ipai_stage_color = fields.Char(
        string="Stage Color",
        default="#6c757d",
        help="Color code for the stage header in kanban view.",
    )

    ipai_stage_icon = fields.Char(
        string="Stage Icon",
        help="Font Awesome icon class (e.g., 'fa-handshake-o') for the stage.",
    )

    ipai_sla_days = fields.Integer(
        string="SLA Days",
        help="Expected maximum days an opportunity should stay in this stage.",
    )

    ipai_automation_notes = fields.Text(
        string="Automation Notes",
        help="Notes about automated actions triggered when entering this stage.",
    )
