from odoo import api, fields, models


class IpaiWorkspace(models.Model):
    """IPAI Workspace - foundational control plane entity.

    Represents a logical workspace grouping for IPAI features.
    This is the Phase 1 vertical slice marker proving the delivery pipeline.
    """

    _name = "ipai.workspace"
    _description = "IPAI Workspace"
    _order = "sequence, name"

    name = fields.Char(required=True, index=True)
    code = fields.Char(index=True, help="Short code for workspace identification")
    description = fields.Text()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Members",
        help="Users who have access to this workspace",
    )

    _sql_constraints = [
        ("code_uniq", "unique(code, company_id)", "Workspace code must be unique per company."),
    ]

    @api.model
    def _get_default_workspace(self):
        """Return or create the default workspace for current company."""
        workspace = self.search([("company_id", "=", self.env.company.id)], limit=1)
        if not workspace:
            workspace = self.create({
                "name": "Default Workspace",
                "code": "DEFAULT",
                "company_id": self.env.company.id,
            })
        return workspace
