from odoo import api, fields, models


class IpaiWorkload(models.Model):
    _name = "ipai.workload"
    _description = "IPAI Workload"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    key = fields.Char(
        required=True,
        tracking=True,
        help="Unique machine-readable key (e.g. odoo-erp, databricks-lakehouse)",
    )
    workload_type = fields.Selection(
        [
            ("odoo", "Odoo ERP"),
            ("web", "Web Application"),
            ("data_intelligence", "Data Intelligence"),
            ("automation", "Automation"),
            ("agent", "Agent / Copilot"),
            ("infrastructure", "Infrastructure"),
        ],
        required=True,
        tracking=True,
    )
    owner_user_id = fields.Many2one("res.users", string="Owner", tracking=True)
    owner_team = fields.Char(tracking=True)
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("registered", "Registered"),
            ("active", "Active"),
            ("degraded", "Degraded"),
            ("retired", "Retired"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    topology_kind = fields.Selection(
        [
            ("single", "Single Environment"),
            ("multi_env", "Multi-Environment"),
            ("distributed", "Distributed"),
        ],
        default="single",
    )
    source_repo = fields.Char(help="GitHub repository slug")
    source_system = fields.Char(help="External system identifier")
    description = fields.Text()
    active = fields.Boolean(default=True)

    environment_ids = fields.One2many(
        "ipai.workload.environment", "workload_id", string="Environments"
    )
    component_ids = fields.One2many(
        "ipai.workload.component", "workload_id", string="Components"
    )
    release_ids = fields.One2many(
        "ipai.workload.release", "workload_id", string="Releases"
    )
    validation_run_ids = fields.One2many(
        "ipai.workload.validation.run", "workload_id", string="Validation Runs"
    )
    policy_check_ids = fields.One2many(
        "ipai.workload.policy.check", "workload_id", string="Policy Checks"
    )
    cost_snapshot_ids = fields.One2many(
        "ipai.workload.cost.snapshot", "workload_id", string="Cost Snapshots"
    )

    environment_count = fields.Integer(
        compute="_compute_counts", string="Env Count"
    )
    release_count = fields.Integer(
        compute="_compute_counts", string="Release Count"
    )
    validation_count = fields.Integer(
        compute="_compute_counts", string="Validation Count"
    )

    _sql_constraints = [
        ("key_uniq", "unique(key)", "Workload key must be unique!"),
    ]

    @api.depends(
        "environment_ids", "release_ids", "validation_run_ids"
    )
    def _compute_counts(self):
        for rec in self:
            rec.environment_count = len(rec.environment_ids)
            rec.release_count = len(rec.release_ids)
            rec.validation_count = len(rec.validation_run_ids)

    def action_register(self):
        self.ensure_one()
        self.status = "registered"

    def action_activate(self):
        self.ensure_one()
        self.status = "active"

    def action_retire(self):
        self.ensure_one()
        self.status = "retired"
