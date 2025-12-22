from odoo import fields, models


class IpaiStcWorklistType(models.Model):
    _name = "ipai.stc.worklist_type"
    _description = "STC Worklist Type (SAP Business Content)"
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    description = fields.Text()

    _sql_constraints = [
        (
            "stc_worklist_code_unique",
            "unique(code)",
            "Worklist type code must be unique.",
        ),
    ]


class IpaiStcCheck(models.Model):
    _name = "ipai.stc.check"
    _description = "STC Compliance Check"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    workstream_id = fields.Many2one(
        "ipai.workstream", required=True, ondelete="cascade", index=True
    )
    worklist_type_id = fields.Many2one("ipai.stc.worklist_type", ondelete="set null")
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    description = fields.Text()
    category = fields.Char(help="Check category: DATA_QUALITY, COMPLETENESS, etc.")
    sequence = fields.Integer(default=10)
    severity = fields.Selection(
        [("low", "Low"), ("med", "Medium"), ("high", "High"), ("critical", "Critical")],
        default="med",
    )
    is_active = fields.Boolean(default=True)
    auto_run = fields.Boolean(default=True, help="Run automatically in scenarios")
    sap_reference = fields.Char(help="SAP STC check reference")
    rule_json = fields.Text(help="Rule definition as JSON")

    _sql_constraints = [
        ("stc_check_code_unique", "unique(code)", "Check code must be unique."),
    ]


class IpaiStcScenario(models.Model):
    _name = "ipai.stc.scenario"
    _description = "STC Scenario (Bundle of Checks)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    workstream_id = fields.Many2one(
        "ipai.workstream", required=True, ondelete="cascade", index=True
    )
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    frequency = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
            ("on_demand", "On Demand"),
        ],
        default="monthly",
    )
    run_day_offset = fields.Integer(default=0, help="Day offset for scheduled run")
    sequence = fields.Integer(default=10)
    check_ids = fields.Many2many("ipai.stc.check", string="Checks")
    bir_forms = fields.Char(help="Comma-separated BIR form codes")
    notes = fields.Text()
    sap_reference = fields.Char(help="SAP STC scenario reference")

    _sql_constraints = [
        ("stc_scenario_code_unique", "unique(code)", "Scenario code must be unique."),
    ]
