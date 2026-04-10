from odoo import api, fields, models


class KnowledgeSource(models.Model):
    _name = "ipai.knowledge.source"
    _description = "Knowledge Source"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name asc"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        required=True, index=True,
        help="Slug used in Azure AI Search index selection",
    )
    description = fields.Text()
    source_type = fields.Selection(
        [
            ("policy", "Policy Document"),
            ("procedure", "Procedure"),
            ("checklist", "Checklist"),
            ("regulatory", "Regulatory Guidance"),
            ("faq", "FAQ"),
            ("other", "Other"),
        ],
        default="policy",
        required=True,
    )

    # Azure AI Search binding
    azure_index_name = fields.Char(
        string="Azure Index Name", required=True,
        help="The Azure AI Search index name for this source",
    )
    azure_semantic_config = fields.Char(
        string="Semantic Config",
        default="default",
        help="Azure AI Search semantic configuration name",
    )

    # Index state
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("retired", "Retired"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    last_indexed_at = fields.Datetime(readonly=True)
    doc_count_estimate = fields.Integer(
        string="Document Count",
        readonly=True,
    )
    index_health = fields.Selection(
        [
            ("unknown", "Unknown"),
            ("healthy", "Healthy"),
            ("degraded", "Degraded"),
            ("error", "Error"),
        ],
        default="unknown",
        readonly=True,
    )

    # Confidence policy
    confidence_threshold = fields.Float(
        default=0.70,
        help="Minimum score to return an answer (0.0-1.0)",
    )
    abstain_below_threshold = fields.Boolean(
        default=True,
        help="Return 'I don't know' when below threshold",
    )
    max_results = fields.Integer(
        default=5,
        help="Max chunks returned per query",
    )

    # Consumer tag
    consumer_tag = fields.Char(
        help="Consumer filter tag, e.g. finance_close, taxpulse, pulser",
    )

    # Owner
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company,
    )

    # Relations
    query_log_ids = fields.One2many(
        "ipai.knowledge.query.log", "source_id",
    )
    query_count = fields.Integer(compute="_compute_query_count")

    @api.depends("query_log_ids")
    def _compute_query_count(self):
        for rec in self:
            rec.query_count = len(rec.query_log_ids)

    def action_activate(self):
        self.write({"state": "active"})

    def action_pause(self):
        self.write({"state": "paused"})

    def action_retire(self):
        self.write({"state": "retired"})

    def action_check_index_health(self):
        bridge = self.env["ipai.knowledge.bridge"]
        for source in self:
            bridge._check_index_health(source)

    def action_view_query_logs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Query Logs",
            "res_model": "ipai.knowledge.query.log",
            "view_mode": "tree,form",
            "domain": [("source_id", "=", self.id)],
        }

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "Source code must be unique.",
        ),
    ]
