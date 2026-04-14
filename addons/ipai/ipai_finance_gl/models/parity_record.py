# © 2026 InsightPulseAI — License: LGPL-3
"""
ipai.finance.gl.parity
-----------------------
D365 Finance General Ledger parity record.

Each record maps one D365 GL concept to its Odoo CE/OCA/ipai_* equivalent and
tracks whether that equivalent is fully covered, partially covered, a gap, or
explicitly out of scope.

Wave-01 D365 GL scope (Epic #523, 7 Tasks):
  chart-of-accounts | fiscal-calendar | financial-dimensions
  accounting-structure | financial-journal | periodic-process | gl-scope-definition

This model does NOT override any account.* behaviour. It is a pure overlay —
query / reporting / documentation surface only.
"""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# Status → Kanban color index mapping (Odoo color convention)
_STATUS_COLOR = {
    "covered": 10,       # green
    "partial": 2,        # yellow / amber
    "gap": 1,            # red
    "out_of_scope": 4,   # grey
}


class FinanceGlParityRecord(models.Model):
    """D365 Finance GL concept ↔ Odoo equivalent parity record."""

    _name = "ipai.finance.gl.parity"
    _description = "D365 Finance GL Parity Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "category_id, d365_concept"

    # -------------------------------------------------------------------------
    # Computed name (display only — not stored to avoid stale data)
    # -------------------------------------------------------------------------

    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
        help="Auto-computed as '[d365_module] d365_concept', e.g. '[GL] Main account'.",
    )

    # -------------------------------------------------------------------------
    # D365 side
    # -------------------------------------------------------------------------

    d365_concept = fields.Char(
        string="D365 Concept",
        required=True,
        tracking=True,
        help="Exact D365 Finance concept name, e.g. 'Main account', 'Fiscal calendar'.",
    )
    d365_module = fields.Char(
        string="D365 Module",
        tracking=True,
        help="D365 module abbreviation, e.g. 'GL', 'AP', 'AR', 'FA'.",
    )
    d365_doc_url = fields.Char(
        string="D365 Docs URL",
        help=(
            "Link to the Microsoft Learn / dynamics-365-unified-operations-public "
            "documentation page for this concept."
        ),
    )

    # -------------------------------------------------------------------------
    # Taxonomy
    # -------------------------------------------------------------------------

    category_id = fields.Many2one(
        comodel_name="ipai.finance.gl.parity.category",
        string="Category",
        required=True,
        ondelete="restrict",
        tracking=True,
        help="Functional grouping, e.g. 'Chart of Accounts', 'Fiscal Calendar'.",
    )

    # -------------------------------------------------------------------------
    # Odoo / OCA side
    # -------------------------------------------------------------------------

    odoo_module = fields.Char(
        string="Odoo Module",
        tracking=True,
        help="CE or OCA module that covers this concept, e.g. 'account', 'OCA/mis-builder'.",
    )
    odoo_model = fields.Char(
        string="Odoo Model",
        tracking=True,
        help="Primary Odoo model, e.g. 'account.account', 'account.fiscal.position'.",
    )
    odoo_view_ref = fields.Char(
        string="Odoo View XML ID",
        help=(
            "Fully-qualified XML ID used to open the Odoo model view directly, "
            "e.g. 'account.view_account_form'. Used by action_open_odoo_model()."
        ),
    )

    # -------------------------------------------------------------------------
    # Parity status
    # -------------------------------------------------------------------------

    status = fields.Selection(
        selection=[
            ("covered", "Covered"),
            ("partial", "Partial"),
            ("gap", "Gap"),
            ("out_of_scope", "Out of Scope"),
        ],
        string="Status",
        required=True,
        default="gap",
        tracking=True,
        help=(
            "covered — Odoo CE/OCA fully satisfies the D365 concept.\n"
            "partial — Partial coverage; supplementary ipai_* work may be needed.\n"
            "gap — No Odoo equivalent exists yet.\n"
            "out_of_scope — Explicitly excluded from parity scope."
        ),
    )
    status_color = fields.Integer(
        string="Status Color",
        compute="_compute_status_color",
        help="Kanban color index derived from status (not stored — display only).",
    )

    # -------------------------------------------------------------------------
    # Notes and implementation metadata
    # -------------------------------------------------------------------------

    notes = fields.Html(
        string="Implementation Notes",
        help="Rich-text notes on how the parity is achieved, gaps, or workarounds.",
    )
    ipai_module_id = fields.Char(
        string="IPAI Module",
        tracking=True,
        help=(
            "Name of the thin ipai_* adapter module if one is needed or already exists, "
            "e.g. 'ipai_finance_gl_dimensions'."
        ),
    )

    # -------------------------------------------------------------------------
    # Wave / project tracking
    # -------------------------------------------------------------------------

    wave = fields.Char(
        string="Wave",
        default="Wave-01",
        tracking=True,
        help="Delivery wave this record belongs to, e.g. 'Wave-01'.",
    )
    ado_task_id = fields.Char(
        string="ADO Task ID",
        help="Azure DevOps Task ID under Epic #523, e.g. '#612'.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    # -------------------------------------------------------------------------
    # SQL constraints
    # -------------------------------------------------------------------------

    _sql_constraints = [
        (
            "d365_concept_wave_uniq",
            "unique(d365_concept, wave)",
            "A parity record for this D365 concept already exists in the same wave.",
        ),
    ]

    # -------------------------------------------------------------------------
    # Compute methods
    # -------------------------------------------------------------------------

    @api.depends("d365_module", "d365_concept")
    def _compute_name(self):
        """Derive display name as '[MODULE] Concept' or just 'Concept' when no module."""
        for rec in self:
            if rec.d365_module:
                rec.name = f"[{rec.d365_module}] {rec.d365_concept or ''}"
            else:
                rec.name = rec.d365_concept or ""

    @api.depends("status")
    def _compute_status_color(self):
        """Map parity status to Odoo kanban color index."""
        for rec in self:
            rec.status_color = _STATUS_COLOR.get(rec.status, 0)

    # -------------------------------------------------------------------------
    # Constraint methods
    # -------------------------------------------------------------------------

    @api.constrains("status", "odoo_module", "odoo_model")
    def _check_covered_requires_odoo_fields(self):
        """Enforce that 'covered' status records declare their Odoo module and model."""
        for rec in self:
            if rec.status == "covered" and not (rec.odoo_module and rec.odoo_model):
                raise ValidationError(
                    _(
                        "Parity record '%s' has status 'Covered' but is missing "
                        "Odoo Module and/or Odoo Model. Both fields are required "
                        "when status is Covered.",
                        rec.name or rec.d365_concept,
                    )
                )

    # -------------------------------------------------------------------------
    # Action methods
    # -------------------------------------------------------------------------

    def action_open_odoo_model(self):
        """Open the related Odoo model view identified by odoo_view_ref.

        Returns a window action dict when odoo_view_ref is set, or raises
        a UserError with guidance when the field is empty.

        Usage: bound to a button on the parity record form view.
        """
        self.ensure_one()
        if not self.odoo_view_ref:
            raise ValidationError(
                _(
                    "No Odoo View XML ID is configured for '%s'. "
                    "Set the 'Odoo View XML ID' field to enable direct navigation.",
                    self.name or self.d365_concept,
                )
            )
        view = self.env.ref(self.odoo_view_ref, raise_if_not_found=False)
        if not view:
            raise ValidationError(
                _(
                    "The XML ID '%s' could not be resolved. "
                    "Verify the module containing this view is installed.",
                    self.odoo_view_ref,
                )
            )
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": view.model,
            "view_mode": "list,form",
            "views": [(view.id, view.type)],
            "target": "current",
        }
